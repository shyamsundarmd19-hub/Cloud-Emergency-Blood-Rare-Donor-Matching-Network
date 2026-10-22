import logging
from typing import List, Optional
import boto3
from botocore.exceptions import ClientError
from app.core.config import settings

logger = logging.getLogger("lifeline.notifications")


class NotificationService:
    def __init__(self):
        self.region = settings.AWS_REGION
        self._sns_client = None
        self._ses_client = None

    def get_sns_client(self):
        if self._sns_client is None:
            kwargs = {"region_name": self.region}
            if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
                kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
                kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY
            try:
                self._sns_client = boto3.client("sns", **kwargs)
            except Exception as e:
                logger.warning(f"SNS client initialization skipped: {e}")
                self._sns_client = None
        return self._sns_client

    def get_ses_client(self):
        if self._ses_client is None:
            kwargs = {"region_name": self.region}
            if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
                kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
                kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY
            try:
                self._ses_client = boto3.client("ses", **kwargs)
            except Exception as e:
                logger.warning(f"SES client initialization skipped: {e}")
                self._ses_client = None
        return self._ses_client

    async def send_emergency_sms(self, phone_number: str, message: str) -> bool:
        """
        Sends an immediate SMS via AWS SNS with Transactional routing priority.
        Used for urgent donor dispatching when rare or emergency blood is required.
        """
        client = self.get_sns_client()
        if not client:
            logger.info(f"[MOCK SNS SMS] To: {phone_number} | Message: {message}")
            return True

        try:
            # Set SMS type to Transactional for highest delivery speed
            response = client.publish(
                PhoneNumber=phone_number,
                Message=message,
                MessageAttributes={
                    'AWS.SNS.SMS.SenderID': {
                        'DataType': 'String',
                        'StringValue': settings.SMS_SENDER_ID[:11]
                    },
                    'AWS.SNS.SMS.SMSType': {
                        'DataType': 'String',
                        'StringValue': 'Transactional'
                    }
                }
            )
            message_id = response.get("MessageId")
            logger.info(f"Emergency SMS dispatched via AWS SNS to {phone_number} (MessageId: {message_id})")
            return True
        except ClientError as e:
            logger.error(f"Failed to send SMS to {phone_number} via SNS: {e}")
            return False

    async def send_emergency_email(
        self,
        recipient_emails: List[str],
        subject: str,
        body_html: str,
        body_text: Optional[str] = None
    ) -> bool:
        """
        Sends an emergency broadcast email to hospitals, blood banks, or rare donor registries using AWS SES.
        """
        client = self.get_ses_client()
        if not client:
            logger.info(f"[MOCK SES EMAIL] Recipients: {recipient_emails} | Subject: {subject}")
            return True

        if not recipient_emails:
            return False

        try:
            client.send_email(
                Source=settings.AWS_SES_SENDER_EMAIL,
                Destination={'ToAddresses': recipient_emails},
                Message={
                    'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                    'Body': {
                        'Html': {'Data': body_html, 'Charset': 'UTF-8'},
                        'Text': {'Data': body_text or body_html, 'Charset': 'UTF-8'}
                    }
                }
            )
            logger.info(f"Emergency email alert sent to {len(recipient_emails)} recipients via AWS SES")
            return True
        except ClientError as e:
            logger.error(f"Failed to send SES email alert: {e}")
            return False


notification_service = NotificationService()
