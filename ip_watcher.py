#!/usr/bin/env python
import smtplib
from email.mime.text import MIMEText
import yaml
import os
from requests import get
import argparse


def get_args():
    desc = 'Send emails when your public ip address changes'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-f', '--force',
                        action='store_true',
                        help='Force an email to be sent')
    return parser.parse_args()


def get_current_pub_ip():
    return get('https://api.ipify.org').text


def get_previous_pub_ip(filename):
    return open(filename).read() if os.path.isfile(filename) else 'No History'


def write_previous_pub_ip_file(filename, pub_ip):
    open(filename, 'w').write(pub_ip)


def send_change_email(gmail_username, gmail_password, from_email, to_email,
                      email_subject, email_content):
    # setup the message
    msg = MIMEText(email_content)
    msg['Subject'] = email_subject
    msg['From'] = from_email
    msg['To'] = to_email

    # Send the message via Gmail.
    s = smtplib.SMTP("smtp.gmail.com", 587)
    s.ehlo()
    s.starttls()
    s.login(gmail_username, gmail_password)
    s.send_message(msg)
    s.quit()


def get_email_content(email_template_filename, dns_name, previous_ip,
                      current_ip, dns_management_link):
    tempalte = open(email_template_filename).read()
    return tempalte % (dns_name, previous_ip, current_ip, dns_management_link)


def main():
    args = get_args()
    # load settings and setup variables
    settings = yaml.load(open('settings.yaml').read())
    to_emails = ', '.join(settings['to_emails'])
    current_pub_ip = get_current_pub_ip()
    previous_pub_ip = get_previous_pub_ip(settings['previous_ip_filename'])
    email_content = get_email_content(settings['email_template_filename'],
                                      settings['dns_name'],
                                      previous_pub_ip,
                                      current_pub_ip,
                                      settings['dns_management_link'])

    # check if our ip address has changed
    if (previous_pub_ip != current_pub_ip) or (args.force):
        write_previous_pub_ip_file(settings['previous_ip_filename'],
                                   current_pub_ip)
        send_change_email(settings['gmail_username'],
                          settings['gmail_password'],
                          settings['from_email'],
                          to_emails,
                          settings['email_subject'],
                          email_content)


if __name__ == '__main__':
    main()
