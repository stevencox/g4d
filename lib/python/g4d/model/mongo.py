import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId

class MongoModel (object):

    def __init__(self):
        self.client = MongoClient ()
        self.db = self.client.g4d
        self.default_page_size = 5

    def add_flow (self, name):
        return self.db.flows.insert ({ 'name' : name })

    def list_flows (self, current_id, page, page_size):
        result = []
        page_size = page_size if page_size else self.default_page_size
        target_page = page * page_size
        
        query = None
        if current_id != '0':
            query = { "_id" : { "$gt" : ObjectId (current_id)} }

        cursor =  self.db.flows.find (query) if query else self.db.flows.find ()  #{ "_id" : { "$gt" : ObjectId (current_id)} })
        result = list (cursor.skip (target_page).limit (page_size).sort ("_id", pymongo.ASCENDING))
        count = len (result)
        def streamable (x):
            x['_id'] = str(x['_id'])
        map (streamable, result)
        return result

