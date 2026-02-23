from django import forms

from .models import NewsletterSubscription


class NewsletterSubscriptionForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscription
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'placeholder': 'Seu melhor e-mail',
                'class': (
                    'flex-grow rounded-full border-gray-300 shadow-sm '
                    'focus:border-primary-500 focus:ring-primary-500 px-6 py-4'
                ),
            })
        }
