#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2010-2019 Denis Machard
# This file is part of the extensive automation project
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301 USA
# -------------------------------------------------------------------


import sys
import os
import signal
import subprocess
import json
import hashlib
from binascii import hexlify
import base64
import sqlite3
try:
    import cStringIO
except ImportError: # support python 3
    import io as cStringIO
try:
    import cPickle
except ImportError: # support python 3
    import pickle as cPickle

from Libs import  Settings, Logger
from Libs.FileModels import TestResult as TestResult

from ServerRepositories import ( RepoAdapters )

if Settings.instance() is None:                       
    Settings.initialize()


def querySQL ( query, db):
    """
    """
    try:
        conn = sqlite3.connect(db)
        
        c = conn.cursor()
        c.execute(query)
        c.close ()
        
        conn.commit()
        conn.close()
    except Exception as e:
        print("[query] %s - %s" % (str(e), query) )
        sys.exit(1)
 
db_name = "%s/%s/%s" % (   Settings.getDirExec(),
                            Settings.get( 'Paths', 'var' ),
                            Settings.get( 'Database', 'db' ))

def error(msg):
    """
    """
    print("ERROR: %s" % msg)
    
class CliFunctions(Logger.ClassLogger):
    """
    """
    def __init__(self, parent):
        """
        """
        self.parent=parent

    def version(self):
        """
        Get version of the server
        """
        sys.stdout.write( "Server version: %s\n" % Settings.getVersion())

    def installAdapter(self, name):
        """
        """
        RepoAdapters.initialize(context=None)
        
        folder_lib = "%s/%s/%s" % (Settings.getDirExec(), 
                                   Settings.get('Paths','packages-sutadapters'),
                                   name ) 
        if os.path.exists( folder_lib ):
            try:
                # install dependancies according to the plugin with pip
                pip_list = "%s/deps/pip_list.txt" % folder_lib
                if os.path.exists(pip_list) and os.path.getsize(pip_list) > 0:
                    cmd = "pip install -r %s" % pip_list
                    subprocess.call(cmd, shell=True)  
                    
                # system detect
                yum_list = "%s/deps/yum_list.txt" % folder_lib
                if os.path.exists(yum_list) and os.path.getsize(yum_list) > 0:
                    if os.path.exists( "/etc/os-release" ):
                        os_id = ""
                        with open("/etc/os-release") as f:
                            for line in f:
                                if "=" in line:
                                    k, v = line.rstrip().split("=")
                                    if k == "ID": 
                                        os_id = v.strip('"')
                                        break
                                        
                        if "centos" in os_id or "rhel" in os_id:
                            cmd = "yum install `cat %s | tr '\n' ' '`" % yum_list
                            subprocess.call(cmd, shell=True) 
                        
                    
                RepoAdapters.instance().updateMainInit()
                
                # install samples according to the plugin
                folder_sample = "%s/%s/1/Samples/Adapter_%s" % (Settings.getDirExec(), 
                                                Settings.get('Paths','tests'),
                                                name) 
                if not os.path.exists( folder_sample ):
                    os.mkdir( folder_sample, 0o755 )
                    
                cmd = 'cp -rf %s/samples/* %s' % (folder_lib,
                                                  folder_sample)
                subprocess.call(cmd, shell=True)
                
                print("Sut Adapter installation process terminated")
            except Exception as e:
                print("unable to install adapter: %s" % e)
            
        else:
            print("Sut Adapter (%s) not found!" % name)
            
        RepoAdapters.instance().updateMainInit()
        
    def decodeTrx(self, filename):
        """
        Decode a test result
        """
        doc = TestResult.DataModel()
        doc.error = error
        
        print("Reading the testresult...")
        res = doc.load( absPath = filename )
        if res: self.decodeTrxStats(tr=doc)
        
    def decodeTrxStats(self, tr):
        """
        """
        statisticsEvents = { 'nb-total': 0, 
                         'nb-info': 0, 
                         'nb-error': 0, 
                         'nb-warning': 0, 
                         'nb-debug': 0,
                         'nb-timer': 0, 
                         'nb-step': 0, 
                         'nb-adapter': 0, 
                         'nb-match': 0, 
                         'nb-section': 0,
                         'nb-others': 0, 
                         'nb-step-failed': 0, 
                         'nb-step-passed': 0 }
        errorsEvents = []
        try:
            f = cStringIO.StringIO( tr.testresult )
        except Exception as e:
            print( "unable to read test result.." )
        else:
            all = f.readlines()
            try:
                for line in all:
                    statisticsEvents["nb-total"] += 1
                    
                    l = base64.b64decode(line)
                    event = cPickle.loads( l )
                    
                    if "level" in event:
                        if event["level"] == "info": statisticsEvents["nb-info"] += 1
                        if event["level"] == "warning": statisticsEvents["nb-warning"] += 1
                        if event["level"] == "error": 
                            statisticsEvents["nb-error"] += 1
                            errorsEvents.append( event )
                        if event["level"] == "debug": statisticsEvents["nb-debug"] += 1
                    
                        if event["level"] in [ "send", "received" ]:  statisticsEvents["nb-adapter"] += 1
                        if event["level"].startswith("step"): statisticsEvents["nb-step"] += 1
                        if event["level"].startswith("timer"): statisticsEvents["nb-timer"] += 1
                        if event["level"].startswith("match"): statisticsEvents["nb-match"] += 1
                        if event["level"] == "section": statisticsEvents["nb-section"] += 1
                    else:
                        statisticsEvents["nb-others"] += 1
                        
            except Exception as e:
                print("unable to unpickle: %s" % e)
            else:
                self.displayTrxStats(statisticsEvents)
                self.displayTrxErrors(errorsEvents)
                
    def displayTrxErrors(self, errors):
        """
        """
        print("errors listing (%s):" % len(errors) )
        for err in errors:
            print( "\t%s - %s" % (err['timestamp'], err['short-msg']) )
            
    def displayTrxStats(self, stats):
        """
        """
        
        nbDebugPercent = 0
        nbInfoPercent = 0
        nbWarningPercent = 0
        nbErrorPercent = 0
        if stats["nb-total"]: nbDebugPercent = ( stats["nb-debug"] * 100 ) / stats["nb-total"]
        if stats["nb-total"]: nbInfoPercent = ( stats["nb-info"] * 100 ) / stats["nb-total"]
        if stats["nb-total"]: nbWarningPercent = ( stats["nb-warning"] * 100 ) / stats["nb-total"]
        if stats["nb-total"]: nbErrorPercent = ( stats["nb-error"] * 100 ) / stats["nb-total"]
            
        nbAdapterPercent = 0
        nbTimerPercent = 0
        nbStepPercent = 0
        nbMatchPercent = 0
        nbStepFailedPercent = 0
        nbStepPassedPercent = 0
        if stats["nb-total"]: nbAdapterPercent = ( stats["nb-adapter"] * 100 ) / stats["nb-total"]
        if stats["nb-total"]: nbTimerPercent = ( stats["nb-timer"] * 100 ) / stats["nb-total"]
        if stats["nb-total"]: nbStepPercent = ( stats["nb-step"] * 100 ) / stats["nb-total"]
        if stats["nb-total"]: nbStepFailedPercent = ( stats["nb-step-failed"] * 100 ) / stats["nb-total"]
        if stats["nb-total"]: nbStepPassedPercent = ( stats["nb-step-passed"] * 100 ) / stats["nb-total"]
        if stats["nb-total"]: nbMatchPercent = ( stats["nb-match"] * 100 ) / stats["nb-total"]
        
        nbSectionPercent = 0
        nbOthersPercent = 0
        if stats["nb-total"]: nbSectionPercent = ( stats["nb-section"] * 100 ) / stats["nb-total"]
        if stats["nb-total"]: nbOthersPercent = ( stats["nb-others"] * 100 ) / stats["nb-total"]
        
        print("statistics:")
        print("\ttotal events:\t\t%s\t\t(100%%)" % stats["nb-total"])
        print("")
        print("\tdebug events:\t\t%s\t\t(%.2f%%)" % (stats["nb-debug"], nbDebugPercent) )
        print("\tinfo events:\t\t%s\t\t(%.2f%%)" % (stats["nb-info"], nbInfoPercent) )
        print("\twarning events:\t\t%s\t\t(%.2f%%)" % (stats["nb-warning"], nbWarningPercent) )
        print("\terror events:\t\t%s\t\t(%.2f%%)" % (stats["nb-error"], nbErrorPercent) )
        print("")
        print("\tadapter events:\t\t%s\t\t(%.2f%%)" % (stats["nb-adapter"], nbAdapterPercent) )
        print("\ttimer events:\t\t%s\t\t(%.2f%%)" % (stats["nb-timer"], nbTimerPercent) )
        print("\tstep events:\t\t%s\t\t(%.2f%%)" % (stats["nb-step"], nbStepPercent) )
        print("\tmatch events:\t\t%s\t\t(%.2f%%)" % (stats["nb-match"], nbMatchPercent) )
        print("")
        print("\tsection events:\t\t%s\t\t(%.2f%%)" % (stats["nb-section"], nbSectionPercent) )
        print("\tothers events:\t\t%s\t\t(%.2f%%)" % (stats["nb-others"], nbOthersPercent) )
        print("")
    
    def generateKey(self, username, size=20):
        """
        Generate a key for the rest api
        """
        apikey_id = username
        apikey_secret = hexlify(os.urandom(size))
        
        querySQL( query = "UPDATE `users` SET apikey_id=\"%s\", apikey_secret=\"%s\" WHERE login=\"%s\"" % (username, 
                         apikey_secret,
                         username), db=db_name )
        
        print("API Key ID: %s" % apikey_id)
        print("API Key Secret: %s" % apikey_secret)
            
    def reload(self):
        """
        Reload configuration
        Send a signal to the process
        """
        sys.stdout.write( "Reloading configuration...\n")
        if not self.parent.status():
            sys.stdout.write( "Server not started...\n")
        else:
            pid = self.parent.getPid()
            if pid is not None:
                self.parent.sendSignal(pid, signal.SIGHUP)
                sys.stdout.write( "Configuration reloaded!\n" )
        
        sys.stdout.flush()
        
CLI = None # singleton
def instance ():
    """
    Returns the singleton

    @return: server singleton
    @rtype: object
    """
    return CLI

def initialize (parent):
    """
    Instance creation
    """
    global CLI
    CLI = CliFunctions(parent=parent) 

def finalize ():
    """
    Destruction of the singleton
    """
    global CLI
    if CLI: CLI = None