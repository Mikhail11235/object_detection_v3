#!/usr/bin/python3
import pika
import time

is_continue = True
while is_continue:
    try:
        pika.BlockingConnection(pika.ConnectionParameters("0.0.0.0", 5672))
        is_continue = False
    except:
        time.sleep(1)

