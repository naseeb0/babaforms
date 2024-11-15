from google.oauth2 import service_account
from googleapiclient.discovery import build
from django.conf import settings
import re
import logging

logger = logging.getLogger(__name__)

class GoogleSheetsManager:
    def __init__(self):
        try:
            credentials = service_account.Credentials.from_service_account_info(
                settings.GOOGLE_SHEETS_CREDENTIALS,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            self.service = build('sheets', 'v4', credentials=credentials)
            logger.info("Google Sheets service initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Google Sheets service: {str(e)}")
            raise

    def get_sheet_id_from_url(self, sheet_url):
        """Extract sheet ID from Google Sheets URL"""
        # Handle both edit and view URLs
        patterns = [
            r'/spreadsheets/d/([a-zA-Z0-9-_]+)',
            r'/d/([a-zA-Z0-9-_]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, sheet_url)
            if match:
                return match.group(1)
        
        raise ValueError("Invalid Google Sheets URL")

    def setup_sheet(self, sheet_id):
        """Setup sheet with headers and formatting"""
        try:
            # Define headers
            headers = [
                'Submission Date', 'Name', 'Email', 'Phone', 
                'Is Realtor', 'Message'
            ]
            
            # Check if headers exist
            result = self.service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range='A1:F1'
            ).execute()
            
            if 'values' not in result:
                # Add headers
                self.service.spreadsheets().values().update(
                    spreadsheetId=sheet_id,
                    range='A1:F1',
                    valueInputOption='RAW',
                    body={'values': [headers]}
                ).execute()
                
                # Format headers
                requests = [{
                    'repeatCell': {
                        'range': {
                            'startRowIndex': 0,
                            'endRowIndex': 1,
                            'startColumnIndex': 0,
                            'endColumnIndex': 6
                        },
                        'cell': {
                            'userEnteredFormat': {
                                'backgroundColor': {
                                    'red': 0.9,
                                    'green': 0.9,
                                    'blue': 0.9
                                },
                                'textFormat': {
                                    'bold': True
                                }
                            }
                        },
                        'fields': 'userEnteredFormat(backgroundColor,textFormat)'
                    }
                }]
                
                self.service.spreadsheets().batchUpdate(
                    spreadsheetId=sheet_id,
                    body={'requests': requests}
                ).execute()
                
                logger.info(f"Sheet {sheet_id} setup completed")
            return True
            
        except Exception as e:
            logger.error(f"Error setting up sheet: {str(e)}")
            return False

    def append_row(self, sheet_url, data):
        """Append a new row of data to the sheet"""
        try:
            sheet_id = self.get_sheet_id_from_url(sheet_url)
            logger.info(f"Appending data to sheet: {sheet_id}")
            
            # Setup sheet if needed
            self.setup_sheet(sheet_id)
            
            # Prepare row data
            row = [
                data['submitted_at'].strftime('%Y-%m-%d %H:%M:%S'),
                data['name'],
                data['email'],
                data['phone'],
                'Yes' if data['is_realtor'] else 'No',
                data['message']
            ]
            
            # Append row
            result = self.service.spreadsheets().values().append(
                spreadsheetId=sheet_id,
                range='A:F',
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body={'values': [row]}
            ).execute()
            
            logger.info(f"Successfully appended row to sheet {sheet_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error appending to sheet: {str(e)}")
            return False

    def test_sheet_access(self, sheet_url):
        """Test if we can access the sheet"""
        try:
            sheet_id = self.get_sheet_id_from_url(sheet_url)
            self.service.spreadsheets().get(
                spreadsheetId=sheet_id
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Error accessing sheet: {str(e)}")
            return False