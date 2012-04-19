#!/usr/bin/env python

import hashlib
import hmac
import urllib2

account = "admin"
start = "2012030000"
end = "2012060000"

api_key = "313615b783f562183c0a0ae672e143d1bd446eda"
secret_key = "25eaaafaf6beaa85ea5ec4075c1e73e4c500c195"

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
