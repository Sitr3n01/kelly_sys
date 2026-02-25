from django import forms
from django.core.exceptions import ValidationError

from .models import Application

ALLOWED_RESUME_TYPES = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
]
MAX_RESUME_SIZE = 5 * 1024 * 1024  # 5 MB


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['first_name', 'last_name', 'email', 'phone', 'cover_letter', 'resume']

    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if resume:
            if resume.content_type not in ALLOWED_RESUME_TYPES:
                raise ValidationError(
                    'Somente arquivos PDF e Word (.doc, .docx) são aceitos pelo tipo.'
                )
            if resume.size > MAX_RESUME_SIZE:
                raise ValidationError(
                    'O arquivo não pode exceder 5 MB.'
                )
            import os
            ext = os.path.splitext(resume.name)[1].lower()
            if ext not in ['.pdf', '.doc', '.docx']:
                raise ValidationError(
                    'Apenas extensões .pdf, .doc e .docx são permitidas.'
                )
        return resume
