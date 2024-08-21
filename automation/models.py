import os
import random
import string
import shutil
from django.db import models
from django.contrib.auth import get_user_model

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

User = get_user_model()

def get_upload_path(instance, filename):
    return os.path.join(instance.slug, filename)

def generate_unique_slug(length=8):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

class AVD(models.Model):
    name = models.CharField(max_length=150)
    sdk_root = models.CharField(max_length=255)
    service_url = models.URLField(max_length=200)
    booted = models.BooleanField(default=False)

    def clean(self):
        if not os.path.isdir(self.sdk_root):
            raise ValidationError(_("The folder path does not exist.")) 

    def __str__(self):
        return self.name

class APP(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, verbose_name=_("App name"))
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, blank=True, max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    screen_changed = models.BooleanField(default=False)
    is_tested = models.BooleanField(default=False)

    apk_file_path = models.FileField(upload_to=get_upload_path, verbose_name=_("APK File Path"))
    ui_hierarchy = models.FileField(upload_to=get_upload_path, blank=True, null=True)
    video_recording_path = models.FileField(upload_to=get_upload_path, blank=True, null=True)
    first_screen_screenshot_path = models.ImageField(upload_to=get_upload_path, blank=True, null=True)
    second_screen_screenshot_path = models.ImageField(upload_to=get_upload_path, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            unique_slug = generate_unique_slug()
            while APP.objects.filter(slug=unique_slug).exists():
                unique_slug = generate_unique_slug()
            self.slug = unique_slug

        for field in ['apk_file_path', 'ui_hierarchy',
                      'video_recording_path', 'first_screen_screenshot_path', 
                      'second_screen_screenshot_path']:
            try:      
                current_file = getattr(self, field)
                if current_file:
                    old_file = APP.objects.get(pk=self.pk)
                    old_file_path = getattr(old_file, field).path
                    if old_file_path != current_file.path:
                        if os.path.isfile(old_file_path):
                            os.remove(old_file_path)
            except:
                pass
                            
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        folder_path = os.path.dirname(self.apk_file_path.path)
        if os.path.isdir(folder_path):
            shutil.rmtree(folder_path)

        super().delete(*args, **kwargs)
         
    def __str__(self):
        return self.name