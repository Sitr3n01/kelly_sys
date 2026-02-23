from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import JobPosting, Application
from .forms import ApplicationForm

def job_list(request):
    jobs = JobPosting.objects.filter(status=JobPosting.Status.OPEN)
    return render(request, 'hiring/job_list.html', {'jobs': jobs})

def job_detail(request, slug):
    job = get_object_or_404(JobPosting, slug=slug, status=JobPosting.Status.OPEN)
    
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.save()
            messages.success(request, 'Sua candidatura foi enviada com sucesso!')
            return redirect('hiring:job_detail', slug=job.slug)
    else:
        form = ApplicationForm()
        
    return render(request, 'hiring/job_detail.html', {'job': job, 'form': form})
