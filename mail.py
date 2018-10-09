#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import configparser
import log
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

#----------------------------[send]
def send(htmltable):
    # read config
    config = configparser.ConfigParser()
    config.read('/usr/local/etc/serialmon_01.ini')
    try:
        host  = config["EMAIL"]["SMPT_HOST"]
        port  = config["EMAIL"]["SMPT_PORT"]
        email = config["EMAIL"]["SMPT_EMAIL"]
        passw = config["EMAIL"]["SMPT_PASSWORD"]
        dest  = config["EMAIL"]["DESTINATION_EMAIL"]
    except KeyError:
        log.info("mail", "serialmon_01.ini not filled")
        return

    # email login
    try:
        s = smtplib.SMTP(host, port)
        s.starttls()
        s.login(email, passw)
    except Exception as e:
        log.info("mail", "SMTP error: " + str(e))
        return

    # prepare email
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "home temperature observation status"
    msg['From'] = email
    msg['To'] = dest

    html = """
    <head></head>
    <body>
        %s
    </body>
    """ % htmltable
    msg.attach(MIMEText(html, 'html'))

    # send email
    try:
        s.sendmail(email, dest, msg.as_string())
        s.quit()
        log.info("mail", "email send")
    except Exception as e:
        log.info("mail", "SMTP error:" + str(e))

    return
