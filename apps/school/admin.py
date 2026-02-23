from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Page, TeamMember, Testimonial


@admin.register(Page)
class PageAdmin(ModelAdmin):
    list_display = ['title', 'site', 'is_published', 'order', 'updated_at']
    list_filter = ['is_published', 'site']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = [
        ('Content', {
            'fields': ('title', 'slug', 'content', 'featured_image'),
        }),
        ('Publication', {
            'fields': ('site', 'is_published', 'order'),
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    ]


@admin.register(TeamMember)
class TeamMemberAdmin(ModelAdmin):
    list_display = ['name', 'title', 'is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['name', 'title', 'bio']
    ordering = ['order', 'name']
    fieldsets = [
        (None, {'fields': ('name', 'title', 'photo', 'bio', 'email')}),
        ('Display', {'fields': ('is_active', 'order')}),
    ]


@admin.register(Testimonial)
class TestimonialAdmin(ModelAdmin):
    list_display = ['name', 'relationship', 'is_featured']
    list_filter = ['is_featured']
    search_fields = ['name', 'quote']
    actions = ['feature_selected', 'unfeature_selected']

    @admin.action(description='Feature selected testimonials')
    def feature_selected(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} testimonial(s) featured.')

    @admin.action(description='Unfeature selected testimonials')
    def unfeature_selected(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} testimonial(s) unfeatured.')
