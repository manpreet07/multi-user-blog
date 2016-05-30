import os

import webapp2
import jinja2
from models import Blog
from google.appengine.ext import ndb

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)


class Handler(webapp2.RequestHandler):
  def write(self, *a, **kw):
    self.response.out.write(*a, **kw)

  def render_str(self, template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

  def render(self, template, **kw):
    self.write(self.render_str(template, **kw))


class BlogsPage(Handler):
  BLOGS_PER_PAGE = 10

  def get(self):
    _blogs = Blog.query_blogs().fetch(self.BLOGS_PER_PAGE)
    self.render('blog.html', blogs=_blogs)

class AddNewPostPage(Handler):
  def get(self):
    self.render('newpost.html')

  def post(self):
    _title = self.request.get("title")
    _blog = self.request.get("blog")

    _title_error = "Please enter title"
    _post_error = "Please enter post"

    if _title and _blog:
      newPost = Blog(title = _title, blog = _blog)
      _newPost_key = newPost.put()
      _newPostID = _newPost_key.id()
      self.redirect('/newpost/%s' % str(_newPostID))

    if _title == "" and _blog == "":
      self.render('newpost.html', title_error=_title_error, post_error=_post_error)
    elif _title == "" or _blog == "":
      if _title == "":
        self.render('newpost.html', title_error=_title_error, title = _title, blog=_blog)
      if _blog == "":
        self.render('newpost.html', post_error=_post_error, title = _title, blog=_blog)


class PostPage(Handler):
  def get(self, post_id):
    blog_key = ndb.Key(Blog, int(post_id))
    post = blog_key.get()

    if not post:
      self.error(404)
      return

    self.render("permalink.html", post=post)

app = webapp2.WSGIApplication(
  [('/', BlogsPage), ('/newpost', AddNewPostPage), ('/newpost/([0-9]+)', PostPage)], debug=True)
