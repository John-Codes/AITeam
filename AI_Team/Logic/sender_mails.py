import os
from django.core.mail import send_mail
from django.conf import settings
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def email_send(prompt):
    # check variables
        subject = 'Someone asked in the chat of AI Team'
        message = f"""
        This email is to show the questions that potential customers have when visiting the page, which helps us to
        Have a better vision about the vision that customers have, their concerns, doubts and what they think about the product
        The question asked is as follows:

        {prompt}"""
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [ 'efexzium@gmail.com']        
        try:
            send_mail(subject, message, from_email, recipient_list)
        except Exception as e:
            print('correo no enviado porque:', e)

def Contac_us_mail(prompt):
    # check variables
        subject = 'A client has contacted AI Team'
        message = f""" 
        the email is send because they client want to contac us, that could contain any message
        Email for contact:
            {prompt}
            """
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [ 'efexzium@gmail.com']
        try:
            send_mail(subject, message, from_email, recipient_list)
        except Exception as e:
            print('correo no enviado porque:', e)

def notice_error(subject, message, side="Server Side"):
    # check variables
        
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [ 'efexzium@gmail.com']
        try:
            send_mail(subject, message, from_email, recipient_list)
        except Exception as e:
            print('correo no enviado porque:', e)

def notice_error_forms(data, email_contact, page, side="Server Side"):
    # check variables
        subject = f'An error has ocurred in the page:{page}'
        
        message =f"""
        emailfor contact: {email_contact}\n
        Side: {side}\n
        {data}
        """        
        
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [ 'efexzium@gmail.com']
        try:
            send_mail(subject, message, from_email, recipient_list)
        except Exception as e:
            print('correo no enviado porque:', e)

def image_seve_fail_email(data):
    # check variables
        subject = 'An error has ocurred When the user try to save any image'
        message = f""" Info of the image which failed to save, error info is:
        {data}
        """
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [ 'efexzium@gmail.com']
        try:
            send_mail(subject, message, from_email, recipient_list)
        except Exception as e:
            print('correo no enviado porque:', e)


def dislike_message(subject, message):
    # check variables
        
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [ 'efexzium@gmail.com']
        try:
            send_mail(subject, message, from_email, recipient_list)
        except Exception as e:
            print('correo no enviado porque:', e)