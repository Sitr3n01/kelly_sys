from django.contrib import admin
from .models import Page, TeamMember, Testimonial


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ['title', 'site', 'is_published', 'order']
    list_filter = ['site', 'is_published']
    search_fields = ['title']
    prepopulated_fields = {'slug': ('title',)}


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ['name', 'title', 'is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['name', 'title']


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['name', 'relationship', 'is_featured']
    list_filter = ['is_featured']
    search_fields = ['name']
