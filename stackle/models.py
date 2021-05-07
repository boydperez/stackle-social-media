from datetime import datetime
from stackle import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return Account.query.get(user_id)

# Associative models

post_likes = db.Table('post_likes',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('account.id'))
)

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('account.id')),
    db.Column('following_id', db.Integer, db.ForeignKey('account.id'))
)

blocked_users = db.Table('blocked_users',
    db.Column('user_id', db.Integer, db.ForeignKey('account.id')),
    db.Column('blocked_id', db.Integer, db.ForeignKey('account.id'))
)

# Models

class Account(db.Model, UserMixin):
    """
    Account model. 
    """
    id = db.Column(db.Integer, primary_key=True)
    account_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(15), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    profile_picture = db.Column(db.String(50), nullable=False, default='default.jpg')
    account_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, nullable=True)
    activity_status = db.Column(db.String(6), nullable=False, default='active')

    posts = db.relationship('Post', backref='user', lazy=True)
    likes = db.relationship('Post', secondary=post_likes, backref=db.backref('liked_by', lazy=True))

    following = db.relationship(
        'Account', secondary=followers, 
        primaryjoin = (followers.c.follower_id == id),
        secondaryjoin = (followers.c.following_id == id), 
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    blocked = db.relationship(
        'Account', secondary=blocked_users,
        primaryjoin = (blocked_users.c.user_id == id),
        secondaryjoin = (blocked_users.c.blocked_id == id), 
        backref=db.backref('blocked_by', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return f"<Account '{self.username}'>"

    def is_liked(self, post):
        post = Post.query.filter_by(id=post.id).first()
        if self in post.liked_by:
            return True
        else:
            return False

    def is_following(self, user):
        if self in user.followers:
            return True
        else:
            return False


class Post(db.Model):
    """
    Post model. 
    """
    id = db.Column(db.Integer, primary_key=True)
    text_content = db.Column(db.String(250), nullable=False)
    image_content = db.Column(db.String(50), nullable=True)
    posted_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    likes = db.Column(db.Integer, nullable=False, default=0)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)

    def __repr__(self):
        return f"<Post '{self.id}'>"


class Comment(db.Model):
    """
    Comment model.
    """
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(250), nullable=False)
    likes = db.Column(db.Integer, nullable=False, default=0)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    posts = db.relationship('Post', backref='comments', lazy=True)


class CommentThread(db.Model):
    """
    Comment thread model.
    """
    __tablename__ = 'comment_thread'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(250), nullable=False)
    likes = db.Column(db.Integer, nullable=False, default=0)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=False)
    comments = db.relationship('Comment', backref='thread', lazy=True)
