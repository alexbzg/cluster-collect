#!/usr/bin/python3
#coding=utf-8
import time

from pymongo import MongoClient

from common import siteConf, startLogging

CONF = siteConf()

MC = MongoClient(CONF['db']['host'],
        username=CONF['db']['user'],
        password=CONF['db']['password'],
        authSource='admin')

DB = MC.dx
ts = time.time() - 3600*24

DB.dx.delete_many({'ts': {'$lt': ts}})
