

from google.appengine.ext import ndb
import project


class User(ndb.Model):
    name = ndb.StringProperty(required=True)
    pw_hash = ndb.StringProperty(required=True)
    email = ndb.StringProperty()

    @classmethod
    def by_id(cls, uid):
        _entity = ndb.Key('User', str(uid))
        return _entity
        # return User.get_by_id(uid)

    @classmethod
    def by_name(cls, name):
        u = User.query().filter(User.name == name)
        return u

    @classmethod
    def register(cls, name, pw, email=None):
        pw_hash = project.make_pw_hash(name, pw)
        return User(name=name,
                    pw_hash=pw_hash,
                    email=email)

    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name).get()
        if u and project.valid_pw(name, pw, u.pw_hash):
            return u

    @classmethod
    def get_all_posts(cls):
        u = User.query()
        return u


class Blog(ndb.Model):

    title = ndb.StringProperty(required=True)
    blog = ndb.TextProperty(required=True)
    dateTime = ndb.DateTimeProperty(auto_now_add=True)
    user = ndb.KeyProperty(kind='User')

    @classmethod
    def query_blogs(cls):
        return cls.query().order(-cls.dateTime)

