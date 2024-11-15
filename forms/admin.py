# forms/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django import forms
from django.core.exceptions import ValidationError
from .models import FormType, Client, ClientForm, FormSubmission
from .google_sheets import GoogleSheetsManager
import re

class ClientAdminForm(forms.ModelForm):
    def clean_sheet_link(self):
        url = self.cleaned_data['sheet_link']
        if url:
            # Verify it's a valid Google Sheets URL
            pattern = r'https://docs.google.com/spreadsheets/d/([a-zA-Z0-9-_]+)'
            if not re.match(pattern, url):
                raise ValidationError(
                    "Please enter a valid Google Sheets URL. "
                    "It should look like: https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID"
                )
            
            # Test sheet access
            try:
                sheets_manager = GoogleSheetsManager()
                if not sheets_manager.test_sheet_access(url):
                    raise ValidationError(
                        "Could not access this Google Sheet. "
                        "Please make sure it's shared with the service account email."
                    )
            except Exception as e:
                raise ValidationError(f"Error validating sheet: {str(e)}")
        return url

@admin.register(FormType)
class FormTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at', 'form_count')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'slug')
    ordering = ('name',)
    
    def form_count(self, obj):
        return obj.clientform_set.count()
    form_count.short_description = 'Active Forms'

class FormSubmissionInline(admin.TabularInline):
    model = FormSubmission
    extra = 0
    readonly_fields = ('name', 'email', 'phone', 'is_realtor', 'message', 'submitted_at')
    can_delete = False
    max_num = 0
    ordering = ('-submitted_at',)

    def has_add_permission(self, request, obj=None):
        return False

class ClientFormInline(admin.TabularInline):
    model = ClientForm
    extra = 1
    fields = ('form_type', 'is_active', 'created_at', 'submission_count', 'get_embed_code')
    readonly_fields = ('created_at', 'submission_count', 'get_embed_code')

    def submission_count(self, obj):
        return obj.submissions.count() if obj.id else 0
    submission_count.short_description = 'Submissions'

    def get_embed_code(self, obj):
        if obj.id:
            code = obj.get_embed_code()
            return format_html(
                '''
                <div class="embed-code">
                    <input type="text" value="{}" 
                           style="width: 360px; padding: 5px;" 
                           readonly 
                           onclick="this.select();">
                    <button type="button" 
                            onclick="navigator.clipboard.writeText(this.previousElementSibling.value)"
                            style="margin-left: 5px; padding: 5px 10px; background: #007bff; color: white; border: none; border-radius: 3px;">
                        Copy
                    </button>
                </div>
                ''',
                code
            )
        return '-'
    get_embed_code.short_description = 'Embed Code'

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    form = ClientAdminForm
    list_display = ('name', 'email', 'get_sheet_status', 'total_submissions', 'created_at')
    search_fields = ('name', 'email')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    inlines = [ClientFormInline]
    
    def get_sheet_status(self, obj):
        if obj.sheet_link:
            try:
                sheets_manager = GoogleSheetsManager()
                if sheets_manager.test_sheet_access(obj.sheet_link):
                    return format_html(
                        '<span style="color: green;">✓ Connected</span>'
                    )
                return format_html(
                    '<span style="color: red;">✗ Access Error</span>'
                )
            except:
                return format_html(
                    '<span style="color: red;">✗ Invalid Sheet</span>'
                )
        return format_html(
            '<span style="color: gray;">○ No Sheet</span>'
        )
    get_sheet_status.short_description = 'Sheet Status'

    def total_submissions(self, obj):
        return FormSubmission.objects.filter(client_form__client=obj).count()
    total_submissions.short_description = 'Total Submissions'

@admin.register(ClientForm)
class ClientFormAdmin(admin.ModelAdmin):
    list_display = ('client', 'form_type', 'is_active', 'submission_count', 'created_at')
    list_filter = ('form_type', 'is_active', 'created_at')
    search_fields = ('client__name', 'client__email', 'form_type__name')
    readonly_fields = ('form_id', 'created_at')
    ordering = ('-created_at',)
    inlines = [FormSubmissionInline]
    
    def submission_count(self, obj):
        return obj.submissions.count()
    submission_count.short_description = 'Submissions'

    def get_embed_code(self, obj):
        code = obj.get_embed_code()
        return format_html(
            '''
            <div class="embed-code">
                <input type="text" value="{}" 
                       style="width: 450px; padding: 5px;" 
                       readonly 
                       onclick="this.select();">
                <button type="button" 
                        onclick="navigator.clipboard.writeText(this.previousElementSibling.value)"
                        style="margin-left: 5px; padding: 5px 10px; background: #007bff; color: white; border: none; border-radius: 3px;">
                    Copy
                </button>
            </div>
            ''',
            code
        )
    get_embed_code.short_description = 'Embed Code'

@admin.register(FormSubmission)
class FormSubmissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'is_realtor', 'get_form_type', 'get_client', 'submitted_at')
    list_filter = ('is_realtor', 'submitted_at', 'client_form__form_type', 'client_form__client')
    search_fields = ('name', 'email', 'phone', 'message', 'client_form__client__name')
    readonly_fields = ('submitted_at',)
    ordering = ('-submitted_at',)
    
    def get_form_type(self, obj):
        return obj.client_form.form_type.name
    get_form_type.short_description = 'Form Type'
    
    def get_client(self, obj):
        return obj.client_form.client.name
    get_client.short_description = 'Client'

    def has_add_permission(self, request):
        return False  # Prevent manual creation of submissions