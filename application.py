# -*- coding: utf-8 -*-
"""
Created on Sat Mar 24 17:34:54 2018

@author: woon.zhenhao
"""
import flask
from flask import Flask, request, make_response, render_template, redirect
from flask_cors import CORS
from flask_restful import Resource, Api
import os

app = Flask(__name__)
api = Api(app)
CORS(app)

@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/main')
def main():
    return render_template('index.html')


if __name__ == '__main__':
     app.run(debug=True)