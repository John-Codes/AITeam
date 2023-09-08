from django.core.mail import send_mail
from django.conf import settings

def email_send(prompt):
    try:
        subject = 'Se ha enviado una pregunta por email'
        message = f"""Un usuario ha enviado la seguiente pregunta: {prompt}"""
        from_email = settings.EMAIL_HOST_USER
        recipient_list = ['destinatario@example.com']
    
        send_mail(subject, message, from_email, recipient_list)
        print('correo enviado')
    except Exception as e:
        print('correo no enviado porque:', e)