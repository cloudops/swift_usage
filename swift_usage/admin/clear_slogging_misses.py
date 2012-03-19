#!/usr/bin/env python

import hmac
import hashlib
from swift_usage.utils import db_connect # requires pymongo

db = db_connect.use.swift
db.processor.update({"processor":"slogging"}, {"$set":{"misses":[]}})
print db.processor.find_one({"processor":"slogging"})
