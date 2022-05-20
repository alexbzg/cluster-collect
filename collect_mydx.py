#!/usr/bin/python3
#coding=utf-8
import asyncio

from pymongo import MongoClient
import websockets

from common import siteConf, startLogging
from dx_spot import DX

CONF = siteConf()

MC = MongoClient(CONF['db']['host'],
        username=CONF['db']['user'],
        password=CONF['db']['password'],
        authSource='admin')

SRC_ID = 'mydx.eu'
DB = MC.dx

SRC_CONF = CONF[f"src:{SRC_ID}"]

async def ws_client():
    async for ws in websockets.connect(SRC_CONF['url']):
        try:
            async for message in ws:
                if message[0] == 'S':
                    _, time, freq, mode, cs, rda, _, _, _, autocfm = message.split(';')
                    item = DX(cs=cs, freq=freq, mode=mode, de='mydx.eu', time=time, 
                            rda=rda).to_dict()
                    txt_data = DB.dx.find_one({
                        'ts': {'$gt': item['ts'] - 5400},
                        'cs': item['cs'],
                        'freq': {
                            '$gt': item['freq'] - 1,
                            '$lt': item['freq'] + 1
                            },
                        'text': {
                            '$ne': ''
                            }
                        })
                    if txt_data:
                        item['text'] = txt_data['text']

                    DB.dx.delete_many({
                        'ts': {'$gt': item['ts'] - 5400},
                        'cs': item['cs'],
                        'freq': {
                            '$gt': item['freq'] - 1,
                            '$lt': item['freq'] + 1
                            }
                        })
                    DB.dx.insert_one(item)

        except websockets.ConnectionClosed:
            continue

asyncio.run(ws_client())
