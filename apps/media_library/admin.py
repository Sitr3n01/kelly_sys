from django.contrib import admin
from .models import MediaFolder, MediaFile


@admin.register(MediaFolder)
class MediaFolderAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent']


@admin.register(MediaFile)
class MediaFileAdmin(admin.ModelAdmin):
    list_display = ['title', 'folder', 'file_type', 'uploaded_by', 'created_at']
    list_filter = ['file_type', 'folder']
    search_fields = ['title', 'alt_text']
