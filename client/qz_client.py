#!/usr/bin/env python3

import sys
import socket
import selectors
import traceback

import qz_message
import threading

sel = selectors.DefaultSelector()



def create_request(action, value):
    if action == "search":
        return dict(
            type="text/json",
            encoding="utf-8",
            content=dict(action=action, value=value),
        )
    else:
        return dict(
            type="binary/custom-client-binary-type",
            encoding="binary",
            content=bytes(action + value, encoding="utf-8"),
        )


def start_connection(host, port, request, callback):
    addr = (host, port)
    print("starting connection to", addr)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(addr)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    message = qz_message.QZMessage(sel, sock, addr, request, callback)
    sel.register(sock, events, data=message)

    return message

host, port = '127.0.0.1', 65432


def start_quiz(keyword, callback):
    action, value = 'search', keyword
    request = create_request(action, value)
    message = start_connection(host, port, request, callback)
    return message


def run():
    start_quiz('ss', lambda x: print('callback'))

    try:
        while True:
            events = sel.select(timeout=1)
            for key, mask in events:
                message = key.data
                try:
                    print('main try')
                    print(mask)
                    message.process_events(mask)
                    print('main post')
                except Exception:
                    print(
                        "main: error: exception for",
                        f"{message.addr}:\n{traceback.format_exc()}",
                    )
                    message.close()
            # Check for a socket being monitored to continue.
            if not sel.get_map():
                break
    except KeyboardInterrupt:
        print("caught keyboard interrupt, exiting")
    finally:
        sel.close()

threading.Thread(target=run).start()


if __name__ == '__main__':
    run()