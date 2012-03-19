#!/usr/bin/env python

import datetime

import csv
import zlib

from swift_usage import db_connect # requires pymongo
from swift_usage import swift_client

swift_auth_url = "http://172.16.23.61:8080/v1.0"
swift_user = "admin"
swift_key = "DTaacz6qeuiCmfd6yNuuLYs5oAiHhhrX2aJbwfJ2sZb1hG2YxQPswm6tyn8rSV3D903ctnrKe38EsAH1iCwVQA"

slogging_container = "log_processing_data" # slogging container where the collector uploads to.
dt_padding = 20 # hours prior to now that we will loop till (we will never have logs up to date).

# connect to the usage db
db = db_connect.use.swift
swift = swift_client.Connection(swift_auth_url, swift_user, swift_key)

# get the list of objects in the slogging container.
container_headers, container_objects = swift.get_container(slogging_container)
log_names = sorted([obj["name"] for obj in container_objects if ".csv.gz" in obj["name"]])


def process_dt(dt, from_miss=False):
    file_substr = dt.strftime("%Y/%m/%d/%H/")
    file_arry = [name for name in log_names if file_substr in name]
    if len(file_arry) > 0: # we have a log for this hour.
        print "found log: "+file_arry[0]
        obj_headers, obj_data = swift.get_object(slogging_container, file_arry[0])
        d = zlib.decompressobj(16 + zlib.MAX_WBITS)
        csv_data = csv.reader(d.decompress(obj_data).split('\n'), delimiter=',')
        header_row = True
        headers = []
        for data in csv_data:
            if header_row:
                headers = data
                header_row = False
            else: #data row
                account = data[1]
                dt_key = "%s%s%s%s" % (int(data[0][0:4]), int(data[0][5:7]), int(data[0][8:10]), int(data[0][11:13])) # format: YYYY/MM/DD HH:MM:SS => YYYYMMDDHH
                account_usage = db.usage.find_one({"account":account})
                if account_usage: 
                    if dt_key in account_usage["usage"]: # append to the current data.
                    
                        print "update existing usage for this hour: "+dt_key
                        
                    else: # seed this hour with this data
                        print "seed with this hour's data: "+dt_key
                        usage_obj = {}
                        for i, header in enumerate(headers[2:]):
                            usage_obj[header] = data[i]
                        db.usage.update({"account":account}, {"$set":{"usage."+dt_key:usage_obj}})
                        print db.usage.find_one({"account":account})
                else: # create the user and seed it with the current data.
                    print "creating usage account: "+account+" ("+dt_key+")"
                    usage_obj = {}
                    for i, header in enumerate(headers[2:]):
                        usage_obj[header] = data[i]
                    db.usage.insert({"account":account, "usage":{dt_key:usage_obj}})
                    print db.usage.find_one({"account":account})    
                
        if from_miss: # this dt was from the misses array, so remove it from now that it is processed.
            db.processor.update({"processor":"slogging"}, {"$pull":{"misses":dt}})
            
    else: # we do not have a log in this run for this hour.
        current_processor = db.processor.find_one({"processor":"slogging"})
        print "processing miss: "+str(dt)
        if "misses" in current_processor:
            if dt not in current_processor["misses"]: # current miss is not in the array already, add it.
                db.processor.update({"processor":"slogging"}, {"$push":{"misses":dt}})
        else: # add a 'misses' array to the processor with this dt.
            db.processor.update({"processor":"slogging"}, {"$set":{"misses":[dt]}})
    next_dt = dt + datetime.timedelta(hours=1)
    db.processor.update({"processor":"slogging"}, {"$set":{"current_dt":next_dt}})


# setup the processor and start execution.
processor = db.processor.find_one({"processor":"slogging"})
# if we do not have an slogging processor, create one.
if not processor:
    print "no slogging processor, create one..."
    # grab the first file in the slogging csv sequence and establish the first current_file and current_dt
    file_pieces = log_names[0].split('/')
    current_dt = datetime.datetime(int(file_pieces[0]), int(file_pieces[1]), int(file_pieces[2]), int(file_pieces[3]))
    db.processor.insert({"processor":"slogging", "current_dt":current_dt})
    processor = db.processor.find_one({"processor":"slogging"})

# process the previous misses
if "misses" in processor:
    for dt in processor["misses"]:
        process_dt(dt, from_miss=True)

# grab the processor again because it has likely changed after processing the misses.
processor = db.processor.find_one({"processor":"slogging"})
current_dt = processor["current_dt"]
#last_dt = datetime.now() - datetime.timedelta(hours=dt_padding)
last_dt = current_dt + datetime.timedelta(hours=1)
while current_dt <= last_dt:
    process_dt(current_dt)
    current_dt += datetime.timedelta(hours=1)

print db.processor.find_one({"processor":"slogging"})
    
#print container_details
#print "\n\n"s
#print container_objects

#for obj in container_objects:
#    print obj['name'
