# -*- coding: utf-8 -*-
"""
Created on Sat Mar 24 17:34:54 2018

@author: woon.zhenhao
"""

from flask import Flask, request, make_response, render_template, redirect
from flask_cors import CORS
from flask_restful import Resource, Api
#
app = Flask(__name__)
#api = Api(app)
#CORS(app)

#@app.route('/')
#def hello():
#    return render_template('index.html')
#
#@app.route('/main')
#def main():
#    return render_template('index.html')

#if __name__ == '__main__':
#     app.debug=True
#     app.run(host='0.0.0.0')

# print a nice greeting.
def say_hello(username = "World"):
    return '<p>Hello %s!</p>\n' % username

# some bits of text for the page.
header_text = '''
    <html>\n<head> <title>EB Flask Test</title> </head>\n<body>'''
instructions = '''
    <p><em>Hint</em>: This is a RESTful web service! Append a username
    to the URL (for example: <code>/Thelonious</code>) to say hello to
    someone specific.</p>\n'''
home_link = '<p><a href="/">Back</a></p>\n'
footer_text = '</body>\n</html>'

# EB looks for an 'application' callable by default.
#application = Flask(__name__)

# add a rule for the index page.
app.add_url_rule('/', 'index', (lambda: header_text +
    say_hello() + instructions + footer_text))

# add a rule when the page is accessed with a name appended to the site
# URL.
app.add_url_rule('/<username>', 'hello', (lambda username:
    header_text + say_hello(username) + home_link + footer_text))

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    app.debug = True
    app.run()