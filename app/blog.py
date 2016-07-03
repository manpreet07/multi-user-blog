import hmac
import os

import jinja2
import webapp2
import hashlib
from models import Blog, User, Comment, Like

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)


def make_salt():
  """
  method return salt
  :return:
  :rtype:
  """
  return "dsfkadb425b42534132erada34sdsadaas1234sqedq2112e21e22312qerdfdsfarqewr31421324"


def hash_str(s):
  """
  method to create hash string
  :param s:
  :type s:
  :return:
  :rtype:
  """
  return hmac.new(make_salt(), s).hexdigest()


def make_secure_val(s):
  """
  method return secure value
  :param s:
  :type s:
  :return:
  :rtype:
  """
  return "%s|%s" % (s, hash_str(s))


def check_secure_val(h):
  """
  metohd to check secure value
  :param h:
  :type h:
  :return:
  :rtype:
  """
  val = h.split('|')[0]
  if h == make_secure_val(val):
    return val


def make_pw_hash(name, pw, salt=None):
  """
  method to make hash password
  :param name:
  :type name:
  :param pw:
  :type pw:
  :param salt:
  :type salt:
  :return:
  :rtype:
  """
  if not salt:
    salt = make_salt()
  h = hashlib.sha256(name + pw + salt).hexdigest()
  return '%s,%s' % (salt, h)


def valid_pw(name, pw, h):
  """
  method to validate hash password
  :param name:
  :type name:
  :param pw:
  :type pw:
  :param h:
  :type h:
  :return:
  :rtype:
  """
  _salt = h.split(",")[0]
  return True if h == make_pw_hash(name, pw, _salt) else False


class Handler(webapp2.RequestHandler):
  """
  Main Handler class
  """

  def write(self, *a, **kw):
    """
    method to write response
    :param a:
    :type a:
    :param kw:
    :type kw:
    """
    self.response.out.write(*a, **kw)

  def render_str(self, template, **params):
    """
    method to render template
    :param template:
    :type template:
    :param params:
    :type params:
    :return:
    :rtype:
    """
    t = jinja_env.get_template(template)
    return t.render(params)

  def render(self, template, **kw):
    self.write(self.render_str(template, **kw))

  def read_secure_cookie(self, name):
    """
    method to read cookies
    :param name:
    :type name:
    :return:
    :rtype:
    """
    cookie_val = self.request.cookies.get(name)
    return cookie_val and check_secure_val(cookie_val)

  def set_secure_cookie(self, name, val):
    """
    method to set cookies
    :param name:
    :type name:
    :param val:
    :type val:
    """
    cookie_val = make_secure_val(val)
    self.response.headers.add_header('Set-Cookie', '%s=%s' % (name, cookie_val))

  def login(self, user):
    """
    method to login
    :param user:
    :type user:
    """
    self.set_secure_cookie('user_id', str(user))

  def logout(self):
    """
    method to log out
    """
    self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

  def initialize(self, *a, **kw):
    """
    Initialize method returns user
    :param a:
    :type a:
    :param kw:
    :type kw:
    """
    webapp2.RequestHandler.initialize(self, *a, **kw)
    uid = self.read_secure_cookie('user_id')
    self.user = uid and User.by_id(int(uid))


class AddNewPostPage(Handler):
  """Add new post page class"""

  def get(self):
    """
    Get method to render newpost.html
    """
    if self.user:
      self.render('newpost.html')
    else:
      self.redirect('/login')

  def post(self):
    """
    Post method to create new posts
    :rtype: object
    """
    blog = {}
    _title = self.request.get("title")
    _blog = self.request.get("blog")
    _title_error = "Please enter title"
    _post_error = "Please enter post"

    if self.user:
      if _title and _blog:
        user = self.user
        newPost = Blog(user=user.key, title=_title, blog=_blog)
        newPost_key = newPost.put()
        newPostID = newPost_key.id()
        self.redirect('/blog/%s' % str(newPostID))
      elif _title == "" or _blog == "":
        if _title == "":
          blog["title"] = ""
          blog["blog"] = _blog
          self.render('newpost.html', title_error=_title_error, blog=blog)
        if _blog == "":
          blog["title"] = _title
          blog["blog"] = ""
          self.render('newpost.html', post_error=_post_error, blog=blog)
    else:
      self.redirect('/login')


class PostPage(Handler):
  """ post page class """

  def get(self, post_id):
    """
    Get method to render permalink.html
    :param post_id:
    :type post_id:
    :return:
    :rtype:
    """
    user = self.user
    parent = user.key
    blog_key = Blog.get_by_id(int(post_id))
    post = blog_key

    if not post:
      self.render('error.html')
      return

    self.render("permalink.html", blog=post)


class SignUpPage(Handler):
  """ signup page class """

  def get(self):
    """
    Get method to render signup.html
    """
    self.render('signup.html')

  def post(self):
    """
    Post method to signup
    """
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
        _user = User.query(User.name == _username).get()
        print _user
        if _user is None:
          _newUser = User.register(_username, _pwd, _email)
          newUserKey = _newUser.put()
          newUser = newUserKey.id()
          self.login(newUser)
          self.render('welcome.html', user=_username)
        else:
          self.render('signup.html', username_error="User already exist")
      else:
        self.render('signup.html', verify_pw_error=verify_pw_error)

    if _username == "" or _pwd == "" or _verify_pwd == "" or _email == "":
      self.render('signup.html', username_error=username_error, pw_error=pw_error,
                  verify_pw_error=verify_pw_error, email_error=email_error)


class LoginPage(Handler):
  """ login page class """

  def get(self):
    """
    Get metoh to render login.html
    """
    self.render('login.html')

  def post(self):
    """
    Post method to login and render blog.html
    """
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
        self.redirect('/blog/signup')
    else:
      self.render('blog.html', username_error=username_error,
                  pw_error=pw_error, error=error)


class Logout(Handler):
  """logout page class"""

  def get(self):
    """
    Get methog to render logout.html
    """
    self.logout()
    self.render('logout.html')


class BlogsPage(Handler):
  """Blogs page class"""

  def get(self):
    """
    Get method to render blog.html
    """
    if self.user:
      user_key = self.user
      user_id = user_key.key.id()
      _user = User.by_id(int(user_id))
      _blogs = Blog.query_blogs().fetch()
      likes = Like.query().fetch()
      self.render('blog.html', blogs=_blogs, user=_user, likes=likes)
    else:
      _blogs = Blog.query_blogs().fetch()
      self.render('blog.html', blogs=_blogs, user=None, likes=None)

  def post(self):
    """
    Post method to like and unlike blogs
    """
    if self.user:
      if self.request.get("like_blog"):
        _blog_id = self.request.get("like_blog")
        user = self.user
        user_id = user.key.id()
        _user = User.by_id(int(user_id))
        _blog = Blog.get_by_id(int(_blog_id))
        like = Like(user=user.key, blog=_blog.key)
        like.like = 1
        like_key = like.put()
        blog = _blog.key.get()
        blog.likes.append(like_key)
        blog.put()
        self.redirect('/')
      if self.request.get("dislike"):
        _blog_id = self.request.get("dislike")
        user = self.user
        user_id = user.key.id()
        _user = User.by_id(int(user_id))
        _blog = Blog.get_by_id(int(_blog_id))
        like = Like.query(Like.user == user.key, Like.blog == _blog.key).get()
        like_key = like.key
        blog = _blog.key.get()
        blog.likes.remove(like_key)
        blog.put()
        like_key.delete()
        self.redirect('/')
    else:
      self.redirect('/login')

  def isLiked(user, blog, likes):
    """
    Helper method return boolean if blog is liked by login user
    :param blog:
    :type blog:
    :param likes:
    :type likes:
    :return:
    :rtype:
    """
    for like in likes:
      if (like.key in blog.likes) and (like.user == user.key):
        return True
    return False

  jinja_env.globals.update(isLiked=isLiked)


class EditPostPage(Handler):
  """Edit Post page class"""

  def get(self, _postID):
    """
    Get method to get post by id
    """
    if self.user:
      user = self.user
      parent = user.key
      blog_key = Blog.get_by_id(int(_postID))
      post = blog_key
      self.render('editpost.html', blog=post)

  def post(self, _postID):
    """
    Post method to edit post by id
    :param _postID:
    :type _postID:
    """
    _title = self.request.get("title")
    _blog = self.request.get("blog")
    _post_error = "Please enter post"
    _title_error = "Please enter title"
    if self.user:
      if _title and _blog:
        user = self.user
        parent = user.key
        blog_key = Blog.get_by_id(int(_postID))
        blog_key.title = _title
        blog_key.blog = _blog
        blog_key.put()
        self.redirect('/')
      elif _title == "" or _blog == "":
        if _title == "":
          blog = {"title": "", "blog": _blog}
          self.render('editpost.html', title_error=_title_error, blog=blog)
        if _blog == "":
          blog = {"title": _title, "blog": ""}
          self.render('editpost.html', post_error=_post_error, blog=blog)
    else:
      self.redirect('/login')


class DeletePostPage(Handler):
  """Delete page class"""

  def get(self, deletID):
    """
    Get method to get Post by id
    :param deletID:
    :type deletID:
    """
    if self.user:
      user = self.user
      parent = user.key
      blog_key = Blog.get_by_id(int(deletID))
      post = blog_key
      self.render('deletepost.html', blog=post)

  def post(self, deletID):
    """
    Post method to delete post by id
    :param deletID:
    :type deletID:
    """
    if self.user:
      blog_key = Blog.get_by_id(int(deletID))
      blog_key.key.delete()
      self.redirect("/")
    else:
      self.redirect('/login')

class CommentPage(Handler):
  """Comment page class"""

  def get(self, _postID):
    """
    Get method to get post by id and render comment.html
    :param _postID:
    :type _postID:
    """
    blog_key = Blog.get_by_id(int(_postID))
    self.render('comment.html', blog=blog_key)

  def post(self, _postID):
    """
    Post method to add comment on the blog
    :param _postID:
    :type _postID:
    """
    if self.user:
      _user = self.user
      user_id = _user.key.id()
      user_key = User.get_by_id(int(user_id))
      _comment = self.request.get("comment")
      blog_key = Blog.get_by_id(int(_postID))
      comment = Comment(comment=_comment, user=user_key.key)
      comment_key = comment.put()
      blog = blog_key.key.get()
      blog.comments.append(comment_key)
      blog.put()
      self.redirect('/')
    else:
      self.redirect('/login')


class EditCommentPage(Handler):
  """Edit Comment page class"""

  def get(self, _postID):
    """
    Get method to get post by id and render editcomment.html
    :param _postID:
    :type _postID:
    """
    if self.user:
      comment_key = Comment.get_by_id(int(_postID))
      post = comment_key
      self.render('editcomment.html', comment=post)
    else:
      self.redirect('/login')

  def post(self, _postID):
    """
    Post method to update comment by id
    :param _postID:
    :type _postID:
    """
    _comment = self.request.get("comment")
    _comment_error = "Please enter comment"
    if self.user:
      if _comment:
        comment_key = Comment.get_by_id(int(_postID))
        comment_key.comment = _comment
        comment_key.put()
        self.redirect('/')
      elif _comment == "":
        self.render('editcomment.html', _comment_error=_comment_error, )
    else:
      self.redirect('/login')


class DeleteCommentPage(Handler):
  """Delete Comment page class"""

  def get(self, deleteID):
    """
    Get method to get post by id to delete
    :param deleteID:
    :type deleteID:
    """
    if self.user:
      comment_key = Comment.get_by_id(int(deleteID))
      post = comment_key
      self.render('deletecomment.html', comment=post)
    else:
      self.redirect('/login')

  def post(self, deleteID):
    """
    Post method to delete comment by id
    :param deleteID:
    :type deleteID:
    """
    if self.user:
      comment_key = Comment.get_by_id(int(deleteID))
      comment_key.key.delete()
      self.redirect("/")
    else:
      self.redirect('/login')


app = webapp2.WSGIApplication([('/', BlogsPage),
                               ('/newpost', AddNewPostPage),
                               ('/login', LoginPage),
                               ('/comment/([0-9]+)', CommentPage),
                               ('/editcomment/([0-9]+)', EditCommentPage),
                               ('/deletecomment/([0-9]+)', DeleteCommentPage),
                               ('/logout', Logout),
                               ('/blog/signup', SignUpPage),
                               ('/blog/([0-9]+)', PostPage),
                               ('/editpost/([0-9]+)', EditPostPage),
                               ('/deletepost/([0-9]+)', DeletePostPage),
                               ('/logout', Logout), ], debug=True)
