import os
import time
import subprocess
import shutil

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
