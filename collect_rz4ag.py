#!/usr/bin/python3
#coding=utf-8
import asyncio
from datetime import datetime
import time

from pymongo import MongoClient
import socketio

from common import siteConf

CONF = siteConf()

MC = MongoClient(CONF['db']['host'],
        username=CONF['db']['user'],
        password=CONF['db']['password'],
        authSource='admin')

SRC_ID = 'rz4ag'
DB = MC.dx

BANDS = [
            ['1.8', 1800, 2000],
            ['3.5', 3500, 4000],
            ['7', 7000, 7300],
            ['10', 1000, 10150],
            ['14', 14000, 14350],
            ['18', 18068, 18168],
            ['21', 21000, 21450],
            ['24', 24890, 24990],
            ['28', 28000, 29700],
            ['50', 50000, 54000],
            ['144', 144000, 148000],
            ['UHF', 150000, 2000000]
        ]

SRC_CONF = CONF[f"src:{SRC_ID}"]

sio = socketio.AsyncClient()

@sio.event
async def new_spot(data):
    _, time_s, freq, mode, cs, rda, _, txt, de = data.split('|')
    if len(time_s) == 5:
        time_s = datetime.utcnow().date().strftime("%Y-%m-%d") + f" {time_s}:00"
    ts = time.mktime(datetime.strptime(time_s, "%Y-%m-%d %H:%M:%S").timetuple())
    if ts > time.time():
        ts -= 86400

    qrp = False
    if '/QRP' in cs:
        cs = cs.replace( '/QRP', '' )
        qrp = True

    band = None
    if freq:
        freq = float(freq)
        for diap in BANDS:
            if diap[1] <= freq <= diap[2]:
                band = diap[0]
                break
            if diap[1] > freq:
                break


    item = {
            'cs': cs,
            'qrp': qrp,
            'text': txt,
            'de': de,
            'freq': float(freq),
            'dt': time_s,
            'ts': ts,
            'time': time_s[11:16],
            'band': band,
            'mode': mode,
            'rda': rda
            }

    DB.dx.delete_many({
        'ts': {'$gt': item['ts'] - 5400},
        'cs': item['cs'],
        'freq': {
            '$gt': item['freq'] - 1,
            '$lt': item['freq'] + 1
            }
        })
    DB.dx.insert_one(item)

async def main():
    await sio.connect(SRC_CONF['url'])
    await sio.wait()

asyncio.run(main())
