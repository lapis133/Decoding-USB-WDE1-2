#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pickle

#----------------------------[read]
def read():
    array = [ "?", "?", "?", "?"]
    try:
        with open ("/usr/local/etc/serialmon_01.pic", 'rb') as fp:
            array = pickle.load(fp)
        return array
    except Exception:
        pass

    try:
        with open ("serialmon_01.pic", 'rb') as fp:
            array = pickle.load(fp)
        return array
    except Exception:
        pass

    return array
