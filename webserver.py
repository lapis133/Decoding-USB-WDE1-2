#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from http.server import BaseHTTPRequestHandler, HTTPServer
import log
import threading
import time

hsvr = None
fkt_gethtmltable = None
fkt_relstate = None
fkt_relupdate = None
fkt_led = None

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
        self.senddata(fkt_gethtmltable())
        if fkt_relstate() == 1:
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
        if fkt_relstate() == 1:
            fkt_relupdate(0)
        else:
            fkt_relupdate(1)
        self.resp_header()
        self.resp_page()

#----------------------------[serverthread]
def serverthread():
    global hsvr

    log.info("websvr", "init")
    fkt_led(0)

    # init server
    while True:
        try:
            hsvr = HTTPServer(("", 4711), RequestHandler)
            break
        except Exception:
            time.sleep(1)

    # running
    log.info("websvr", "started")
    fkt_led(1)
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
def start(fgethtmltable, frelstate, frelupdate, fled):
    global fkt_gethtmltable
    global fkt_relstate
    global fkt_relupdate
    global fkt_led

    fkt_gethtmltable = fgethtmltable
    fkt_relstate = frelstate
    fkt_relupdate = frelupdate
    fkt_led = fled
    thread = threading.Thread(target=serverthread, args=[])
    thread.start()
    return