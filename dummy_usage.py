#!/usr/bin/env python

import db_connect # uses pymongo...

db = db_connect.use.swift

db.usage.insert({
    "account":"admin",
    "usage":{
        "2012030100":{
            "2xx":               0,
            "4xx":               0,
            "5xx":               0,
            "COPY":              0,
            "DELETE":            0,
            "GET":               0,
            "HEAD":              0,
            "POST":              0,
            "PUT":               0,
            "account_requests":  0,
            "bytes_used":        0,
            "container_count":   1,
            "container_requests":0,
            "object_count":      0,
            "object_requests":   0,
            "ops_count":         0,
            "public_bw_in":      0,
            "public_bw_out":     0,
            "public_request":    0,
            "replica_count":     1,
            "service_bw_in":     0,
            "service_bw_out":    0,
            "service_request":   0},
        "2012030200":{
            "2xx":               0,
            "4xx":               0,
            "5xx":               0,
            "COPY":              0,
            "DELETE":            0,
            "GET":               0,
            "HEAD":              0,
            "POST":              0,
            "PUT":               0,
            "account_requests":  0,
            "bytes_used":        108838,
            "container_count":   4,
            "container_requests":0,
            "object_count":      464,
            "object_requests":   0,
            "ops_count":         0,
            "public_bw_in":      0,
            "public_bw_out":     0,
            "public_request":    0,
            "replica_count":     1,
            "service_bw_in":     0,
            "service_bw_out":    0,
            "service_request":   0},
        "2012030300":{
            "2xx":               0,
            "4xx":               0,
            "5xx":               0,
            "COPY":              0,
            "DELETE":            0,
            "GET":               0,
            "HEAD":              0,
            "POST":              0,
            "PUT":               0,
            "account_requests":  0,
            "bytes_used":        0,
            "container_count":   0,
            "container_requests":0,
            "object_count":      0,
            "object_requests":   0,
            "ops_count":         0,
            "public_bw_in":      0,
            "public_bw_out":     0,
            "public_request":    0,
            "replica_count":     1,
            "service_bw_in":     0,
            "service_bw_out":    0,
            "service_request":   0}
    }
})
print "inserted data into swift.usage"

#db.usage.remove({"account":"admin"})
#print "removed dummy data from swift.usage"
