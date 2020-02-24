"""
Copyright 2017, Zingbox, http://zingbox.com

Date: 8/24/2017 09:13:00

Author: Jeffrey LEE
"""
import os
import yaml
from pymongo import MongoClient

def load_config():
  """load_config function combine and return the configurations
    from default and az-testing configuration files.

    Confiuration from az-testing.yml will overwrite configurations
    in default.yml. update_config will do the overwrite job.

      :return: return conbined configurations dictionary
      :rtype: dict

  """
  def update_config(src, extra):
    for key in extra:
      #print key + " in update config extra"
      if key in src:
        #print type(extra[key])
        if type(extra[key]) == dict:
          update_config(src[key], extra[key])
        else:
          src[key] = extra[key]  
      else:
        src[key] = extra[key]

  config = {}
  dir_path = os.path.dirname(os.path.realpath(__file__))
  with open(dir_path + "/config/default.yml", 'r') as ymlfile:
    config = yaml.load(ymlfile)

  # AP-3364: We need to make sure user script only alter az-testing and staging env.
  # NO other options are allowed.
  node_env = os.environ['NODE_ENV']
  config_file_path = '/config/az-testing.yml'
  if 'staging' in node_env:
    config_file_path = '/config/staging.yml'
  with open(dir_path + config_file_path, 'r') as ymlfile:
    extra_config = yaml.load(ymlfile)
    update_config(config, extra_config)

  return config


def gen_mongo_uri(config):
  """gen_mongo_uri load mongo information from config dictionary provided.
    Return a valid mongo connection string for pymonogo to connect a db.

      :param config:
        configurations dictionary, typically created from load_config
      :type config: dict
      :return: return conbined configurations dictionary
      :rtype: dict

  """
  servers = config['mongo']['hosts']
  dbName = config['mongo']['dbName']
  user = config['mongo']['user']
  passwd = config['mongo']['pass']
  mongoStr = 'mongodb://';
  mongoStr += user + ':' + passwd + '@' + servers[0];
  for server in servers[1:]:
    mongoStr += ',' + server;
  mongoStr += '/' + dbName;
  if 'rsName' in config['mongo']:
      mongoStr += "?replicaSet=" + config['mongo']['rsName'];
  return mongoStr

# print config
# mongo_uri



class DB:
  """DB class is an abstraction on MongoClient to connect Zingcloud mongodb.
    It handles to configurations and connections of MongoClient by exposing
    getConnection() and closeConnection static methods.
  """
  __db = None
  @staticmethod
  def getConnection():
    """getConnection initialize one and only one MongoClient instance.
      It loads proper configuration and handles MongoClient connection uri.

        :return: return MongoClient instance connected to Zingcloud testing
          server xiar database.
        :rtype: pymongo.database.Database

    """
    if DB.__db is not None:
      return DB.__db.xiar
    else:
      print("initializing")
      config = load_config()
      mongo_uri = gen_mongo_uri(config)
      print("mongo server:"+mongo_uri)
      DB.__db = MongoClient(mongo_uri)
      return DB.__db.xiar

  @staticmethod
  def closeConnection():
    """closeConnection terminates a database connection to safe resources.
    """
    if DB.__db is not None:
      DB.__db.close()

#db = DB.getConnection()

