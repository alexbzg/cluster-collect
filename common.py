#!/usr/bin/python3
#coding=utf-8

import configparser, logging, logging.handlers, os
from os import path

appRoot = path.dirname( path.abspath( __file__ ) ) 

def siteConf():
    conf = configparser.ConfigParser()
    conf.optionxform = str
    conf.read( appRoot + '/site.conf' )
    return conf

def readConf( file ):
    conf = configparser.ConfigParser()
    conf.read( appRoot + '/' + file )
    return conf

def startLogging( type, level = logging.DEBUG ):
    conf = siteConf()
    fpLog = conf.get( 'logs', type ) 
    logger = logging.getLogger('')
    logger.setLevel( level )
    loggerHandler = logging.handlers.WatchedFileHandler( fpLog )
    loggerHandler.setLevel( level )
    loggerHandler.setFormatter( logging.Formatter( \
        '%(asctime)s %(name)-12s %(levelname)-8s %(message)s' ) )
    logger.addHandler( loggerHandler )

