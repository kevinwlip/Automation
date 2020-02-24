#!/usr/bin/python


#  Author : Vinh Nguyen



from pymongo import MongoClient
import os, sys, re, logging


class Mongo(MongoClient):

    # constructor.  login to mongodb
    def __init__(self, host, uname, pword):
        uri = 'mongodb://'+uname+':'+pword+'@'+host
        self.client = MongoClient(uri)


    # function to insert into db
    #      or if seeing 'pattern' value, then update db
    def insert(self, db, col, v, p=None):
        self.db = self.client[db]
        self.col = self.db[col]

        if not p:
            post_id = self.col.insert(v)
        else:
            v = {'$push': v}
            post_id = self.col.update(p, v)
        logging.debug(post_id)


    # function to insert into db
    #      or if seeing 'pattern' value, then update db
    def replace(self, db, col, v, p):
        self.db = self.client[db]
        self.col = self.db[col]
        v = {'$set': v}
        
        post_id = self.col.update(p, v, upsert=True)
        logging.debug(post_id)   


    # function to query db
    #   Each entry found is a dictionary.  Put all entry (dictionary into list).  return list.
    #   If not found, return None.
    def query(self, db, col, p, r):
        list_dict = []
        self.db = self.client[db]
        self.col = self.db[col]

        #doc = self.col.find_one()
        for doc in self.col.find(p, r):
            list_dict.append(doc)
        
        if len(list_dict) > 0:
            return list_dict
        else:
            return None


    # function to remove a document
    def remove(self, db, col, p):
        self.db = self.client[db]
        self.col = self.db[col]
        post_id = self.col.remove(p)
        logging.debug(post_id)


    # destructor
    def __del__(self):
        self.client.disconnect()
        del self

