#!/usr/bin/env python
import hashlib
import hmac
import urllib2
import sys

api_key = "92efa04a6269b84268f36ac9ccae03f4e34c5263"
secret_key = "3274b46befebc2b47d6a69711642e787046e2d31"

if len(sys.argv) <> 2:
    print "Usage: python "+sys.argv[0]+" <label>"
    sys.exit(1)

path = "/generate_key/"+sys.argv[1]

params = {}
params["apikey"] = api_key

# build signature
# all params have keys and values lower cased, then sorted and joined together as url query parameters to the path which is hashed via sha1.
# requesting: http://www.example.com/usage/account?start=2012030100&apikey=28a1a...30300&signature=97b01...5df4e
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
