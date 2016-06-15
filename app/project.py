import hmac
import os

import jinja2
import webapp2
from google.appengine.ext import ndb
import hashlib
from models import Blog, User


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)


def make_salt():
  return "dsfkadb425b42534132erqerdfdsfarqewr31421324"

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
  return '%s,%s' % (salt,h)


def valid_pw(name, pw, h):
  _salt = h.split(",")[0]
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

  def read_secure_cookie(self, name):
    cookie_val = self.request.cookies.get(name)
    return cookie_val and check_secure_val(cookie_val)

  def set_secure_cookie(self, name, val):
    cookie_val = make_secure_val(val)
    self.response.headers['Set-Cookie'] = '%s=%s' % (name, cookie_val)

  def login(self, user):
    self.set_secure_cookie('user_id', str(user))

  def logout(self):
    self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

  def initialize(self, *a, **kw):
    webapp2.RequestHandler.initialize(self, *a, **kw)
    uid = self.read_secure_cookie('user_id')
    self.user = uid and User.by_id(int(uid))


class AddNewPostPage(Handler):
  def get(self):
    self.render('newpost.html')

  def post(self):
    _title = self.request.get("title")
    _blog = self.request.get("blog")

    _title_error = "Please enter title"
    _post_error = "Please enter post"

    if self.user:
      if _title and _blog:
        print self.user
        newPost = Blog(title=_title, blog=_blog, user=self.user)
        _newPost_key = newPost.put()
        _newPostID = _newPost_key.id()
        self.redirect('/blog/%s' % str(_newPostID))

      if _title == "" and _blog == "":
        self.render('newpost.html', title_error=_title_error, post_error=_post_error)
      elif _title == "" or _blog == "":
        if _title == "":
          self.render('newpost.html', title_error=_title_error, title=_title, blog=_blog)
        if _blog == "":
          self.render('newpost.html', post_error=_post_error, title=_title, blog=_blog)

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
    _pwd = self.request.get("password")
    _verify_pwd = self.request.get("verify_password")
    _email = self.request.get("email")

    username_error = "Please enter Username"
    pw_error = "Please enter password"
    verify_pw_error = "Please verify password"
    email_error = "Please enter email"

    if _username and _pwd and _verify_pwd and _email:
      if _pwd == _verify_pwd:
        _newUser = User.register(_username, _pwd, _email)
        newUserKey = _newUser.put()
        newUser = newUserKey.id()
        self.login(newUser)
        self.render('blog.html', user=_newUser)
      else:
        self.render('signup.html', verify_pw_error=verify_pw_error)

    if _username == "" or _pwd == "" or _verify_pwd == "" or _email == "":
      self.render('signup.html', username_error=username_error, pw_error=pw_error, verify_pw_error=verify_pw_error,
                  email_error=email_error)


class LoginPage(Handler):
  def get(self):
    self.render('login.html')

  def post(self):
    _username = self.request.get("username")
    _pwd = self.request.get("password")

    username_error = "Please enter Username"
    pw_error = "Please enter password"
    error = "Invalid Username or password entered"

    if _username and _pwd:
      user = User.login(_username, _pwd)
      if (user):
        _user = user.key.id()
        self.login(_user)
        self.redirect('/')
    else:
      self.render('login.html', username_error=username_error, pw_error=pw_error)


class Logout(Handler):
  def get(self):
    self.logout()
    self.render('logout.html')

class BlogsPage(Handler):
  def get(self):
    if self.user:
      _blogs = Blog.query(Blog.user == self.user)
      self.render('blog.html', blogs=_blogs, user=self.user)
    else:
      _blogs = Blog.query_blogs()
      self.render('blog.html', blogs=_blogs)

app = webapp2.WSGIApplication([('/', BlogsPage),
                               ('/newpost', AddNewPostPage),
                               ('/login', LoginPage),
                               ('/logout', Logout),
                               ('/blog/signup', SignUpPage),
                               ('/blog/([0-9]+)', PostPage),
                               ('/logout', Logout),], debug=True)
