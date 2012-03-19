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
dt_now_delta = 5 # hours prior to now that we will loop till (we will never have logs up to date).

db = db_connect.use.swift # connect to the usage db 'swift'
swift = swift_client.Connection(swift_auth_url, swift_user, swift_key) # create a swift client for accessing data in swift.

# get the list of objects in the slogging container.
container_headers, container_objects = swift.get_container(slogging_container) # grab the usage objects from slogging
log_names = sorted([obj["name"] for obj in container_objects if ".csv.gz" in obj["name"]]) # create a sorted list of the slogging logs


# function to process a dt and see if there is an associated log, if so, process it...
def process_dt(dt, from_miss=False):
    file_substr = dt.strftime("%Y/%m/%d/%H/") # date substring for the current dt to match the incoming .csv.gz file
    file_arry = [name for name in log_names if file_substr in name] # there should only be one match (we only look at the first)
    if len(file_arry) > 0: # we have a matching log for this hour.
        print file_substr+" found log: "+file_arry[0]
        obj_headers, obj_data = swift.get_object(slogging_container, file_arry[0]) # get the log data
        d = zlib.decompressobj(16 + zlib.MAX_WBITS) # setup the decompresser | http://stackoverflow.com/questions/2423866/python-decompressing-gzip-chunk-by-chunk/2424549#2424549
        csv_data = csv.reader(d.decompress(obj_data).split('\n'), delimiter=',') # get the csv data from the log
        header_row = True # first row is the header, then this will be set to False
        headers = []
        for data in csv_data: # go through line at a time.
            if header_row: # populate the array which will be they keys in the usage object
                headers = data
                header_row = False
            else: #data row, so process the data.
                account = data[1]
                dt_key = "%s%s%s%s" % (data[0][0:4], data[0][5:7], data[0][8:10], data[0][11:13]) # format: YYYY/MM/DD HH:MM:SS => YYYYMMDDHH
                existing_usage = db.usage.find_one({"account":account})
                if existing_usage: # there is an existing account with usage, add this usage to it.
                    if dt_key not in existing_usage["usage"]: # put this hour's data in the database
                        print "=> INSERTING hour '%s' into '%s'..." % (dt_key, account)
                        usage_obj = {}
                        for i, header in enumerate(headers[2:]):
                            usage_obj[header] = data[i]
                        print "data: "+str({dt_key:usage_obj})
                        db.usage.update({"account":account}, {"$set":{"usage."+dt_key:usage_obj}})
                    else: 
                        print "=> SKIPPING hour '%s' for '%s', it already exists..." % (dt_key, account)
                else: # create the user and seed it with the current data.
                    print "=> CREATING usage account '%s' starting from '%s'..." % (account, dt_key)
                    usage_obj = {}
                    for i, header in enumerate(headers[2:]):
                        usage_obj[header] = data[i]
                    print "data: "+str({dt_key:usage_obj})
                    db.usage.insert({"account":account, "usage":{dt_key:usage_obj}})
                
        if from_miss: # this dt was from the misses array, so remove it now that we found a matching log.
            db.processor.update({"processor":"slogging"}, {"$pull":{"misses":dt}})
            
    else: # we do not have a log for this hour in this run.
        current_processor = db.processor.find_one({"processor":"slogging"})
        print "processing miss: "+str(dt)
        if "misses" in current_processor:
            if dt not in current_processor["misses"]: # current miss is not in the array already, add it.
                db.processor.update({"processor":"slogging"}, {"$push":{"misses":dt}})
        else: # add a 'misses' array to the processor with this dt.
            db.processor.update({"processor":"slogging"}, {"$set":{"misses":[dt]}})
            
    if not from_miss:
        # move the dt pointer in the processor to the next dt that should be processed.
        next_dt = dt + datetime.timedelta(hours=1)
        db.processor.update({"processor":"slogging"}, {"$set":{"current_dt":next_dt}})


# setup the processor and start execution.
processor = db.processor.find_one({"processor":"slogging"})
# if we do not have an slogging processor, create one.
if not processor:
    print "no slogging processor, creating one..."
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
last_dt = datetime.datetime.now() - datetime.timedelta(hours=dt_now_delta)
while current_dt <= last_dt:
    process_dt(current_dt)
    current_dt += datetime.timedelta(hours=1) # minimize db access by just incrementing the current dt with a local variable instead of accessing the db each time.

# status of the processor after the run.
print db.processor.find_one({"processor":"slogging"})
    
