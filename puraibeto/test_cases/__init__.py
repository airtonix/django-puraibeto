from django.template import Template, Context
from django.conf import settings
from django.test import TestCase
from django.test.client import Client
from django.http import Http404
from django.contrib.auth.models import AnonymousUser, User, Group
from django.core.files.uploadedfile import SimpleUploadedFile

from puraibeto import models, views, urls, signals

# from test_project.models import Thing


class TemplateTagTestCase(TestCase):

    def setUp(self):
        self.client = Client()

        # self.thing = Thing(name="First")
        self.authorised_user = User(username='zeno', first_name='zeno', last_name='jiricek')
        self.unauthorised_user = User(username='john', first_name='john', last_name='doe')
        self.anonymous_user = AnonymousUser()

    def tearDown(self):
        pass

    def test_upload_file(self):
        source = SimpleUploadedFile("file.txt", "file_content")

