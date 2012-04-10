import pymongo # setup: sudo pip install pymongo
from ConfigParser import ConfigParser
import os.path
import sys

conf_file = ""
conf = ConfigParser({ # defaults
            "mongo-db-name":"swift_usage",
            "mongo-db-host":"localhost",
            "mongo-db-port":"27017"
        })

if os.path.exists("/etc/swift/swift-usage.conf"):
    conf_file = "/etc/swift/swift-usage.conf"
    
conf.read(conf_file)
    
# load config from the config file if it exists
mongo_db_name = conf.get('DEFAULT', 'mongo-db-name')
mongo_db_host = conf.get('DEFAULT', 'mongo-db-host')
mongo_db_port = int(conf.get('DEFAULT', 'mongo-db-port'))

db = pymongo.Connection(mongo_db_host, mongo_db_port)[mongo_db_name] # use the swift_usage database