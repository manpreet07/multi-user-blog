import hmac
import os

import jinja2
import webapp2
from google.appengine.ext import ndb
import random
import string
import hashlib
from models import Blog, User

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)

def make_salt():
  return ''.join(random.choice(string.letters) for x in xrange(5))

def hash_str(s):
  return hmac.new(make_salt(), s).hexdigest()

def make_secure_val(s):
  return "%s|%s" % (s, hash_str(s))

def check_secure_val(h):
  val = h.split('|')[0]
  if h == make_secure_val(val):
    return val

def make_pw_hash(name, pw, salt=None):
  if not salt:
    salt = make_salt()
  h = hashlib.sha256(name + pw + salt).hexdigest()
  return '%s,%s' % (h, salt)


def valid_pw(name, pw, h):
  _salt = h.split(",")[1]
  if h == make_pw_hash(name, pw, _salt):
    return True
  else:
    return False


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
    self.response.headers['Content-Type'] = 'text/html'
    visits = 0
    visit_cookie_str = self.request.cookies.get('visits')

    if visit_cookie_str:
      cookie_val = check_secure_val(visit_cookie_str)
      if cookie_val:
        visits = int(cookie_val)
    visits += 1

    new_cookie_val = make_secure_val(str(visits))

    # self.response.headers.add_headers('Set_Cookie', 'visits=%s' % new_cookie_val)
    self.response.headers['Set-Cookie'] = 'visits=%s' % new_cookie_val

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
      self.redirect('/blog/%s' % str(_newPostID))

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

    self.render("permalink.html", blog=post)

class SignUpPage(Handler):

  def get(self):
    self.render('signup.html')

  def post(self):
    _username = self.request.get("username")
    _pwd = self.request.get("pwd")
    _verify_pwd = self.request.get("verify_pwd")
    _email = self.request.get("email")

    username_error = "Please enter Username"
    pw_error = "Please enter password"
    verify_pw_error = "Please verify password"
    email_error = "Please enter email"

    if _username and _pwd and _verify_pwd and _email:
      if _pwd == _verify_pwd:
        _hashpw = make_pw_hash(_username, _pwd)
        newUser = User(username = _username, password = _hashpw, email=_email)
        newUser.put()
        self.redirect('/')
      else:
        self.render('signup.html', verify_pw_error=verify_pw_error)

    if _username == "":
      self.render('signup.html', username_error=username_error)
    if _pwd == "":
      self.render('signup.html', pw_error=pw_error)
    if _verify_pwd == "":
      self.render('signup.html', verify_pw_error=verify_pw_error)
    if _email == "":
      self.render('signup.html', email_error=email_error)

app = webapp2.WSGIApplication(
  [('/', BlogsPage),('/newpost', AddNewPostPage), ('/blog/signup', SignUpPage), ('/blog/([0-9]+)', PostPage)], debug=True)
