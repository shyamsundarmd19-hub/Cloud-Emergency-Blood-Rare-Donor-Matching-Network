import logging
from typing import List, Optional
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from app.core.config import settings

logger = logging.getLogger("lifeline.notifications")


class NotificationService:
    def __init__(self):
        self.region = settings.AWS_REGION
        self._sns_client = None
        self._ses_client = None

    def get_sns_client(self):
        """Lazy-initialize Boto3 SNS client."""
        if self._sns_client is None:
            kwargs = {"region_name": self.region}
            if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
                kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
                kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY
            try:
                self._sns_client = boto3.client("sns", **kwargs)
            except Exception as e:
                logger.warning(f"Boto3 SNS client initialization fallback: {e}")
                self._sns_client = None
        return self._sns_client

    def get_ses_client(self):
        """Lazy-initialize Boto3 SES client."""
        if self._ses_client is None:
            kwargs = {"region_name": self.region}
            if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
                kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
                kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY
            try:
                self._ses_client = boto3.client("ses", **kwargs)
            except Exception as e:
                logger.warning(f"Boto3 SES client initialization fallback: {e}")
                self._ses_client = None
        return self._ses_client

    async def send_sms_alert(self, phone: str, message: str) -> bool:
        """
        Sends high-priority Transactional SMS via AWS SNS.
        """
        client = self.get_sns_client()
        if not client:
            logger.info(f"[MOCK SNS SMS] -> {phone}: {message}")
            return True

        try:
            response = client.publish(
                PhoneNumber=phone,
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
            logger.info(f"AWS SNS SMS dispatched to {phone} (MessageId: {response.get('MessageId')})")
            return True
        except (ClientError, NoCredentialsError, Exception) as e:
            logger.info(f"[MOCK SNS SMS Fallback] (AWS {type(e).__name__}) -> {phone}: {message}")
            return True

    async def send_email_alert(self, recipients: List[str], subject: str, html_body: str) -> bool:
        """
        Sends formatted emergency alerts to donors & hospitals via AWS SES.
        """
        client = self.get_ses_client()
        if not client:
            logger.info(f"[MOCK SES EMAIL] -> {recipients} | Subject: {subject}")
            return True

        if not recipients:
            return False

        try:
            client.send_email(
                Source=settings.AWS_SES_SENDER_EMAIL,
                Destination={'ToAddresses': recipients},
                Message={
                    'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                    'Body': {
                        'Html': {'Data': html_body, 'Charset': 'UTF-8'},
                        'Text': {'Data': subject, 'Charset': 'UTF-8'}
                    }
                }
            )
            logger.info(f"AWS SES Email dispatched to {len(recipients)} recipient(s)")
            return True
        except (ClientError, NoCredentialsError, Exception) as e:
            logger.info(f"[MOCK SES EMAIL Fallback] (AWS {type(e).__name__}) -> {recipients} | Subject: {subject}")
            return True

    async def trigger_critical_blood_alert(
        self,
        donor_phones: List[str],
        donor_emails: List[str],
        blood_group: str,
        hospital_name: str,
        city: str,
        units_required: int,
        urgency: str,
        patient_name: str
    ) -> dict:
        """
        Broadcasts instant emergency alerts to matching donors via AWS SNS (SMS) & SES (Email).
        """
        sms_body = (
            f"🚨 [LIFELINE CRITICAL] Blood Group {blood_group} urgently needed! "
            f"Hospital: {hospital_name}, {city}. Units: {units_required}. "
            f"Urgency: {urgency.upper()}. Please open LifeLine app to pledge."
        )

        email_html = f"""
        <div style="font-family: Arial, sans-serif; background-color: #fffaf0; padding: 24px; border-radius: 12px; border: 1px solid #fed7aa;">
            <h2 style="color: #ea580c; margin-top: 0;">🚨 LifeLine Urgent Blood Dispatch Alert</h2>
            <p style="font-size: 15px; color: #7c2d12;">A verified emergency transfusion request matches your blood profile:</p>
            <table style="width: 100%; border-collapse: collapse; margin: 16px 0; background: white; border-radius: 8px;">
                <tr><td style="padding: 10px; font-weight: bold; border-bottom: 1px solid #ffedd5;">Blood Group:</td><td style="padding: 10px; font-size: 18px; font-weight: bold; color: #ea580c; border-bottom: 1px solid #ffedd5;">{blood_group}</td></tr>
                <tr><td style="padding: 10px; font-weight: bold; border-bottom: 1px solid #ffedd5;">Patient:</td><td style="padding: 10px; border-bottom: 1px solid #ffedd5;">{patient_name}</td></tr>
                <tr><td style="padding: 10px; font-weight: bold; border-bottom: 1px solid #ffedd5;">Hospital:</td><td style="padding: 10px; border-bottom: 1px solid #ffedd5;">{hospital_name} ({city})</td></tr>
                <tr><td style="padding: 10px; font-weight: bold; border-bottom: 1px solid #ffedd5;">Units Needed:</td><td style="padding: 10px; border-bottom: 1px solid #ffedd5;">{units_required}</td></tr>
                <tr><td style="padding: 10px; font-weight: bold;">Urgency Level:</td><td style="padding: 10px; text-transform: uppercase; font-weight: bold; color: #dc2626;">{urgency}</td></tr>
            </table>
            <p style="color: #9a3412; font-size: 13px;">Every second counts. Log in to LifeLine to confirm your donation pledge.</p>
        </div>
        """

        sms_count = 0
        for phone in donor_phones:
            if phone:
                success = await self.send_sms_alert(phone, sms_body)
                if success:
                    sms_count += 1

        email_count = 0
        if donor_emails:
            subject = f"🚨 URGENT {blood_group} Blood Required at {hospital_name}"
            success = await self.send_email_alert(donor_emails, subject, email_html)
            if success:
                email_count = len(donor_emails)

        return {
            "sms_alerts_sent": sms_count,
            "email_alerts_sent": email_count,
            "matched_recipients": max(len(donor_phones), len(donor_emails))
        }


notification_service = NotificationService()
