#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Created by BigFlower at 16/8/20
import re, os



def create_dir_if_not_exist(base_dir, dir_name):
    if dir_name not in os.listdir(base_dir):
        os.mkdir(os.path.join(base_dir, dir_name))

def delete_dir_if_exist(base_dir, dir_name):
    if dir_name in os.listdir(base_dir):
        os.rmdir()