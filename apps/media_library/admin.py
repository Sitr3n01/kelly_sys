from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import MediaFile, MediaFolder


@admin.register(MediaFolder)
class MediaFolderAdmin(ModelAdmin):
    list_display = ['name', 'parent']
    search_fields = ['name']


@admin.register(MediaFile)
class MediaFileAdmin(ModelAdmin):
    list_display = ['title', 'folder', 'file_type', 'uploaded_by', 'created_at']
    list_filter = ['file_type', 'folder']
    search_fields = ['title', 'alt_text']
