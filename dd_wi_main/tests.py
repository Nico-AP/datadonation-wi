from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ddm.projects.models import ResearchProfile

User = get_user_model()


class TestUrls(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.credentials = {'username': 'user', 'password': '<PASSWORD>'}
        cls.user = User.objects.create_user(
            **cls.credentials, **{'email': 'owner@mail.com'})
        ResearchProfile.objects.create(user=cls.user)

    def test_ddm_urls_not_authenticated(self):
        url = reverse('ddm_projects:list')
        get_response = self.client.get(url)
        self.assertEqual(get_response.status_code, 302)

    def test_ddm_urls_authenticated(self):
        url = reverse('ddm_projects:list')
        client = Client()
        client.login(**{'username': 'owner', 'password': '123'})
        get_response = client.get(url, follow=True)
        self.assertEqual(get_response.status_code, 200)

    def test_login_url(self):
        url = reverse('ddm_login')
        get_response = self.client.get(url, follow=True)
        self.assertEqual(get_response.status_code, 200)

    def test_logout_url(self):
        url = reverse('ddm_logout')
        client = Client()
        client.login(**{'username': 'owner', 'password': '123'})
        get_response = client.get(url, follow=True)
        self.assertEqual(get_response.status_code, 200)
