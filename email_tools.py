import imaplib
import email
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os

from agno.utils.log import logger

load_dotenv()

user_email = os.getenv("GMAIL_USER")
password = os.getenv("GMAIL_PASSWORD")
user_name = os.getenv("GMAIL_USER_NAME")


def read_last_emails(num_emails=5):
    """
    Reads the last `num_emails` emails from the user's Gmail inbox.
    :param num_emails: The number of emails to read from the inbox. must be a positive integer.
    :return: A string containing the details of the last `num_emails` emails.
    """
    logger.info(f"Reading last {num_emails} emails from inbox")
    imap_url = 'imap.gmail.com'

    try:
        imap = imaplib.IMAP4_SSL(imap_url)
        imap.login(user_email, password)
        imap.select('Inbox')  # Connect to the inbox.

        _, msgnums = imap.search(None, 'ALL')

        c = 0
        messages = ""
        for msgnum in msgnums[0].split()[::-1]:
            if c >= num_emails: break
            c += 1
            _, data = imap.fetch(msgnum, '(RFC822)')
            message = email.message_from_bytes(data[0][1])

            messages += f"From: {message['From']}\n"
            messages += f"Subject: {message['Subject']}\n"
            messages += f"To: {message['To']}\n"
            messages += f"Date: {message['Date']}\n"
            for part in message.walk():
                if part.get_content_type() == 'text/plain':
                    messages += f"Body: {part.as_string()}\n"
            messages += "\n" + "="*50 + "\n"  # Add a blank line between emails
    except Exception as e:
        logger.error(f"Error reading emails: {e}")
        return f"error: {e}"
    
    return messages

def send_email(receiver_email, subject, body ):
    """
    Sends an email with the specified subject and body to the receiver's email address.
    :param receiver_email: The email address of the receiver.
    :param subject: The subject of the email.
    :param body: The body of the email.
    :return: "email sent successfully" if the email was sent successfully, "error: [error message]" otherwise.
    """
    logger.info(f"Sending email to {receiver_email}")
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = f"{user_name} <{user_email}>"
    msg["To"] = receiver_email
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(user_email, password)
            smtp.send_message(msg)
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return f"error: {e}"
    return "email sent successfully"