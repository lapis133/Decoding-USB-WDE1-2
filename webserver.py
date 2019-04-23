#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import configparser
import datetime
import log
import threading
import time
import base64
import ssl

s_hsvr = None
s_key  = ""
fkt_gethtmltable = None
fkt_relstate     = None
fkt_relupdate    = None
fkt_led          = None

FAVICON = b"AAABAAEAEBAAAAEAIABoBAAAFgAAACgAAAAQAAAAIAAAAAEAIAAAAAAAAAQAAB\
            ILAAASCwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\
            AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAjAA\
            AATQAAAE0AAABNAAAAOAAAAAAAAAAAAAAAOAAAAE0AAABNAAAATQAAACMAAAAA\
            AAAAAAAAAAAAAAAAAAAAtAAAAP8AAAD/AAAA/wAAALoAAAAAAAAAAAAAALoAAA\
            D/AAAA/wAAAP8AAAC0AAAAAAAAAAAAAAAAAAAAAAAAALcAAAD/AAAA/wAAAP8A\
            AAC6AAAAAAAAAAAAAAC6AAAA/wAAAP8AAAD/AAAAtwAAAAAAAAAAAAAAAAAAAA\
            AAAAC3AAAA/wAAAP8AAAD/AAAAugAAAAAAAAAAAAAAugAAAP8AAAD/AAAA/wAA\
            ALcAAAAAAAAAAAAAAAAAAAAAAAAAtwAAAP8AAAD/AAAA/wAAANwAAAB/AAAAfw\
            AAANwAAAD/AAAA/wAAAP8AAAC3AAAAAAAAAAAAAAAEAAAAAgAAALcAAAD/AAAA\
            /wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAtwAAAAIAAAAEAA\
            AAsAAAAK8AAABbAAAA8wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/\
            AAAA8wAAAFsAAACvAAAAsAAAAIkAAAD+AAAA0AAAAE8AAADfAAAA/wAAAP8AAA\
            D/AAAA/wAAAP8AAAD/AAAA3wAAAE8AAADQAAAA/gAAAIkAAAAAAAAAXwAAAPgA\
            AADoAAAAUAAAAMIAAAD/AAAA/wAAAP8AAAD/AAAAwgAAAFEAAADoAAAA+AAAAF\
            8AAAAAAAAAAAAAAAAAAAA7AAAA6AAAAPcAAABlAAAAmwAAAP8AAAD/AAAAmwAA\
            AGUAAAD3AAAA/wAAALcAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAAADRAAAA/g\
            AAAIkAAABwAAAAcAAAAIkAAAD+AAAA/wAAAP8AAAC3AAAAAAAAAAAAAAAAAAAA\
            AAAAAAAAAAAAAAAADQAAAK8AAAD/AAAAsQAAALEAAAD/AAAArgAAANwAAAD/AA\
            AAtwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAAAhwAAAP4AAAD+\
            AAAAhwAAAAIAAADSAAAA/wAAALcAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\
            AAAAAAAAAAAAAAAABDAAAAQwAAAAAAAAAAAAAASgAAAGAAAABAAAAAAAAAAAAA\
            AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\
            AAAAAAAAAAAAAAAAAAAAAA//8AAMGDAADBgwAAwYMAAMGDAADAAwAAAAAAAAAA\
            AAAAAAAAAAAAAMADAADgAwAA8AMAAPgDAAD8IwAA//8AAA=="

#----------------------------[preparechart]
def preparechart():
    return "\
<script type='text/javascript' src='https://www.gstatic.com/charts/loader.js'></script>\r\n\
<script type='text/javascript'>\r\n\
    google.charts.load('current', {'packages':['corechart']});\r\n\
    google.charts.setOnLoadCallback(drawChart);\r\n\
    function drawChart() {\r\n\
    var data = google.visualization.arrayToDataTable([\r\n\
        ['Datum', 'Temperatur'],\r\n\
        *DATA*\r\n\
    ]);\r\n\
    \r\n\
    var options = {\r\n\
        title: 'Temperaturverlauf',\r\n\
        curveType: 'function',\r\n\
        legend: { position: 'none' },\r\n\
        hAxis: { textPosition: 'none' }\r\n\
    };\r\n\
    \r\n\
    var chart = new google.visualization.LineChart(document.getElementById('curve_chart'));\r\n\
    chart.draw(data, options);\r\n\
    }\r\n\
</script>\r\n"

#----------------------------[readlog]
def readlog(filename, compareidx):
    log = ""
    try:
        f = open("/var/log/{:s}".format(filename),"r")
    except Exception:
        try:
            f = open(filename,"r")
        except Exception:
            return "no log found", ""

    if compareidx > 0:
        js = preparechart()
    else:
        js = ""
    data = ""
    ctime = datetime.datetime.today() - datetime.timedelta(days=15)

    while True:
        rl = f.readline()
        if not rl:
            break
        line = str(rl)

        if compareidx > 0:
            try:
                date = datetime.datetime.strptime(line[:10], "%d.%m.%Y")
                if date < ctime:
                    continue
            except Exception:
                pass

            values = line.split(";")
            try:
                tval = values[0]
                temp = values[compareidx]
                humi = values[compareidx+10]
                log += "{:s} {:>5s} &deg;C {:>5s} %<br>".format(tval, temp, humi)
                try:
                    x = float(temp)
                    data += "['{:s}', {:s}],\r\n".format(tval[:16], temp)
                except:
                    pass
            except Exception:
                log += "-<br>"
        else:
            log += line.replace('\n', "<br>")

    log   = log.replace("<br><br>", "<br>")
    data  = data.strip(',\r\n')
    data += "\r\n"
    js    = js.replace("*DATA*", data)
    return log, js

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

    def resp_location(self, path):
        self.send_response(302)
        self.send_header('Location', path)
        self.end_headers()

    def senddata(self, data):
        self.wfile.write(bytes(data, "utf-8"))

    def resp_page(self, filename, compareidx):
        html = "<!docstype html>\r\n"
        html += "<html lang='de'>\r\n"
        html += "<head>\r\n"
        html += "<meta charset='UTF-8'>\r\n"
        html += "<meta name='viewport' content='width=device-width, initial-scale=1'>\r\n"
        html += "<title>home temperature observation</title>\r\n"
        if filename == "":
            html += "<meta http-equiv='refresh' content='5'>\r\n"
        else:
            hlog, hjs = readlog(filename, compareidx)
            if compareidx > 0:
                html += hjs
        html += "<link rel='stylesheet' href='https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css' integrity='sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm' crossorigin='anonymous'>\r\n"
        html += "<link rel='stylesheet' href='https://use.fontawesome.com/releases/v5.1.1/css/all.css' integrity='sha384-O8whS3fhG2OnA5Kas0Y9l3cfpmYjapjI0E4theH4iuMD+pLhbf6JI0jIMfYcK3yZ' crossorigin='anonymous'>\r\n"
        html += "</head>\r\n"
        html += "<body>\r\n"
        html += "<div class='container'>\r\n"
        html += "<main>\r\n"
        if filename == "":
            html += "<h2><i class='fas fa-home'></i> &Uuml;bersicht</h2>"
            html += "<p>{:s}</p>".format(time.strftime("%d-%m-%Y Time: %H:%M:%S",time.localtime()))
            html += "<hr>"
            html += fkt_gethtmltable(False)
            html += "<form action='' method='post'>"
            if fkt_relstate():
                html += "<button type='submit' class='btn tn-outline-secondary btn-sm' name='rel0'>"
                html += "Heizung ausschalten <i class='fas fa-ban'></i>"
                html += "</button>"
            else:
                html += "<button type='submit' class='btn tn-outline-secondary btn-sm' name='rel1'>"
                html += "Heizung für eine Stunde einschalten <i class='fas fa-stopwatch'></i>"
                html += "</button>"
                html += "<br><br>"
                html += "<button type='submit' class='btn tn-outline-secondary btn-sm' name='rel2'>"
                html += "Heizung dauerhaft einschalten <i class='fas fa-fire'></i>"
                html += "</button>"
            html += "</form>"
            html += "<hr>"
            html += "<form action='' method='post'><button type='submit' class='btn btn-primary btn-sm' name='logfiles'>Aufzeichnungen <i class='fas fa-caret-right'></i></button></form>"
        elif filename == "logfiles":
            html += "<h2><i class='fas fa-copy'></i> Aufzeichnungen</h2>"
            html += "<form action='' method='post'><button type='submit' class='btn btn-primary btn-sm' name='main'><i class='fas fa-caret-left'></i> &Uuml;bersicht</button></form>"
            html += "<hr>"
            html += "Temperatur<br>"
            html += "<form action='' method='post'>"
            html += "<div class='btn-group-vertical'>"
            html += "<button type='submit' class='btn btn-info btn-lg' name='log1'>Obergescho&szlig;</button></form>"
            html += "<button type='submit' class='btn btn-outline-info btn-lg' name='log2'>Halle</button></form>"
            html += "<button type='submit' class='btn btn-info btn-lg' name='log3'>Schlafzimmer</button></form>"
            html += "<button type='submit' class='btn btn-outline-info btn-lg' name='log4'>Toilette</button></form>"
            html += "<button type='submit' class='btn btn-info btn-lg' name='log5'>Badezimmer</button></form>"
            html += "<button type='submit' class='btn btn-outline-info btn-lg' name='log6'>K&uuml;che</button></form>"
            html += "<button type='submit' class='btn btn-info btn-lg' name='log7'>Heizung</button></form>"
            html += "<button type='submit' class='btn btn-outline-info btn-lg' name='log8'>B&uuml;ro</button></form>"
            html += "<button type='submit' class='btn btn-info btn-lg' name='log9'>Au&szlig;en</button>"
            html += "<button type='submit' class='btn btn-outline-info btn-lg' name='log10'>Vorlauf</button></form>"
            html += "</div>"
            html += "</form>"
            html += "<hr>"
            html += "Logfiles<br>"
            html += "<form action='' method='post'>"
            html += "<div class='btn-group-vertical'>"
            html += "<button type='submit' class='btn btn-secondary btn-lg' name='log0'>Temperatur</button></form>"
            html += "<button type='submit' class='btn btn-outline-secondary btn-lg' name='logsys'>System</button></form>"
            html += "</div>"
            html += "</form>"
        else:
            if compareidx == 0:
                html += "<h2><i class='fas fa-file'></i> {:s}</h2>".format(filename)
            else:
                if   compareidx == 1:
                    name = "Obergescho&szlig;"
                elif compareidx == 2:
                    name = "Halle"
                elif compareidx == 3:
                    name = "Schlafzimmer"
                elif compareidx == 4:
                    name = "Toilette"
                elif compareidx == 5:
                    name = "Badezimmer"
                elif compareidx == 6:
                    name = "K&uuml;che"
                elif compareidx == 7:
                    name = "Heizung"
                elif compareidx == 8:
                    name = "B&uuml;ro"
                elif compareidx == 9:
                    name = "Au&szlig;en"
                elif compareidx == 10:
                    name = "Heizung"
                else:
                    name = "Aufzeichnung"
                html += "<h2><i class='fas fa-file-medical-alt'></i> {:s}</h2>".format(name)
            html += "<form action='' method='post'><button type='submit' class='btn btn-primary btn-sm' name='logfiles'><i class='fas fa-caret-left'></i> Zur&uuml;ck</button></form>"
            if compareidx > 0:
                html += "<div id='curve_chart' style='width: 600px; height: 300px'></div>"
            html += "<p><pre>"
            html += hlog
            html += "</pre></p>"
            html += "<form action='' method='post'><button type='submit' class='btn btn-primary btn-sm' name='logfiles'><i class='fas fa-caret-left'></i> Zur&uuml;ck</button></form>"
        html += "\r\n</main>\r\n"
        html += "</div>\r\n"
        html += "</body>\r\n"
        html += "</html>\r\n"
        self.senddata(html)

    def do_GET2(self):
        if self.path == "/favicon.ico":
            self.send_response(200)
            self.send_header('Content-type', 'image/gif')
            self.end_headers()
            self.wfile.write(base64.b64decode(FAVICON))
        else:
            path = str(self.path)
            self.resp_header()
            if self.path == "/logfiles":
                self.resp_page("logfiles", 0)
            elif self.path == "/logsys":
                self.resp_page("serialmon_info_{:s}.log".format(time.strftime("%Y-%m")), 0)
            elif path[:4] == "/log" and len(path) >= 5:
                self.resp_page("serialmon_01.log", int(path[4:]))
            else:
                self.resp_page("", 0)

    def do_GET(self):
        global s_key
        if s_key == "":
            self.do_GET2()
        else:
            if self.headers.get('Authorization') == None:
                self.resp_auth()
                self.senddata("no auth header received")
                pass
            elif self.headers.get('Authorization') == "Basic "+s_key:
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
        if val.find("rel") == 2:
            log.info("websvr", "do_POST: {:s}".format(val))
            fkt_relupdate(int(val[2+3]))
            self.resp_location("/")
        elif val.find ("logfiles=") == 2:
            self.resp_location("/logfiles")
        elif val.find ("logsys=") == 2:
            self.resp_location("/logsys")
        else:
            pos = val.find("log")
            if pos == 2:
                log.info("websvr", "get {:s} [{:s}]".format(val, self.address_string()))
                po2 = val.find("=")
                if po2 != -1:
                    self.resp_location(val[2:po2])
                    return
            self.resp_location("/")

    def do_POST(self):
        global s_key
        if s_key == "":
            self.do_POST2()
        else:
            if self.headers.get('Authorization') == None:
                self.resp_auth()
                self.senddata("no auth header received")
                pass
            elif self.headers.get('Authorization') == "Basic "+s_key:
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
    global s_hsvr
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
            s_hsvr = ThreadedHTTPServer(("", 4711), RequestHandler)
        except Exception:
            time.sleep(1)

        try:
            f = open("/usr/local/etc/serialmon_01.pem","r")
            f.close()
            try:
                s_hsvr.socket = ssl.wrap_socket(s_hsvr.socket, server_side=True, certfile="/usr/local/etc/serialmon_01.pem", ssl_version=ssl.PROTOCOL_TLSv1)
                break
            except Exception as e:
                print (str(e))
                s_hsvr.server_close()
                time.sleep(1)
        except Exception:
            log.info("websvr", "https is disabled")
            break

    # running
    log.info("websvr", "started")
    fkt_led(1)
    try:
        s_hsvr.serve_forever()
    except KeyboardInterrupt:
        s_hsvr.server_close()
    log.info("websvr", "stop")
    return

#----------------------------[stop]
def stop():
    global s_hsvr
    if s_hsvr != None:
        s_hsvr.shutdown()
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
