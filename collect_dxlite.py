#!/usr/bin/python3
#coding=utf-8
import sys

from pymongo import MongoClient
import requests
import xmltodict

from common import siteConf, startLogging
from dx_spot import DX, DXData

CONF = siteConf()

MC = MongoClient(CONF['db']['host'],
        username=CONF['db']['user'],
        password=CONF['db']['password'],
        authSource='admin')

SRC_ID = sys.argv[1]
DB = MC.dx

DXCC_RU = set(['54', '126', '15'])

SRC_CONF = CONF[f"src:{SRC_ID}"]
IS_SKIMMER = SRC_CONF.getboolean('skimmer')
rsp = requests.get(SRC_CONF['url'])
data = xmltodict.parse(rsp.text)['spots']['spot']
dx_data = DXData(reverse_order=True)
last_id = DB.src.find_one({'id': SRC_ID})['last']
for dx in data:
    if dx['@id'] != last_id:
        if IS_SKIMMER:
            dx['spotter'] += '-#'
        dx_data.append(DX(cs=dx['dx'], freq=dx['frequency'], de=dx['spotter'], time=dx['time'],
                text=dx['comment'], id=dx['@id'], dxcc=dx['dxcc']))
    else:
        break
if dx_data.data:
    for item in dx_data.data:
        if item['dxcc'] in DXCC_RU:
            rda_data = DB.dx.find_one({'cs': item['cs'], 'rda': {'$nin': [None, '?']}})
            if rda_data:
                item['rda'] = rda_data['rda']
        DB.dx.delete_many({
            'ts': {'$gt': item['ts'] - 5400}, 
            'cs': item['cs'], 
            'freq': {
                '$gt': item['freq'] - 1,
                '$lt': item['freq'] + 1
                }
            })
    DB.dx.insert_many(dx_data.data)
    DB.src.update_one({'id': SRC_ID}, {'$set': {'last': data[0]['@id']}})

