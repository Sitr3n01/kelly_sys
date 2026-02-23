from django.shortcuts import render, get_object_or_404
from .models import Page, TeamMember, Testimonial

def home(request):
    testimonials = Testimonial.objects.filter(is_featured=True)
    return render(request, 'school/home.html', {
        'testimonials': testimonials,
    })

def page_detail(request, slug):
    page = get_object_or_404(Page, slug=slug, site=request.site, is_published=True)
    return render(request, 'school/page_detail.html', {'page': page})

def team_list(request):
    members = TeamMember.objects.filter(is_active=True)
    return render(request, 'school/team_list.html', {'members': members})
