

from google.appengine.ext import ndb


class Blog(ndb.Model):

    title = ndb.StringProperty(required=True)
    blog = ndb.StringProperty(required=True)
    # creator = ndb.StringProperty()
    date = ndb.DateProperty(auto_now_add=True)

    @classmethod
    def query_blogs(cls):
        return cls.query().order(-cls.date)