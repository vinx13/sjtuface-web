#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Created by BigFlower at 16/8/20
import re, os, hashlib


def is_image_file(filename):
    return re.match(r'^.+\.(jpg)$', filename)


def md5_file_name(data):
    m = hashlib.md5()
    m.update(data)
    return m.hexdigest()

