import hug
from os import environ

from hug.types import shorter_than

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime

from datetime import datetime

SHORT_DESCR_LENGTH = 255
LONG_DESCR_LENGTH = 512

DEFAULT_DB_PATH = 'sqlite:///linkfloyd.db'
db_path = environ.get('LF_DB_PATH', DEFAULT_DB_PATH)

engine = create_engine(db_path, echo=True)
Model = declarative_base()
Session = sessionmaker(bind=engine)


class User(Model):

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(80), unique=True)
    password = Column(String(255))

    def __init__(self, email, password):
        self.email = email
        self.password = password

    def __repr__(self):
        return '<User: %s>' % self.email


class Tag(Model):
    __tablename__ = 'tag'

    id = Column(Integer, primary_key=True)
    name = Column(String(60))
    description = Column(String(255))


class Post(Model):

    __tablename__ = 'post'

    id = Column(Integer, primary_key=True)
    url = Column(String(255))
    title = Column(String(512))
    created_on = Column('created_on', DateTime, default=datetime.now)

    def __init__(self, url, title):
        self.url = url
        self.title = title

    def __repr__(self):
        return '<Link %r>' % self.url

    def serialize(self):
        return {'url': self.url,
                'title': self.title,
                'comment_count': 0,
                'created_on': self.created_on,
                'tags': ['müzik', 'resim', 'fotoğraf']}


Model.metadata.create_all(engine)


@hug.post('/post/create/')
def create_post(url:hug.types.text,
                title:hug.types.shorter_than(LONG_DESCR_LENGTH)):
    post = Post(url, title)
    session = Session()
    session.add(post)
    session.commit()
    return {'success': True}


@hug.get('/post/all/')
def all_posts(tags=None):
    """Returns all posts, posts can be filtered by tag parameter."""
    session = Session()
    posts = session.query(Post).all()
    return {'objects': [post.serialize() for post in posts]}
