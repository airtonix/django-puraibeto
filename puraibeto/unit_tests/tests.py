from uuid import uuid4
from django.test import TestCase
from django.test.client import Client
from django.http import Http404
from django.contrib.auth.models import AnonymousUser, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.contenttypes.models import ContentType

from puraibeto.models import PrivateFile
from puraibeto.conf import settings

from . import models


class BasicTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.csrf_client = Client(enforce_csrf_checks=True)
        self.thing = models.Thing(name="First")
        self.thing.save()
        self.authorised_user = User(username='zeno', first_name='zeno', last_name='jiricek')
        self.unauthorised_user = User(username='john', first_name='john', last_name='doe')
        self.anonymous_user = AnonymousUser()

    def tearDown(self):
        pass

    # def test_basic_urls(self):
    #     response = self.client.get(reverse('thing-list'))
    #     self.assertEqual(response.status_code, 200)
    #     response = self.client.get(reverse('thing-detail', args=[self.thing.id]))
    #     self.assertEqual(response.status_code, 200)
    #     response = self.client.get(reverse('puraibeto_files', args=[self.thing.id]))
    #     self.assertEqual(response.status_code, 200)

    def test_create_file(self):
        newthing = models.Thing.objects.create(name="New File")

        for i in range(0, 30):
            source = SimpleUploadedFile("file.txt", str(uuid4()))
            newfile = PrivateFile(file=source, attached_to=newthing)
            newfile.save()

    # def test_upload_urls(self):
    #     path = reverse('puraibeto_upload', args=[self.thing.id])
    #     response = self.client.get(path)
    #     self.assertEqual(response.status_code, 200)

    #     source = SimpleUploadedFile("file.txt", "file_content")
    #     response = self.client.post(path, {'name': 'test file', 'file': source})
    #     self.assertEqual(response.status_code, 200)
