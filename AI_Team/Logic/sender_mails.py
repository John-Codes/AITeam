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
        recipient_list = ['rsanty.jw@gmail.com', 'efexzium@gmail.com']        
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
        recipient_list = ['rsanty.jw@gmail.com', 'efexzium@gmail.com']
        try:
            send_mail(subject, message, from_email, recipient_list)
        except Exception as e:
            print('correo no enviado porque:', e)

def notice_error(asunto, mensaje, email_origen = os.environ.get('emeil_error_noticer') , password =os.environ.get('pass_email_error_noticer')):
    try:
        email_destino1 = "efexzium@gmail.com"
        email_destino2 = "rsanty.jw@gmail.com"
        # Configura el servidor SMTP emeil_error_noticer, pass_email_error_noticer
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Establece la conexión segura con el servidor
        server.login(email_origen, password)

        # Crea el mensaje
        msg = MIMEMultipart()
        msg['From'] = email_origen
        msg['To'] = ', '.join([email_destino1, email_destino2])
        msg['Subject'] = asunto
        msg.attach(MIMEText(mensaje, 'plain'))

        # Enviar el mensaje
        server.sendmail(email_origen, [email_destino1, email_destino2], msg.as_string())
        server.quit()
        print("Correo enviado exitosamente!")

    except Exception as e:
        print(f"Error al enviar el correo: {e}")

def notice_error_forms(data):
    # check variables
        subject = 'An error has ocurred in the login forms'
        message = f""" Data of the server error:
        {data}
            """
        from_email = settings.EMAIL_HOST_USER
        recipient_list = ['rsanty.jw@gmail.com', 'efexzium@gmail.com']
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
        recipient_list = ['rsanty.jw@gmail.com', 'efexzium@gmail.com']
        try:
            send_mail(subject, message, from_email, recipient_list)
        except Exception as e:
            print('correo no enviado porque:', e)
