

from google.appengine.ext import ndb
import blog


class Comment(ndb.Model):
    comment = ndb.StringProperty()


class Blog(ndb.Model):
    title = ndb.StringProperty(indexed=False)
    blog = ndb.TextProperty(indexed=False)
    dateTime = ndb.DateTimeProperty(auto_now_add=True)
    comments = ndb.KeyProperty(Comment, repeated=True)

    @classmethod
    def by_id(cls, uid, parent):
        return Blog.get_by_id(uid, parent=parent)

    @classmethod
    def query_blogs(cls):
        return cls.query().order(-cls.dateTime)


class User(ndb.Model):
    name = ndb.StringProperty()
    pw_hash = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(indexed=False)
    blogs = ndb.KeyProperty(Blog,repeated=True)

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(int(uid))

    @classmethod
    def by_name(cls, name):
        u = User.query().filter(User.name == name)
        return u

    @classmethod
    def register(cls, name, pw, email=None):
        pw_hash = blog.make_pw_hash(name, pw)
        return User(name=name,
                    pw_hash=pw_hash,
                    email=email)

    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name).get()
        if u and blog.valid_pw(name, pw, u.pw_hash):
            return u

    @classmethod
    def get_all_posts(cls):
        u = User.query()
        return u




