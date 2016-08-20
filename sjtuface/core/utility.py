#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Created by BigFlower at 16/8/20
import re, os, hashlib, shutil

# FIXME: where should I place this variable?
UPLOAD_DIR = os.path.abspath("sjtuface/static/uploads")


def is_image_file(filename, allowed_type):
    """

    :param filename: file name with extension name
    :param allowed_type: a list of allowed extension name

    is_image_file("abc.jpg", ["jpg", "jpeg", "png"])
    -> True
    """
    return re.match(r'^.+\.(%s)$' % ("|".join(allowed_type)), filename)


def md5(data):
    m = hashlib.md5()
    m.update(data)
    return m.hexdigest()


def create_dir_if_not_exist(dir_name, base_dir=""):
    try:
        os.mkdir(os.path.join(base_dir, dir_name))
    except OSError:
        pass


def get_extension_name(filename):
    return filename.split(".", 1)[-1]  #


def delete_photo_file(filename, dir_name=None):
    """
    Photo files all have different names,
    however they are in different sub-directories under `static/uploads`,
    this function can delete the assigned photo file from all of these dirs
    :param: filename: filename, extestion name included
    """
    if not dir_name:
        for d in os.listdir(UPLOAD_DIR):
            if os.path.isdir(d) and filename in os.listdir(os.path.join(UPLOAD_DIR, d)):
                dir_name = d

    if not dir_name:
        # TODO:No such file
        # add exception handle
        return

    # todo: exception handle
    os.remove(os.path.join(UPLOAD_DIR, dir_name, filename))


def delete_photo_dir(dir_name, silent=True):
    try:
        shutil.rmtree(os.path.join(UPLOAD_DIR, dir_name))
    except OSError:
        if silent:
            pass
        else:
            raise

