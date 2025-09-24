#!/usr/bin/env python3
"""
Alert Sender for Grafana alerts
Sends notifications to Slack via webhook when Grafana alerts fire
"""

import json
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, Optional

import requests
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlertSender:
    """Handles sending Grafana alerts to Slack"""
    
    def __init__(self):
        self.slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        self.slack_token = os.getenv("SLACK_BOT_TOKEN")
        self.channel = os.getenv("SLACK_CHANNEL", "#monitoring")
        self.client = None
        
        if self.slack_token:
            self.client = WebClient(token=self.slack_token)
        elif not self.slack_webhook_url:
            logger.warning("No Slack webhook URL or token configured")
    
    def send_slack_alert(self, alert_data: Dict[str, Any]) -> bool:
        """
        Send alert to Slack using either webhook or bot client
        
        Args:
            alert_data: Grafana alert payload
            
        Returns:
            bool: True if sent successfully
        """
        try:
            if self.slack_webhook_url:
                return self._send_via_webhook(alert_data)
            elif self.client:
                return self._send_via_bot(alert_data)
            else:
                logger.error("No Slack configuration available")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")
            return False
    
    def _send_via_webhook(self, alert_data: Dict[str, Any]) -> bool:
        """Send alert using Slack webhook"""
        if not self.slack_webhook_url:
            logger.error("Slack webhook URL not configured")
            return False
            
        # Parse Grafana alert data
        title = alert_data.get("alerts", [{}])[0].get("annotations", {}).get("summary", "Alert Fired")
        description = alert_data.get("alerts", [{}])[0].get("annotations", {}).get("description", "")
        severity = alert_data.get("alerts", [{}])[0].get("labels", {}).get("severity", "unknown")
        status = alert_data.get("status", "unknown")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create Slack message
        slack_message = {
            "text": f"🚨 *{title}* 🚨",
            "attachments": [
                {
                    "color": self._get_severity_color(severity),
                    "fields": [
                        {
                            "title": "Status",
                            "value": status,
                            "short": True
                        },
                        {
                            "title": "Severity",
                            "value": severity.upper(),
                            "short": True
                        },
                        {
                            "title": "Timestamp",
                            "value": timestamp,
                            "short": True
                        }
                    ],
                    "text": description or "No description provided",
                    "footer": "Chonost Monitoring",
                    "ts": datetime.now().timestamp()
                }
            ]
        }
        
        response = requests.post(
            self.slack_webhook_url,
            json=slack_message,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info(f"Alert sent to Slack webhook: {title}")
            return True
        else:
            logger.error(f"Webhook request failed: {response.status_code} - {response.text}")
            return False
    
    def _send_via_bot(self, alert_data: Dict[str, Any]) -> bool:
        """Send alert using Slack bot client"""
        try:
            # Parse Grafana alert data
            title = alert_data.get("alerts", [{}])[0].get("annotations", {}).get("summary", "Alert Fired")
            description = alert_data.get("alerts", [{}])[0].get("annotations", {}).get("description", "")
            severity = alert_data.get("alerts", [{}])[0].get("labels", {}).get("severity", "unknown")
            status = alert_data.get("status", "unknown")
            
            # Create Slack blocks for rich formatting
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"🚨 {title} 🚨"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Status:*\n{status}"
                        },
                        {
                            "type": "mrkdwn", 
                            "text": f"*Severity:*\n{severity.upper()}"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{description}*"
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"Sent at <{datetime.now().isoformat()}|now>"
                        }
                    ]
                }
            ]
            
            if self.client is None:
                logger.error("Slack client not initialized")
                return False
                
            response = self.client.chat_postMessage(
                channel=self.channel,
                blocks=blocks,
                text=f"{title} - {status}"
            )
            
            if not response["ok"]:
                logger.error(f"Slack bot message failed: {response['error']}")
                return False
                
            logger.info(f"Alert sent to Slack bot: {title}")
            return True
            
        except SlackApiError as e:
            logger.error(f"Slack API error: {e.response['error']}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending Slack alert: {e}")
            return False
    
    def _get_severity_color(self, severity: str) -> str:
        """Get Slack attachment color based on severity"""
        colors = {
            "critical": "#FF0000",  # Red
            "warning": "#FFC000",   # Yellow
            "info": "#00FF00",      # Green
            "unknown": "#CCCCCC"    # Gray
        }
        return colors.get(severity.lower(), "#CCCCCC")
    
    def send_email_alert(self, alert_data: Dict[str, Any], to_email: str) -> bool:
        """
        Fallback email alert using smtplib
        
        Args:
            alert_data: Grafana alert payload
            to_email: Recipient email address
            
        Returns:
            bool: True if sent successfully
        """
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            # Email configuration
            smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
            smtp_port = int(os.getenv("SMTP_PORT", "587"))
            smtp_user = os.getenv("SMTP_USER")
            smtp_password = os.getenv("SMTP_PASSWORD")
            
            if not all([smtp_server, smtp_user, smtp_password]):
                logger.warning("SMTP configuration incomplete, skipping email alert")
                return False
            
            # Ensure non-None values for type safety
            smtp_user = smtp_user or ""
            smtp_password = smtp_password or ""
            
            # Parse alert data
            title = alert_data.get("alerts", [{}])[0].get("annotations", {}).get("summary", "Alert Fired")
            description = alert_data.get("alerts", [{}])[0].get("annotations", {}).get("description", "")
            severity = alert_data.get("alerts", [{}])[0].get("labels", {}).get("severity", "unknown")
            status = alert_data.get("status", "unknown")
            
            # Create email message
            msg = MIMEMultipart()
            msg["From"] = smtp_user
            msg["To"] = to_email
            msg["Subject"] = f"🚨 Chonost Alert: {title}"
            
            body = f"""
Chonost Monitoring Alert

Title: {title}
Status: {status}
Severity: {severity}
Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Description:
{description}

---
This is an automated alert from Chonost Manuscript OS monitoring system.
            """
            
            msg.attach(MIMEText(body, "plain"))
            
            # Send email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_password)
            text = msg.as_string()
            server.sendmail(smtp_user, to_email, text)
            server.quit()
            
            logger.info(f"Email alert sent to {to_email}: {title}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
            return False


def main():
    """Main function to handle Grafana webhook requests"""
    sender = AlertSender()
    
    try:
        # Read JSON payload from stdin (Grafana webhook)
        input_data = sys.stdin.read().strip()
        if not input_data:
            logger.error("No input data received")
            sys.exit(1)
        
        alert_data = json.loads(input_data)
        logger.info(f"Received alert: {alert_data.get('status', 'unknown')} - {alert_data.get('alerts', [{}])[0].get('annotations', {}).get('summary', 'Unknown')}")
        
        # Send to Slack
        slack_success = sender.send_slack_alert(alert_data)
        
        # Fallback to email if Slack fails and email is configured
        if not slack_success:
            email_recipient = os.getenv("ALERT_EMAIL")
            if email_recipient:
                sender.send_email_alert(alert_data, email_recipient)
                logger.info("Sent fallback email alert")
            else:
                logger.warning("Slack failed and no email recipient configured")
        
        sys.exit(0 if slack_success else 1)
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON received: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()