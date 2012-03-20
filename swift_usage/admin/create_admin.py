#!/usr/bin/env python

import datetime
import hmac
import hashlib
from swift_usage.utils import db_connect # requires pymongo

db = db_connect.db
keys = {}
keys["label"] = "admin"
keys["api_key"] = hmac.new('cloudops', str(datetime.datetime.now()), hashlib.sha1).hexdigest()
keys["secret_key"] = hmac.new(keys["api_key"], 'cloudops', hashlib.sha1).hexdigest()
db.auth.insert({"api_key":keys["api_key"], "secret_key":keys["secret_key"], "label":keys["label"], "admin":"True"})
print keys
