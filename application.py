# -*- coding: utf-8 -*-
"""
Created on Sat Mar 24 17:34:54 2018

@author: woon.zhenhao
"""

from flask import Flask, request, make_response, render_template, redirect
from flask_cors import CORS
from flask_restful import Resource, Api
#
application = Flask(__name__)
api = Api(application)
CORS(application)

@application.route('/')
def hello():
    return render_template('index.html')

@application.route('/main')
def main():
    return render_template('index.html')


# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()