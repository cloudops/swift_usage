#!/usr/bin/env python

import bottle # setup: sudo pip install bottle
import datetime
import hmac
import hashlib
import urllib

import db_connect # uses pymongo...

# @decorator: verify that the incoming request has a valid apikey and signature.
def authorize(callback):
    def validate(*args, **kwargs):
        # rebuild the signature in order to check if the signature that was passed is valid.
        sig_params = dict((k.lower(), v.lower()) for k,v in bottle.request.query.items()) # signature items are the lower cased query parameters. 
        if "signature" in sig_params:
            del(sig_params["signature"]) # remove the signature because it was not included in the creation of the signature.
        else:
            bottle.abort(403, "The request is missing the required 'signature'.")
        sig_str = bottle.request.path+"?"+"&".join(sorted(map(lambda (k,v):k+"="+v, sig_params.items())))
        
        if "apikey" in bottle.request.query:
            db = db_connect.use.auth
            keys = db.keys.find_one({"api_key":bottle.request.query.apikey})
            if keys:
                signature = hmac.new(keys["secret_key"].encode('utf-8'), sig_str, hashlib.sha1).hexdigest()
                if signature == bottle.request.query.signature:
                    return callback(*args, **kwargs)
                else:
                    bottle.abort(403, "The request is not authorized.")
            else:
                bottle.abort(403, "The request is not authorized.")
        else:
            bottle.abort(403, "The request is missing the required 'apikey'.")
    return validate


# @decorator: verify that the incoming request is by an admin (MUST be used with @authorize for security).
def verify_admin(callback):
    def validate(*args, **kwargs):
        if "apikey" in bottle.request.query:
            db = db_connect.use.auth
            keys = db.keys.find_one({"api_key":bottle.request.query.apikey})
            if keys:
                if "admin" in keys and keys["admin"]:
                    return callback(*args, **kwargs)
                else:
                    bottle.abort(403, "The request is not authorized.")
            else:
                bottle.abort(403, "The request is not authorized.")
        else:
            bottle.abort(403, "The request is missing the required 'apikey'.")
    return validate


# homepage:  if we want to have any 'basic info', we would put it here.
@bottle.route('/')
def index():
    return "Swift Usage API"


# usage syntax:  describe the syntax for the  usage functionality.
@bottle.route('/usage')
def usage_index():
    return "URL Syntax: /usage/account?start=2012030100&end=2012030300&apikey=520f6...6bf38&signature=83a12...dbec1"


# usage function: does the usage work.
@bottle.route('/usage/<account>', apply=[authorize])
def usage(account):
    labels_to_output = ['COPY', 'DELETE', 'GET', 'HEAD', 'POST', 'PUT', 'bytes_used', 'public_bw_in', 'public_bw_out', 'public_request']
    f_str = bottle.request.query.start
    t_str = bottle.request.query.end
    if not f_str or not t_str or len(f_str) != 10 or len(t_str) != 10:
        bottle.abort(400, "You must specify 'start' and 'end' dates. Check '/usage' for syntax.")
    else:
        output = {}
        db = db_connect.use.swift
        
        # find the account usage via the account name passed via the url
        usage = db.usage.find_one({"account":account})
        if usage:
            # setup the 'from' and 'to' datetime objects which will control cycling through the hourly data.
            f_dt = datetime.datetime(int(f_str[0:4]), int(f_str[4:6]), int(f_str[6:8]), int(f_str[8:10])) # format: YYYYMMDDHH
            t_dt = datetime.datetime(int(t_str[0:4]), int(t_str[4:6]), int(t_str[6:8]), int(t_str[8:10])) # format: YYYYMMDDHH
            
            # handle the unique request for a single hour of data.
            if f_dt == t_dt: # start and end dates are the same
                date_key = f_dt.strftime("%Y%m%d%H") # create the date_key from the datetime
                if date_key in usage['usage']:
                    for k,v in usage['usage'][date_key].items(): # loop through the database data
                        if k in labels_to_output: # limit the data as per config
                            output[k] = int(v) # put the data in the output object.
            
            # handle all requests other than the 'single hour' request.
            # start <= usage < end
            current = f_dt # set the 'current' datetime object which will increment by 1 hour and act as a key datestamp.
            while current < t_dt:
                # check for data in the database
                date_key = current.strftime("%Y%m%d%H") # create the date_key from the current datetime
                if date_key in usage['usage']:
                    for k,v in usage['usage'][date_key].items(): # loop through the database data
                        if k in labels_to_output: # limit the data as per config
                            if k in output:
                                output[k] = int(output[k]) + int(v) # this label exists, sum it with the current value
                            else:
                                output[k] = int(v) # this label does not exist yet, seed it with the current value
                # increment the current datetime stamp by 1 hour to generate the next date_key.
                current += datetime.timedelta(hours=1)
        return output


# generate keys: creates new 'non-admin' authorization keys (requires 'admin').
@bottle.route('/generate_key/<label>', apply=[authorize, verify_admin])
def generate_key(label):
    db = db_connect.use.auth
    keys = {}
    keys["label"] = label
    keys["api_key"] = hmac.new('cloudops', str(datetime.datetime.now()), hashlib.sha1).hexdigest()
    keys["secret_key"] = hmac.new(keys["api_key"], 'cloudops', hashlib.sha1).hexdigest()
    db.keys.insert({"api_key":keys["api_key"], "secret_key":keys["secret_key"], "label":keys["label"]})
    return keys


# favicon: serve a favicon.ico so the pages do not return a 404 for the /favicon.ico path in the browser.
@bottle.route('/favicon.ico')
def favicon():
    return bottle.static_file('favicon.ico', root='./static/')


# enable debugging.
bottle.debug(True)

# start the server.
bottle.run(server=bottle.PasteServer, host='172.16.23.61', port=8888, reloader=True)
