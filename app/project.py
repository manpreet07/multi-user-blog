import os

import webapp2
import jinja2
from models import Blog

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


class MainPage(Handler):
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

    newPost = Blog(title = _title, blog = _blog)
    newPost.put()

    self.render('newpost.html', title=_title, blog=_blog)

app = webapp2.WSGIApplication(
  [('/', MainPage), ('/newpost', AddNewPostPage)], debug=True)
