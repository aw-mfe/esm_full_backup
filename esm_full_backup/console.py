# -*- coding: utf-8 -*-

import argparse
import sys
from configparser import ConfigParser, NoSectionError, MissingSectionHeaderError
from esm_full_backup.esm_full_backup import Config, ESM, dehexify
            
def main():
    config = Config()
    try:
        host = config.esmhost
    except AttributeError:
        print("Cannot find 'esmhost' key in .mfe_saw.ini")
        sys.exit(0)
    try:        
        user = config.esmuser
    except AttributeError:
        print("Cannot find 'esmuser' key in .mfe_saw.ini")
        sys.exit(0)
    try:        
        passwd = config.esmpass
    except AttributeError:
        print("Cannot find 'esmpass' key in .mfe_saw.ini")
        sys.exit(0)
    helpdoc = '''\
    usage: esm_full_backup -f

    Start Full Back up McAfee ESM
    
      -f, --full           Full backup
      -v, --version        Print version
      --help               Show this help message and exit'''
    
    if len(sys.argv) != 2:
    
        print(helpdoc)
        sys.exit(0)
    if sys.argv[1] == "-f":
        print('ESM backup initiated. The ESM will be inaccessible during this process and it may take a long time depending upon the volume of data in the database.')
        esm = ESM(host, user, passwd)
        esm.login()
        print(esm.start_full_backup())
            
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.warning("Control-C Pressed, stopping...")
        sys.exit()
