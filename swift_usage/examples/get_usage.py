#!/usr/bin/env python

import hashlib
import hmac
import urllib2

account = "syntenic"
start = "2012030100"
end = "2012060100"

api_key = "57fab605eff621987b3b5df15675465efb649e75"
secret_key = "c3d2f416b278bfc33052f60dbafdb889c1fe0613"

path = "/usage/"+account

params = {}
params["start"] = start
params["end"] = end
params["apikey"] = api_key

# build signature
# all params have keys and values lower cased, then sorted and joined together as url query parameters to the path which is hashed via sha1.
# path to hash: /usage/admin?apikey=4ce66c97c2d38ca211f4b3d78779f72d0fada9cc&end=2012030100&start=2012020100
signature = hmac.new(secret_key, path+"?"+"&".join(sorted(map(lambda (k,v):k.lower()+"="+v.lower(), params.items()))), hashlib.sha1).hexdigest()

# final query string...
url = "http://172.16.23.61:8888"+path+"?"+"&".join(map(lambda (k,v):k+"="+v, params.items()))+"&signature="+signature

print "requesting: "+url

try:
    result = urllib2.urlopen(url)
    print result.read()
except urllib2.HTTPError, e:
    print e
except urllib2.URLError, e:
    print e
