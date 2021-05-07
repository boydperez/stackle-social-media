from flask import render_template, redirect, url_for, request, flash, request, jsonify, abort
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from os.path import join
from flask_wtf import FlaskForm
import time

from stackle.forms import SignupForm, LoginForm, UpdateForm, PostForm
from stackle.models import Account, Post, post_likes, Comment
from stackle import app, login_manager, db, bcrypt 

from flask_cors import CORS
CORS(app)

@login_manager.user_loader
def load_user(user_id):
    return Account.query.get(user_id)


@app.route('/')
def home():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    posts = Post.query.all()
    # posts = Post.query.paginate(per_page=2)
    return render_template('home.html', posts=posts, Account=Account, form=FlaskForm())


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    # Check if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    # Instantiate signup form
    form = SignupForm()
    if form.validate_on_submit():

        # Get the data submitted by the user
        name = form.name.data
        username = form.username.data
        email = form.email.data
        password = form.password.data
        # Hash password using flask-bcrypt
        hashed_passwd = bcrypt.generate_password_hash(password).decode('utf-8')

        # Create an account record
        user = Account(account_name=name.strip(), username=username.strip(), email=email.strip(), password=hashed_passwd)

        # Add and commit to db
        db.session.add(user)
        db.session.commit()

        flash('Account created', 'success')
        return redirect(url_for('home'))
    return render_template('signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Check if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = Account.query.filter_by(username=form.username.data.strip()).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            # TODO: Add remember me functionality
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))

        flash('Username or password is incorrect')
    return render_template('login.html', form=form)


@app.route('/<string:user_account>')
def user_profile(user_account):
    user = Account.query.filter_by(username=user_account).first()
    if user:
        data = {
            'title': user.account_name,
            # 'posts': Post.query.filter_by(account_id=user).all()
            'posts': user.posts 
        }

        has_followers, has_followings = True, True

        # Check if the user has any followings
        try:
            _ = user.following[0]
        except IndexError:
            has_followings = False

        # Check if the user has any followers
        try:
            _ = user.followers[0]
        except IndexError:
            has_followers = False

        # Count follower
        followers_count = 0
        for _ in user.followers:
            followers_count += 1

        # Count following
        followings_count = 0
        for _ in user.following:
            followings_count += 1

        return render_template('user_profile.html', posts=user.posts, user=user, followers=user.followers, 
                                followings=user.following, has_followings=has_followings, has_followers=has_followers, 
                                followers_count=followers_count, followings_count=followings_count)
        
    abort(404)

@app.route('/<string:user_account>/followers')
def followers(user_account):
    user = Account.query.filter_by(username=user_account).first()
    if user:
        has_followers, has_followings = True, True
        try:
            _ = user.following[0]
        except IndexError:
            has_followings = False

        try:
            _ = user.followers[0]
        except IndexError:
            has_followers = False

        # Count follower
        followers_count = 0
        for _ in user.followers:
            followers_count += 1

        # Count following
        followings_count = 0
        for _ in user.following:
            followings_count += 1


        return render_template('followers.html', followers=user.followers, followings=user.following, 
                                has_followings=has_followings, has_followers=has_followers, 
                                followers_count=followers_count, followings_count=followings_count, user=user)
                                 
        
    abort(404)


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/account/settings/user', methods=['GET', 'POST'])
@login_required
def account():

    form = UpdateForm()

    # Update profile picture
    if request.method == 'POST':
        # Handle image file
        try:
            print(f"\n\n{request.files['image']}\n\n")
            file = request.files['image']
            print(f"\n\n\nfile.filename:\n{file.filename}\n\n\n")

            if file.filename == '':
                raise Exception()
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(join(app.config['UPLOAD_FOLDER'], 'profile_pictures', filename))
                print('profile picture successfully uploaded')
                current_user.profile_picture = file.filename
        except:
            print(f"[ERR] File error")

        # Update other info
        if form.validate_on_submit():
            print("\n\n\nUpdating other info\n\n\n")
            current_user.account_name = form.name.data
            current_user.username = form.username.data
            current_user.email = form.email.data

        # Upate activity status
        status = request.form.get('activityStatus')
        if status:
            current_user.activity_status = status

        # Commit all changes to db 
        db.session.commit()

        flash('Account details updated')
        return redirect(request.url)

    image_filename = f"images/profile_pictures/{current_user.profile_picture}"
    image_file = url_for('static', filename=image_filename)
    return render_template('account.html', image_file=image_file, form=form)


@app.route('/account/settings/blocked-users', methods=['GET', 'POST'])
@login_required
def blocked_users():
    return render_template('blocked_users.html')


@app.route('/logout')
def logout():
    logout_user()
    flash('Logged out')
    return redirect(url_for('login'))



@app.route('/new-post', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        # Get the file object
        file_obj = form.image_file.data
        filename = secure_filename(file_obj.filename)
        file_obj.save(join(app.config['UPLOAD_FOLDER'], 'posts', filename))

        # Get the post content
        content = form.post_content.data

        post = Post(text_content=content, image_content=filename, user=current_user)
        db.session.add(post)
        db.session.commit()

        flash('Post has been uploaded', 'success')
        return redirect(url_for('home'))
        
    return render_template('new_post.html', form=form)


@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def post(post_id):
    post = Post.query.get_or_404(int(post_id))

    # Check if post actually exists
    if request.method == 'POST':
        content = request.form.get('postComment')
        comment = Comment(content=content, account_id=current_user, post_id=post)
        db.session.add(comment)
        db.session.commit()
        # return redirect(url_for('post', post_id=post.id))
        return 'done'

    return render_template('post.html', post=post, Account=Account, form=FlaskForm())


@app.route('/post/delete-post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(int(post_id))

    if current_user.username != post.user.username:
        return redirect(url_for('home'))

    if request.method == 'POST': 
        if request.form.get('action') == 'Delete': 
            print(f"\n\n{request.form.get('action')}\n\n")
            db.session.delete(post)
            db.session.commit()
            flash("Post deleted", 'success')
            return redirect(url_for('home'))

        if request.form.get('action') == 'Cancel':
            return redirect(url_for('home'))

    return render_template('delete_post.html', post=post, form=FlaskForm())


@app.route('/messenger')
def messenger():
    return render_template('messenger.html')




# Error handler
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# APIs
@app.route('/api/username-availability')
def username_availability():
    # TODO: CORS
     
    username = request.args.get('username')
    user = Account.query.filter_by(username=username).first()
    if user or username == 'account': 
        return 'true'
    else:
        return 'false'


@app.route('/api/get-post-likes/<int:post_id>')
def get_post_likes(post_id):
    post = Post.query.filter_by(id=post_id).first()
    return jsonify({'likes': post.likes})


@app.route('/api/like-post/<int:post_id>', methods=['GET','POST'])
def like_post(post_id):
    post = Post.query.filter_by(id=post_id).first()

    if post:
        # Console debug
        print('---------- in post -----------------')
        print(f"\npost.liked_by: {post.liked_by}\n")
        print(f"\ncurrent_user: {current_user}\n")
        print(f"\ncurrent_user.id: {current_user.id}\n")
        print(f"\n\n\n{[user.id for user in post.liked_by]}\n\n\n")

        if current_user in post.liked_by: 
            # Remove the entry from the association table
            post.liked_by.remove(current_user)
            post.likes -= 1;

            # Commit the like changes to the database
            db.session.commit()
            return jsonify({'message': 'post unliked'})
        else:
            #TODO: Continue
            post.liked_by.append(current_user)
            post.likes += 1;

            # Commit the like changes to the database
            db.session.commit()
            return jsonify({'message': 'post liked'})


    return jsonify({'message': 'error'})


@app.route('/api/get-users/<user_regex>') 
def get_users(user_regex):
    user_objects = Account.query.filter(Account.username.like(user_regex + '%')).all()
    users = [user_obj.username for user_obj in user_objects]
    # Get the profile picture extensions
    profile = [user_obj.profile_picture for user_obj in user_objects]

    return jsonify({'users': users, 'profile': profile})


@app.route('/api/follow/<int:user_id>', methods=['GET', 'POST'])
def follow_user(user_id):
    user = Account.query.filter_by(id=user_id).first()
    
    if user and user.id != current_user.id:
        if not current_user.is_following(user):
            current_user.following.append(user)
            db.session.commit()
            return jsonify({'message': 'followed'})
        else:
            current_user.following.remove(user)
            db.session.commit()
            return jsonify({'message': 'unfollowed'})

    return jsonify({'message': 'error'})


@app.route('/api/block/<int:user_id>', methods=['GET', 'POST'])
def block(user_id):
    user = Account.query.get(user_id)
    
    if user in current_user.blocked:
        current_user.blocked.remove(user)
        db.session.commit()
        return jsonify({'message': 'unblocked'})

    current_user.blocked.append(user)
    db.session.commit()
    return jsonify({'message': 'blocked'})
    