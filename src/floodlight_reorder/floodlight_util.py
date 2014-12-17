import os
import time
import subprocess
import shutil
import json

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
FLOODLIGHT_JAR = os.path.join(
    FILE_DIR,'..','..','external_bins','floodlight.jar')

SYNCDB_FLOODLIGHT_DIR = os.path.join('/','var','lib','floodlight','SyncDB')

def _destroy_syncdb_dir():
    if os.path.exists(SYNCDB_FLOODLIGHT_DIR):
        shutil.rmtree(SYNCDB_FLOODLIGHT_DIR)

def start_floodlight():
    '''
    Begins executing floodlight and waits until floodlight is stable
    before returning.
    '''
    _destroy_syncdb_dir()
    dev_null_fd = open(os.devnull,'wb')
    cmd_vec = ['sudo','java','-ea','-jar',FLOODLIGHT_JAR]
    p = subprocess.Popen(
        cmd_vec,stdout=dev_null_fd,stderr=subprocess.STDOUT)

    # wait some time for floodlight to get settled
    time.sleep(5)

    
def add_flowmod():
    flow_entry_dict = {
        'switch': '00:00:00:00:00:00:00:01',
        'name': 'flow-mod-1',
        'cookie': '0',
        'priority': '32768',
        'ingress-port': '1',
        'active': 'true',
        'actions': 'output=2'
        }
    
    cmd_vec = [
        'curl','-d',json.dumps(flow_entry_dict),
        'http://127.0.0.1:8080/wm/staticflowentrypusher/json']
    subprocess.call(cmd_vec)
