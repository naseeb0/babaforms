from django.db import models
import uuid
from django.conf import settings

class FormType(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class Client(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    sheet_link = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']

class ClientForm(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='forms')
    form_type = models.ForeignKey(FormType, on_delete=models.PROTECT)
    form_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.client.name} - {self.form_type.name}"
    
    def get_embed_code(self):
        domain = "yoursite.com"  # Change this to your domain in production
        if settings.DEBUG:
            domain = "127.0.0.1:8000"
        
        return f'<script src="http://{domain}/static/forms/js/form.js" data-form-id="{self.form_id}" data-form-type="{self.form_type.slug}"></script>'
class FormSubmission(models.Model):
    client_form = models.ForeignKey(ClientForm, on_delete=models.CASCADE, related_name='submissions')
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    is_realtor = models.BooleanField(default=False)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Submission from {self.name} for {self.client_form.client.name}"
    
    class Meta:
        ordering = ['-submitted_at']