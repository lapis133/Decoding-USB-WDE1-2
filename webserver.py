#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
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

#----------------------------[readlog]
def readlog(filename):
    log = ""
    try:
        f = open("/var/log/{:s}".format(filename),"r")
    except Exception:
        try:
            f = open(filename,"r")
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

    def resp_page(self, filename):
        html = "<!docstype html>"
        html += "<html lang='de'>"
        html += "<head>"
        html += "<meta charset='UTF-8'>"
        html += "<meta name='viewport' content='width=device-width, initial-scale=1'>"
        html += "<title>home temperature observation</title>"
        if filename == "":
            html += "<meta http-equiv='refresh' content='5'>"
        html += "<link rel='stylesheet' href='https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css' integrity='sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm' crossorigin='anonymous'>"
        html += "<link rel='stylesheet' href='https://use.fontawesome.com/releases/v5.1.1/css/all.css' integrity='sha384-O8whS3fhG2OnA5Kas0Y9l3cfpmYjapjI0E4theH4iuMD+pLhbf6JI0jIMfYcK3yZ' crossorigin='anonymous'>"
        #html += "<link rel='stylesheet' href='https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css' integrity='sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u' crossorigin='anonymous'>"
        html += "</head>"
        html += "<body>"
        html += "<div class='container'>"
        html += "<main>"
        if filename == "":
            html += "<h2><i class='fas fa-home'></i> &Uuml;bersicht</h2>"
            html += "<p>{:s}</p>".format(time.strftime("%d-%m-%Y Time: %H:%M:%S",time.localtime()))
            html += fkt_gethtmltable(False)
            html += "<form action='' method='post'>"
            html += "<button type='submit' class='btn tn-outline-secondary btn-sm' name='relstate'>"
            if fkt_relstate() == 1:
                html += "Heizung ausschalten <i class='fas fa-ban'></i>"
            else:
                html += "Heizung einschalten <i class='fas fa-fire'></i>"
            html += "</button>"
            html += "</form>"
            html += "<hr>"
            html += "<form action='' method='post'><button type='submit' class='btn btn-primary btn-sm' name='logtemp'>Temperaturaufzeichnung <i class='fas fa-caret-right'></i></button></form>"
            html += "<form action='' method='post'><button type='submit' class='btn btn-primary btn-sm' name='logsys'>Systemlog <i class='fas fa-caret-right'></i></button></form>"
        else:
            html += "<h2><i class='fas fa-file'></i> Logfile {:s}</h2>".format(filename)
            html += "<form action='' method='post'><button type='submit' class='btn btn-primary btn-sm' name='main'><i class='fas fa-caret-left'></i> &Uuml;bersicht</button></form>"
            html += "<p><pre>"
            html += readlog(filename)
            html += "</pre></p>"
            html += "<form action='' method='post'><button type='submit' class='btn btn-primary btn-sm' name='main'><i class='fas fa-caret-left'></i> &Uuml;bersicht</button></form>"
        html += "</main>"
        html += "</div>"
        html += "</body>"
        html += "</html>"
        self.senddata(html)

    def do_GET2(self):
        self.resp_header()
        if   self.path == "/":
            self.resp_page("")
        elif self.path == "/logtemp":
            self.resp_page("serialmon_01.log")
        elif self.path == "/logsys":
            self.resp_page("serialmon_info.log")

    def do_GET(self):
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

        self.resp_header()
        if val.find("relstate=") != -1:
            log.info("websvr", "do_POST: {:s}".format(val))
            if fkt_relstate() == 1:
                fkt_relupdate(0)
            else:
                fkt_relupdate(1)
            self.resp_page("")
        elif val.find ("logtemp=") != -1:
            self.resp_page("serialmon_01.log")
        elif val.find ("logsys=") != -1:
            self.resp_page("serialmon_info.log")
        else:
            self.resp_page("")

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
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """ This class allows to handle requests in separated threads.
        No further content needed, don't touch this. """

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
            hsvr = ThreadedHTTPServer(("", 4711), RequestHandler)
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
