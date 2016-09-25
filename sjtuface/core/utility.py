#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Created by BigFlower at 16/8/20
import os, hashlib, string, time

# FIXME: where should I place this variable?
UPLOAD_DIR = os.path.abspath("/root/sjtuface-web/sjtuface/static/uploads")
ATTENDANCE_UPLOAD_DIR = os.path.abspath("/root/sjtuface-web/sjtuface/static/uploads_attendance")

def is_image_file(filename, allowed_type):
    """

    :param filename: file name with extension name
    :param allowed_type: a list of allowed extension name

    is_image_file("abc.jpg", ["jpg", "jpeg", "png"])
    -> True
    """
    return get_extension_name(filename) in allowed_type


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
    return string.lower(filename.split(".")[-1])  #


def delete_photo_file(filename, from_='u'):
    """
    :param filename: filename, extension name included
    :param from_ : if 'u', delete from `UPLOAD_DIR`, else from 'ATTENDANCE_UPLOAD_DIR'
    """
    base_dir = UPLOAD_DIR if from_ == 'u' else ATTENDANCE_UPLOAD_DIR
    path = os.path.join(base_dir, filename)
    if os.path.exists(path):
        os.remove(path)


def get_filename(file):
    md5_ = md5(file.read())
    file.seek(0)
    ext = get_extension_name(file.filename)
    filename = u"{}{}.{}".format(md5_, time.time(), ext)
    return filename


def find_outstanding_one(lst, key=None, min_threshold=None, diff_threshold=None):
    """
    Find one outstanding item among a list
    e.g.
    f := find_outstanding_one
    f([1,1,1,4,5]) -> 5
    f([1,1,1,4,5], min_threshold=4) -> 5
    f([1,1,1,4,5], min_threshold=6) -> None
    f([1,1,1,4,5], diff_threshold=0.5) -> 5
    f([1,1,1,4,5], diff_threshold=1) -> 5
    f([1,1,1,4,5], diff_threshold=1.5) -> None

    :param lst: a list / dict
    :param key: a function applied to `lst`
     find_outstanding_one(lst, key) = find_outstanding_one(map(key, lst))
    :param min_threshold: the min value of the 'outstanding value'
    :param diff_threshold: the min difference between the biggest and the second-biggest value
    :return: the outstanding value or `None`
    """
    tmp = map(key, lst) if key else lst

    m = max(tmp)
    if min_threshold and m < min_threshold:
        return None

    ind = tmp.index(m)
    second_m = max(x for i, x in enumerate(tmp) if i != ind)

    if diff_threshold and m - second_m < diff_threshold:
        return None

    return lst[ind]
