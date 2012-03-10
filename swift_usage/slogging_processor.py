#!/usr/bin/env python

from swift_usage import db_connect # requires pymongo
from swift_usage import swift_client

swift_auth_url = "http://172.16.23.61:8080/v1.0"
swift_user = "admin"
swift_key = "DTaacz6qeuiCmfd6yNuuLYs5oAiHhhrX2aJbwfJ2sZb1hG2YxQPswm6tyn8rSV3D903ctnrKe38EsAH1iCwVQA"

slogging_container = "log_processing_data"

db = db_connect.use.swift
swift = swift_client.Connection(swift_auth_url, swift_user, swift_key)

container_details, container_objects = swift.get_container(slogging_container)

if db.processor.find({"current_file": {"$exists": False}}):
    print "processor does not have a current file. find one...\n"
    
    log_names = sorted([obj["name"] for obj in container_objects if ".csv.gz" in obj["name"]])
        
    print [name for name in log_names]
    
#print container_details
#print "\n\n"s
#print container_objects

#for obj in container_objects:
#    print obj['name']
