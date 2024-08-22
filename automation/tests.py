import os
import tempfile
import shutil
from django.conf import settings

from django.test import TestCase, override_settings, Client
from django.core.files.uploadedfile import SimpleUploadedFile

from django.urls import reverse

from django.contrib.auth.models import User
from .models import APP, AVD
from .testing import AppiumTestAutomation 


class UserAuthTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_user_registration(self):
        response = self.client.post(reverse('automation:register'), {
            'username': 'newuser',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'email': 'newuser@example.com',
        })
        self.assertEqual(response.status_code, 302)  # Redirect after registration
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_user_login(self):
        response = self.client.post(reverse('automation:login'), {
            'username': 'testuser',
            'password': '12345',
        })
        self.assertEqual(response.status_code, 302)  # Redirect after login
        self.assertTrue('_auth_user_id' in self.client.session)


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class APPModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')

        self.app = APP.objects.create(
            name="Test App",
            uploaded_by=self.user,
            apk_file_path='test.apk',
        )

    def test_app_creation(self):
        self.assertEqual(self.app.name, "Test App")
        self.assertEqual(self.app.uploaded_by.username, "testuser")

    def test_app_update(self):
        self.app.name = "Updated App"
        self.app.save()
        self.assertEqual(self.app.name, "Updated App")

    def test_app_deletion(self):
        app_id = self.app.id
        self.app.delete()
        self.assertFalse(APP.objects.filter(id=app_id).exists())

@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class AppViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

        self.test_file_path = os.path.join(settings.MEDIA_ROOT, 'test_files', 'test.apk')
        os.makedirs(os.path.dirname(self.test_file_path), exist_ok=True)

        with open(self.test_file_path, 'wb') as f:
            f.write(b'Test APK content')

        self.app = APP.objects.create(
            name="Test App",
            apk_file_path=self.test_file_path,
            uploaded_by=self.user,
        )

    def tearDown(self):
        shutil.rmtree(settings.MEDIA_ROOT)

    def test_app_list_view(self):
        response = self.client.get(reverse('automation:user_apps'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'automation/apps_list.html')

    def test_app_detail_view(self):
        response = self.client.get(reverse('automation:app_detail', kwargs={'slug': self.app.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'automation/app_detail.html')

    def test_app_create_view(self):
        with open(self.test_file_path, 'rb') as f:
            uploaded_file = SimpleUploadedFile(f.name, f.read(), content_type='application/vnd.android.package-archive')

        response = self.client.post(reverse('automation:create_app'), {
            'name': 'New App',
            'apk_file_path': uploaded_file,
        })

        self.assertEqual(response.status_code, 302)  # Check for redirect after successful post
        self.assertTrue(APP.objects.filter(name='New App').exists())  # Check if the new app was created
        
    def test_app_update_view(self):
        response = self.client.post(reverse('automation:app_update', kwargs={'slug': self.app.slug}), {
            'name': 'Updated App',
        })
        self.assertEqual(response.status_code, 302)  # Redirect after update
        self.app.refresh_from_db()
        self.assertEqual(self.app.name, 'Updated App')

    def test_app_delete_view(self):
        response = self.client.post(reverse('automation:app_delete', args=[self.app.slug]), follow=True)
        self.assertEqual(response.status_code, 200)  
        self.assertFalse(APP.objects.filter(id=self.app.id).exists())  # Check if the app was deleted


class AppiumTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')

        # Create a sample AVD instance for testing
        self.avd = AVD.objects.create(
            name="Test AVD",
            sdk_root="C:/Users/USER_NAME/AppData/Local/Android/Sdk",  # Adjust this to your SDK path
            service_url="http://localhost:4724",
        )

        self.file_path = os.path.join(settings.MEDIA_ROOT, 'test.apk')
        self.automation = AppiumTestAutomation(avd=self.avd)

        # Start the driver
        self.driver = self.automation.start_driver(self.file_path)  # Replace with your actual start_driver implementation

    def test_run_test(self):
        # test driver starting, install the app and launching it
        self.assertTrue(self.driver)
        
    def tearDown(self):

        if self.driver:
            package_name = self.automation.get_package_name(self.file_path)
            self.automation.uninstall_app(package_name) # Ensure the app is uninstalled
            self.automation.driver.quit()  # Ensure the driver is properly closed

