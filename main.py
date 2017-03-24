import hug
from os import environ

from hug.types import shorter_than

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from uuid import uuid4

from datetime import datetime, timedelta
import bcrypt
from falcon import HTTP_200, HTTP_201, HTTP_401, HTTP_400


SHORT_DESCR_LENGTH = 255
LONG_DESCR_LENGTH = 512
API_KEY_LIFESPAN = 30

DEFAULT_DB_PATH = 'sqlite:///linkfloyd.db'
db_path = environ.get('LF_DB_PATH', DEFAULT_DB_PATH)

engine = create_engine(db_path, echo=True)
Model = declarative_base()
Session = sessionmaker(bind=engine)


class User(Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True)
    password = Column(String(255))
    api_keys = relationship("ApiKey", back_populates="owner")

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User: %s>' % self.username

    @classmethod
    def get_by_api_key(cls):
        session = Session()
        return session.query(cls).filter(password)


class ApiKey(Model):
    __tablename__ = 'api_keys'
    key = Column(String(32), primary_key=True)
    owner_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship("User", back_populates="api_keys")
    created_on = Column('created_on', DateTime)

    def __init__(self, owner_id, key=None):
        self.owner_id = owner_id
        self.key = key or uuid4().hex
        self.created_on = self.created_on or datetime.now()

    @classmethod
    def verify(cls, key):
        """Verify if key is valid and not expired. Return owner of key if
        key is valid."""
        session = Session()
        api_key = session.query(cls).filter(cls.key.is_(key)).first()
        if not api_key:
            return None
        return api_key.owner

    def serialize(self):
        return {'key': self.key, 'created_on': self.created_on}


class Tag(Model):
    __tablename__ = 'tags'
    name = Column(String(60), primary_key=True)
    description = Column(String(255))

    def __init__(self, name, description=None):
        self.name = name
        self.description = description

    def __repr__(self):
        return '<Tag: %s>' % self.name

    def serialize(self):
        return {'name': self.name, 'description': self.description}


class Post(Model):
    __tablename__ = 'posts'
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
authentication = hug.authentication.api_key(ApiKey.verify)

@hug.post('/user/create/')
def create_user(username: hug.types.text, password: hug.types.text, response):
    print(password, type(password))
    session = Session()
    existing_user = session.query(User).filter(
        User.username.is_(username)).first()
    if existing_user:
        response.status = HTTP_400
        return {'success': False,
                'errors': ['User with this username already exists']}
    password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    session.add(User(username, password))
    session.commit()
    response.status = HTTP_201
    return {'success': True}


@hug.post('/user/authenticate/')
def create_api_key(username: hug.types.text, password: hug.types.text,
                   response):
    session = Session()
    user = session.query(User).filter(User.username.is_(username)).first()
    if not user:
        response.status = HTTP_404
        return
    password_is_correct = bcrypt.checkpw(password.encode('utf-8'),
                                         user.password)
    if not password_is_correct:
        response.status = 401
        return
    api_key = ApiKey(owner_id=user.id)
    session.add(api_key)
    session.status = HTTP_201
    return {'success': True, 'key': api_key.serialize()}


@hug.post('/post/create/', requires=authentication)
def create_post(user: hug.directives.user, url: hug.types.text,
                title: hug.types.shorter_than(LONG_DESCR_LENGTH)):
    post = Post(url, title)
    session = Session()
    session.add(post)
    session.commit()
    return {'success': True}


@hug.get('/post/all/')
def all_posts(tags=None):
    session = Session()
    posts = session.query(Post).all()
    return {'objects': [post.serialize() for post in posts]}
