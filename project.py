'''
Created on May 10, 2016

@author: manpreetsingh
'''

import webapp2

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Hello, webapp World!')

app = webapp2.WSGIApplication([('/'), MainPage], debug=True)