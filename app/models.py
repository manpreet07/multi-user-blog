

from google.appengine.ext import ndb


class Blog(ndb.Model):

    title = ndb.StringProperty(required=True)
    blog = ndb.TextProperty(required=True)
    creator = ndb.ReferenceProperty(reference_class=User)
    dateTime = ndb.DateTimeProperty(auto_now_add=True)

    @classmethod
    def query_blogs(cls):
        return cls.query().order(-cls.dateTime)


class User(ndb.Model):

    username = ndb.StringProperty(required=True)
    password = ndb.TextProperty(required=True)
    email = ndb.EmailProperty(required=True)