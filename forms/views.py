from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from .models import ClientForm
from .google_sheets import GoogleSheetsManager
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
sheets_manager = GoogleSheetsManager()

@csrf_exempt
def handle_form_submission(request, form_id):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    
    try:
        # Get the client form
        client_form = ClientForm.objects.get(form_id=form_id, is_active=True)
        logger.info(f"Processing submission for {client_form.client.name}")
        
        # Parse the submission data
        data = json.loads(request.body)
        
        # Create the submission
        submission = client_form.submissions.create(
            name=data.get('name', ''),
            email=data.get('email', ''),
            phone=data.get('phone', ''),
            is_realtor=data.get('is_realtor', False),
            message=data.get('message', '')
        )
        
        # Prepare data for Google Sheets
        sheet_data = {
            'submitted_at': submission.submitted_at,
            'name': submission.name,
            'email': submission.email,
            'phone': submission.phone,
            'is_realtor': submission.is_realtor,
            'message': submission.message
        }
        
        # Update Google Sheet if URL is provided
        if client_form.client.sheet_link:
            logger.info(f"Updating Google Sheet: {client_form.client.sheet_link}")
            sheets_manager.append_row(client_form.client.sheet_link, sheet_data)
        
        # Send email notification
        send_mail(
            subject=f'New Form Submission - {client_form.form_type.name}',
            message=f'''
            New submission received:
            
            Form: {client_form.form_type.name}
            Name: {submission.name}
            Email: {submission.email}
            Phone: {submission.phone}
            Is Realtor: {'Yes' if submission.is_realtor else 'No'}
            Message: {submission.message}
            
            This data has been added to your Google Sheet.
            ''',
            from_email='noreply@yoursite.com',
            recipient_list=[client_form.client.email],
            fail_silently=True,
        )
        
        return JsonResponse({
            'status': 'success',
            'message': 'Form submitted successfully!'
        })
        
    except Exception as e:
        logger.error(f"Error processing submission: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'An error occurred while processing your submission.'
        }, status=500)