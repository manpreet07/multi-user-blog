

from google.appengine.ext import ndb


class Blog(ndb.Model):

    title = ndb.StringProperty(required=True)
    blog = ndb.TextProperty(required=True)
    # creator = ndb.StringProperty()
    dateTime = ndb.DateTimeProperty(auto_now_add=True)

    @classmethod
    def query_blogs(cls):
        return cls.query().order(-cls.dateTime)