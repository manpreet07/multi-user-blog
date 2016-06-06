

from google.appengine.ext import ndb
import project


class Blog(ndb.Model):

    title = ndb.StringProperty(required=True)
    blog = ndb.TextProperty(required=True)
    dateTime = ndb.DateTimeProperty(auto_now_add=True)

    @classmethod
    def query_blogs(cls):
        return cls.query().order(-cls.dateTime)


class User(ndb.Model):
    name = ndb.StringProperty(required=True)
    pw_hash = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
    blog = ndb.KeyProperty(kind="Blog", repeated=True)

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid)

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