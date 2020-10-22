#!/usr/bin/env python3

import argparse
import sys
import os
import logging
import shlex
import smtplib
import subprocess

logging.basicConfig(level=logging.INFO)
logger=logging.getLogger()


def init_cli():
    parser = argparse.ArgumentParser() 
    parser.add_argument("--gmail_sender", required=True, help="Bot user email")
    parser.add_argument("--gmail_pass", required=True, help="Bot user password")
    parser.add_argument("--recipients", required=True, 
                        nargs="+", help="Recipients of the mail")
    parser.add_argument("--subject", help="Email subject")
    parser.add_argument("--body_custom", help="Custom body content")
    parser.add_argument("--body_cmd", 
                        help="Bash command to execute to generate the mail content")

    args = parser.parse_args()

    gmail_sender = args.gmail_sender
    gmail_pass = args.gmail_pass
    recipients = ", ".join(args.recipients)
    subject = args.subject
    body_custom = args.body_custom
    body_cmd = args.body_cmd

    logger.info(f"Using {gmail_sender} to sent email")
    logger.info(f"Will send mail to: {recipients}")
    logger.info(f"Email subject: {subject}")

    if body_cmd:
        logger.info(f"Will run the following cmd: {body_cmd}")
    

    return (gmail_sender, gmail_pass, recipients, body_custom, body_cmd, subject)


def generate_body(body_custom="", body_cmd=""):
    body = ""

    if body_custom:
        body += f"{body_custom}\n"

    if body_cmd:
        body += f"Command executed: {body_cmd}"
        body_cmd_return = subprocess.run(shlex.split(body_cmd), 
                                         capture_output=True)
        if body_cmd_return.stdout:
            body += f"\n\nStdout:\n{body_cmd_return.stdout.decode()}"
        if body_cmd_return.stderr:
            body += f"\nStderr:\n{body_cmd_return.stderr.decode()}"

    return body


def generate_full_email(body, subject, gmail_sender, recipients):
    email = (f"To: {recipients}\n"
             f"From: {gmail_sender}\n"
             f"Subject: {subject}\n\n"
             f"{body}")

    return email


def send_mail(recipients, email, gmail_sender, gmail_pass):

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    try: 
        server.login(gmail_sender, gmail_pass)
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"Failed to authenticate {gmail_sender} on gmail with given password")
        sys.exit(1)

    server.sendmail(gmail_sender, recipients, email)
    server.quit()

def send_email_complete(gmail_sender, gmail_pass, 
                        recipients, body_custom, body_cmd, subject):
    body = generate_body(body_custom=body_custom, body_cmd=body_cmd)
    email = generate_full_email(body, subject, gmail_sender, recipients)
    send_mail(recipients, email, gmail_sender, gmail_pass)


def send_email_complete_systemd(gmail_sender, gmail_pass, 
                        recipients, body_custom, body_cmd, subject):

    systemd_service_result = os.environ.get('SERVICE_RESULT')
    
    if systemd_service_result == "success":
        print("Not service failure. Ignoring.")
        sys.exit(0)
    else:
        print(f"Service failure, sending and email to {gmail_sender}")
        send_email_complete(gmail_sender, gmail_pass, 
                            recipients, body_custom, body_cmd, subject)


if __name__ == "__main__":
    (gmail_sender, gmail_pass, recipients, 
     body_custom, body_cmd, subject) = init_cli()
    
    send_email_complete_systemd(gmail_sender, gmail_pass, 
                                recipients, body_custom, body_cmd, subject)
