#!/bin/bash
sudo cp -n serialmon_01.ini /usr/local/etc 
sudo cp serialmon_01.py /usr/local/bin
sudo chmod +x /usr/local/bin/serialmon_01.py
sudo rm /var/log/serialmon_info.log
