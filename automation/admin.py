from django.contrib import admin
from .models import AVD, APP

class AdminAVD(admin.ModelAdmin):
    list_display = ("id", "name", "service_url", "booted")
class AdminAPP(admin.ModelAdmin):
    list_display = ("id", "name", "uploaded_by", "created_at", "updated_at")

admin.site.register(AVD, AdminAVD)
admin.site.register(APP, AdminAPP)
