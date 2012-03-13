#!/usr/bin/env python

import datetime

from swift_usage import db_connect # requires pymongo
from swift_usage import swift_client

swift_auth_url = "http://172.16.23.61:8080/v1.0"
swift_user = "admin"
swift_key = "DTaacz6qeuiCmfd6yNuuLYs5oAiHhhrX2aJbwfJ2sZb1hG2YxQPswm6tyn8rSV3D903ctnrKe38EsAH1iCwVQA"

slogging_container = "log_processing_data" # slogging container where the collector uploads to.
now_padding = 20 # hours prior to now that we will loop till (we will never have logs up to date).

# connect to the usage db
db = db_connect.use.swift
swift = swift_client.Connection(swift_auth_url, swift_user, swift_key)

# get the list of objects in the slogging container.
container_details, container_objects = swift.get_container(slogging_container)
log_names = sorted([obj["name"] for obj in container_objects if ".csv.gz" in obj["name"]])

# setup the processor.
processor = db.processor.find_one({"processor":"slogging"})
# if we do not have an slogging processor, create one.
if not processor:
    print "no slogging processor, create one..."
    # grab the first file in the slogging csv sequence and establish the first current_file and current_dt
    first_file = log_names[0]
    print "first: "+first_file
    file_pieces = first_file.split('/')
    current_dt = datetime.datetime(int(file_pieces[0]), int(file_pieces[1]), int(file_pieces[2]), int(file_pieces[3]))
    db.processor.insert({"processor":"slogging", "current_dt":current_dt, "misses":[current_dt]})
    processor = db.processor.find_one({"processor":"slogging"})

if "misses" in processor:
    for dt in processor["misses"]:
        file_substr = dt.strftime("%Y/%m/%d/%H/")
        #file_str = [log_names[i] for i, name in log_names if file_substr in log_names[i]][0]
        print file_substr
        #print file_str
        print dt

print processor
    
#print container_details
#print "\n\n"s
#print container_objects

#for obj in container_objects:
#    print obj['name']
