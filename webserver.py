#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from http.server import BaseHTTPRequestHandler, HTTPServer
import gpio as GPIO
import log
import threading
import time

hsvr = None
gethtmltable = None
relstate = None
relupdate = None

#----------------------------[MyServer]
class RequestHandler(BaseHTTPRequestHandler):
    def resp_header(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def senddata(self, data):
        self.wfile.write(bytes(data, "utf-8"))

    def resp_page(self):
        self.senddata("<html>")
        self.senddata("<head><title>home temperature observation</title><meta http-equiv='refresh' content='5'></head>")
        self.senddata("<body><font face='verdana,arial'>")
        self.senddata("<p>{:s}</p>".format(time.strftime("%d-%m-%Y Time: %H:%M:%S",time.localtime())))
        self.senddata(gethtmltable())
        if relstate() == 1:
            self.senddata("<form action='' method='post'><button name='foo' value='upvote'>Heizung aus</button></form>")
        else:
            self.senddata("<form action='' method='post'><button name='foo' value='upvote'>Heizung ein</button></form>")
        self.senddata("</body>")

    def do_GET(self):
        log.info("websvr", "do_GET")
        self.resp_header()
        self.resp_page()

    def do_POST(self):
        global rel_state

        log.info("websvr", "do_POST")
        if relstate() == 1:
            relupdate(0)
        else:
            relupdate(1)
        self.resp_header()
        self.resp_page()

#----------------------------[serverthread]
def serverthread():
    global hsvr

    log.info("websvr", "init")
    GPIO.tcp_status(0)

    # init server
    while True:
        try:
            hsvr = HTTPServer(("", 4711), RequestHandler)
            break
        except Exception:
            GPIO.tcp_blink(0)
            time.sleep(1)

    # running
    log.info("websvr", "started")
    GPIO.tcp_status(1)
    try:
        hsvr.serve_forever()
    except KeyboardInterrupt:
        hsvr.server_close()
    log.info("websvr", "stop")
    return

#----------------------------[stop]
def stop():
    global hsvr
    if hsvr != None:
        hsvr.shutdown()

#----------------------------[start]
def start(gethtmltable_fkt, relstate_fkt, relupdate_fkt):
    global gethtmltable
    global relstate
    global relupdate

    gethtmltable = gethtmltable_fkt
    relstate = relstate_fkt
    relupdate = relupdate_fkt
    thread = threading.Thread(target=serverthread, args=[])
    thread.start()
    return
