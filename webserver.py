#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from http.server import BaseHTTPRequestHandler, HTTPServer
import configparser
import log
import threading
import time
import base64
import ssl

hsvr = None
fkt_gethtmltable = None
fkt_relstate = None
fkt_relupdate = None
fkt_led = None

key = ""

#----------------------------[serverthread]
def readlog():
    log = ""
    try:
        f = open("/var/log/serialmon_01.log","r")
    except Exception:
        try:
            f = open("serialmon_01.log","r")
        except Exception:
            return "no log found"

    while True:
        rl = f.readline()
        if not rl:
            break;
        line = str(rl)
        log += line.replace('\n', "<br>")

    return log

#----------------------------[MyServer]
class RequestHandler(BaseHTTPRequestHandler):
    def resp_header(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def resp_auth(self):
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm=\"Test\"')
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def senddata(self, data):
        self.wfile.write(bytes(data, "utf-8"))

    def resp_page(self, logflag):
        if logflag == 0:
            self.senddata("<html>")
            self.senddata("<head><title>home temperature observation</title><meta http-equiv='refresh' content='5'></head>")
            self.senddata("<body><font face='verdana,arial'>")
            self.senddata("<p>{:s}</p>".format(time.strftime("%d-%m-%Y Time: %H:%M:%S",time.localtime())))
            self.senddata(fkt_gethtmltable())
            if fkt_relstate() == 1:
                self.senddata("<form action='' method='post'><button name='relstate'>Heizung aus</button></form>")
            else:
                self.senddata("<form action='' method='post'><button name='relstate'>Heizung ein</button></form>")
            self.senddata("<form action='' method='post'><button name='log'>Logfile</button></form>")
            self.senddata("</body>")
        else:
            self.senddata("<html>")
            self.senddata("<head><title>home temperature observation</title></head>")
            self.senddata("<body><font face='verdana,arial'>")
            self.senddata("<p>{:s}</p><tt>".format(time.strftime("%d-%m-%Y Time: %H:%M:%S",time.localtime())))
            self.senddata(readlog())
            self.senddata("</tt></body>")

    def do_GET2(self):
        log.info("websvr", "do_GET")
        self.resp_header()
        if   self.path == "/":
            self.resp_page(0)
        elif self.path == "/log":
            self.resp_page(1)

    def do_GET(self):
        log.info("websvr", "do_GET")
        global key
        if key == "":
            self.do_GET2()
        else:
            if self.headers.get('Authorization') == None:
                self.resp_auth()
                self.senddata("no auth header received")
                pass
            elif self.headers.get('Authorization') == "Basic "+key:
                self.do_GET2()
                pass
            else:
                self.resp_auth()
                self.senddata("not authenticated")
                pass

    def do_POST2(self):
        content_length = self.headers.get('content-length')
        length = int(content_length[0]) if content_length else 0
        val = str(self.rfile.read(length))

        log.info("websvr", "do_POST: {:s}".format(val))
        self.resp_header()
        if val.find("relstate") != -1:
            if fkt_relstate() == 1:
                fkt_relupdate(0)
            else:
                fkt_relupdate(1)
            self.resp_page(0)
        elif val.find ("log") != -1:
            self.resp_page(1)

    def do_POST(self):
        global key
        if key == "":
            self.do_POST2()
        else:
            if self.headers.get('Authorization') == None:
                self.resp_auth()
                self.senddata("no auth header received")
                pass
            elif self.headers.get('Authorization') == "Basic "+key:
                self.do_POST2()
                pass
            else:
                self.resp_auth()
                self.senddata("not authenticated")
                pass

#----------------------------[serverthread]
def serverthread():
    global hsvr
    global key

    log.info("websvr", "init")
    fkt_led(0)

    # init server
    config = configparser.ConfigParser()
    config.read('/usr/local/etc/serialmon_01.ini')
    try:
        user  = config["WEBSERVER"]["USER"]
        pasw  = config["WEBSERVER"]["PASSWORD"]
    except KeyError:
        user  = ""
        pasw  = ""
        log.info("websvr", "serialmon_01.ini not filled")

    # authentication
    phrase = user + ":" + pasw
    if len(phrase) > 1:
        key = str(base64.b64encode(bytes(phrase, "utf-8")), "utf-8")
    else:
        log.info("websvr", "authentication is disabled")

    # start
    while True:
        try:
            hsvr = HTTPServer(("", 4711), RequestHandler)
        except Exception:
            time.sleep(1)

        try:
            f = open("/usr/local/etc/serialmon_01.pem","r")
            f.close()
            try:
                hsvr.socket = ssl.wrap_socket(hsvr.socket, server_side=True, certfile="/usr/local/etc/serialmon_01.pem", ssl_version=ssl.PROTOCOL_TLSv1)
                break
            except Exception as e:
                print (str(e))
                hsvr.server_close()
                time.sleep(1)
        except Exception:
            log.info("websvr", "https is disabled")
            break

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
    return

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
