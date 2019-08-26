#-*- coding: utf-8 -*-

from concurrent import futures
from threading import Thread
import os, sys, time, logging, grpc, datetime
sys.path.append(os.path.abspath(os.path.dirname(__file__)) + "/proto")

from client import start
from server import serve

if __name__ == '__main__':
    c = None
    try:
        logging.basicConfig()

        mode = input("choice running mode.\n[s] server mode.\n[c] client mode.\n> ")
        while True:
            if mode.upper() == 'S':
                print('Server mode select...')
                print("Server running...")
                serve()
                break 
            elif mode.upper() == 'C':
                print('Client mode select...')
                start()
                break
            else:
                mode = input("choice running mode.\n[s] server mode.\n[c] client mode.\n> ")

    except KeyboardInterrupt:
        print ("\nprogram stop...")
    except Exception as err:
        print("[main.py]", err)
        
        

