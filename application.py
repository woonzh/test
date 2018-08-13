# -*- coding: utf-8 -*-
"""
Created on Sat Mar 24 17:34:54 2018

@author: woon.zhenhao
"""
import flask
from flask import Flask, request, make_response, render_template, redirect
from flask_cors import CORS
from flask_restful import Resource, Api
import json
import dbconnector as db
import main
import redis
import MPCall
import shopee as sh
import pandas as pd
from rq import Connection, get_failed_queue, Queue, get_current_job
from rq.job import Job
from worker import conn
import os
import csvTester

app = Flask(__name__)
api = Api(app)
CORS(app)

@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/main')
def main():
    return render_template('index.html')

@app.route('/accounts')
def getAccount():
    return render_template('accounts.html')

@app.route('/inventory')
def directInventory():
    return render_template('inventory.html')

@app.route('/shopee')
def shopee():
    return render_template('shopee.html')

@app.route('/delivery')
def delivery():
    return render_template('delivery.html')

@app.route('/csvtester')
def csvtester():
    return render_template('csvtester.html')

@app.route('/csvupload', methods=['POST', 'OPTIONS'])
def csvUpload():
    if request.method == 'POST':
        f=request.files['data']
        df=csvTester.findErrors(f)
        
        resp = make_response(df.to_csv(header=True, index=False))
        resp.headers["Content-Disposition"] = "attachment; filename=error_reports.csv"
        resp.headers["Content-Type"] = "text/csv"
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        resp.headers['Access-Control-Allow-Methods']= 'GET,PUT,POST,DELETE,OPTIONS'
        return resp

class CreateAccount(Resource):
    def get(self):
        name = request.args.get("name" ,type = str, default="")
        sellerid = request.args.get("sellerid" ,type = str, default="")
        imsapi=request.args.get("imsapi", type=str, default="")
        tmsapi=request.args.get("tmsapi", type=str, default="")
        query="INSERT INTO accts (acct_name, seller_id, ims_api_key, tms_api_key) VALUES(%s, %s, %s, %s)" % (name, sellerid, imsapi, tmsapi)
        
        result=db.runquery(query)
        df={
            "result": result
                }
        
        resp = flask.Response(json.dumps(df))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp

class AccountDetails(Resource):        
    def get(self):
        print("get account details")
        accounts=main.getAccountDetails()
        print(accounts)
        resp = flask.Response(json.dumps(accounts))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp

class Accounts(Resource):
    def get(self):
        accts=db.getAccounts()
        print(accts)
                   
        resp = flask.Response(json.dumps(accts))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp
    
class Testworker(Resource):
    def get(self):
        print("testworker start")
        q=Queue(connection=conn)
        job=q.enqueue(main.updateInventories2, "1", "false")
        print("testworker ends")
        return str(job.id)
    
class Inventory(Resource):
    def get(self):
        ctype = request.args.get("ctype" ,type = str, default="")
        sellerid = request.args.get("sellerid" ,type = str, default="")
        purpose=request.args.get("purpose", type=str)
        imssku=request.args.get("imssku", type=str, default="")
        mccpsku=request.args.get("mccpsku", type=str, default="")
        
        print("purpose: %s, sellerid: %s, ctype: %s"%(purpose, sellerid, ctype))
        q=Queue(connection=conn)
        
        result={}
        
        if (purpose=="data"):
            timeNeeded=MPCall.getTimeNeeded(sellerid)
            job=q.enqueue(main.updateInventories2,sellerid, "false")
            print("success")
            result['jobid']=str(job.id)
            result['time']=str(timeNeeded)
            print(result)
        else:
            if (ctype=="seller"):
                job=q.enqueue(main.updateInventories2,sellerid, "true")
                result['jobid']=str(job.id)
            else:
                val=main.updateSingularSKU(imssku, sellerid)
                result=val
                
        resp = flask.Response(json.dumps(result))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        print("header success")
        return resp
    
class Failedworkers(Resource):
    def get(self):
        redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
        conn = redis.from_url(redis_url)
        ret={}
        with Connection(conn):
            failed_jobs= get_failed_queue()
            print(failed_jobs.jobs)
            ret['failed jobs']=failed_jobs.jobs
        
        resp = flask.Response(json.dumps(ret))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        print("header success")
        return resp
    
class GetJobReport(Resource):
    def get(self):
        jobid = request.args.get("jobid" ,type = str, default="")
        redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
        conn = redis.from_url(redis_url)
        ret={}
        with Connection(conn):
            job = Job.fetch(jobid,conn)
            if job.is_finished:
                ret['status']='Completed'
                ret['result']=job.return_value
            elif job.is_queued:
                ret['status']='in-queue'
            elif job.is_started:
                ret['status']='waiting'
            elif job.is_failed:
                ret['status']='failed'
        
        resp = flask.Response(json.dumps(ret))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        print("header success")
        return resp
    
class ShopeeURL(Resource):
    def get(self):
        ret=sh.extractUrl()
        
        resp = flask.Response(json.dumps(ret))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        print("header success")
        return resp
    
class ShopeeRedirect(Resource):
    def get(self):
        shopid = request.args.get("shop_id", default="")
        success = request.args.get("success", default=1)
        msg = request.args.get("extra", default="")
        
        if success==1:
            shopid=str(shopid)
        else:
            shopid="Failed to retrieve. "+ str(msg)
            
        url="https://mccptester.herokuapp.com/shopee?shopid=%s" % (shopid)
        print("url: " + url)
        
        return redirect(url, code=302)
    
class DeliveryCheck(Resource):
    def get(self):
        increment_id = request.args.get("increment_id", default="")
        df=MPCall.getShipments(str(increment_id))
        
        resp = flask.Response(json.dumps(df))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        print(df)
        return resp
        

api.add_resource(AccountDetails, '/accountdetails')
api.add_resource(Accounts, '/accounts')
api.add_resource(Inventory, '/inventory')
api.add_resource(Testworker, '/testworker')
api.add_resource(Failedworkers, '/failedworkers')
api.add_resource(GetJobReport, '/jobreport')
api.add_resource(CreateAccount, '/createaccount')
api.add_resource(ShopeeURL, '/shopeeurl')
api.add_resource(ShopeeRedirect, '/shopeeredirect')
api.add_resource(DeliveryCheck, '/deliverycheck')

#test=Accounts
#res=test.get('')
#print(res.data)

if __name__ == '__main__':
     app.run(debug=True)