#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Created by BigFlower at 16/7/29

from __future__ import print_function, with_statement
import facepp
import os
from .models import Person, Photo
from utility import UPLOAD_DIR
from api_exception import api_error_type, NameExistError, NoFaceDetectedError
from config import API_KEY, API_SECRET


class FaceRecognitionSys:
    """
    Face recognition system using facepp api

    1. When instantiated, the `Group` name of the instance is determined
    2. When `initialize` is called,
        1. `Group` is created at the server
        2. `Person` are created according to images at `cls.db_img_dir`
    3. After 1.2. are carried out, call `identify_new_face` to identify a new face
    """

    def __init__(self, group_name):
        self.api = facepp.API(key=API_KEY, secret=API_SECRET)
        self.group_name = group_name

    def initialize(self, reconstruct=True):
        """
        For each face image in directory `db_img_dir`,
        carry out face recognition.
        return unless training at facepp server finished.

        :param reconstruct:
            if `True`:
                if 'Group' or 'Person' with same name already exists at the server,
                 they will be deleted and reconstruct
            if `False`:
                Nothing will happened, which means:
                1. 'Person' already in the group will not be deleted
                2. faces of 'Person' with same name will not be updated
        """
        print("reading database...")
        faces = self._get_db_faces()
        print(str(faces))
        print("{} faces read".format(len(faces)))

        print("Creating group..")
        self._create_group(self.group_name, reconstruct)

        print("Creating person...")
        for name, face_ids in faces.items():
            if len(face_ids) > 0:
                self._create_person(name, reconstruct, face_id=face_ids, group_name=self.group_name)

        print("Training...")
        training = self.api.train.identify(group_name=self.group_name)
        self.api.wait_async(training['session_id'])
        print("Training done.")

        print("Database initialized.")

    def add_person(self, img_path, remove_if_exist, person_name=None):
        """
        Add one 'Person' to the 'Group' at the server
        directly from local image file

        :param img_path: the path to the image file
        :param remove_if_exist: namely
        :param person_name: the name of the person, by default is the file name without suffix
        """
        if person_name is None:
            person_name = os.path.basename(img_path).split(".")[0]  # remove suffix name
        face_id = self._detect_face(facepp.File(img_path))
        self._create_person(person_name, remove_if_exist, face_id=face_id, group_name=self.group_name)

    def remove_person(self, person_name):
        """
        Remove `Person` from the `Group`.
        Raise facepp.ApiError if the name does not exist

        :param person_name: the name of the person
        """
        self.api.group.remove_person(self.group_name, person_name)

    def empty_group(self):
        cnt = 0
        lst = self.api.group.get_info(self.group_name)["person"]
        for p in lst:
            self.api.person.delete(person_id=p["person_id"])
            cnt += 1
            print(u"Person '{}' deleted.".format(p["person_name"]))
        print("{} people deleted.".format(cnt))

    def remove_group(self):
        self.empty_group()
        self.api.group.delete(group_name=self.group_name)
        self.group_name = None

    def identify_new_face(self, path_to_image):
        # TODO: unfinished
        ret = self.api.recognition.identify(group_name=self.group_name, post=True, img=facepp.File(path_to_image))
        ret = ret['face'][0]['candidate']
        print("Result of face identification to '{}'\nCandidates:".format(path_to_image))
        for r in ret:
            print(u"{}:\t{:.3f}%".format(r["person_name"], r["confidence"]))
        return ret

    def _create_group(self, group_name, remove_if_exist=True, **kwargs):
        try:
            self.api.group.create(group_name=group_name, **kwargs)
            ret = "Group '{}' created."
        except facepp.APIError as e:
            if api_error_type(e) is NameExistError:
                if remove_if_exist:
                    self.api.group.delete(group_name=group_name)
                    self.api.group.create(group_name=group_name, **kwargs)
                    ret = "Group '{}' already exists, replaced."
                else:
                    ret = "Group '{}' already exists, ignored."
            else:
                raise

        print(ret.format(group_name))

    def _create_person(self, person_name, remove_if_exist=True, **kwargs):
        try:
            self.api.person.create(person_name=person_name, **kwargs)
            ret = "Person '{}' created."
        except facepp.APIError as e:
            if api_error_type(e) is NameExistError:
                if remove_if_exist:
                    self.api.person.delete(person_name=person_name)
                    self.api.person.create(person_name=person_name, **kwargs)
                    ret = "Person '{}' already exists, replaced."
                else:
                    ret = "Person '{}' already exists, ignored."
            else:
                raise

        print(ret.format(person_name))

    def _get_db_faces(self, db_img_dir=None):
        """
        Get faces from images
        :return: a dict in the format of
            { <person_name> : [< a_str_of_face_id >, ...]
                ...
                ...
              "failed" : [< failed_photo_path_1 >, < failed_photo_path_2 > ...]
            }

        """
        faces = {}
        for person in Person.query.all():
            faces[person.name] = []
            for photo in person.photos:
                photo_path = os.path.join(UPLOAD_DIR, photo.filename)
                print(photo_path)
                photo_file = facepp.File(photo_path)
                try:
                    f_id = self._detect_face(photo_file)
                except NoFaceDetectedError:
                    print("{} failed!".format(photo_path))
                else:
                    faces[person.name].append(f_id)

        return faces

    def _detect_face(self, img_file):
        """
        Detect a face from `facepp.File` type
        :param img_file: of type `facepp.File`
        :return: the id of the face detected
        e.g.
        self._detect_face(facepp.File("database/1.jpg"))
        """
        ret = self.api.detection.detect(post=True, img=img_file)['face']
        if len(ret) > 0:
            return ret[0]['face_id']
        else:
            raise NoFaceDetectedError
