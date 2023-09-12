from django.core.mail import send_mail
from django.conf import settings

def email_send(prompt):
    # check variables
        subject = 'La función de envio de email ya esta enviando correos'
        message = f"""
        Hola soy tu asistente IA de AITEAM y he detectado una pregunta de un usuario con correo: correo_ de usuario
        ahora sigue analizar la respuesta en busca de correos para que se envie y convertir eso en una variable global 
        para que envie preguntas del usuario de toda la conversación, el correo que llegue seguirá diciendo:
        Solo tu puedes responder la pregunta: (a continuación el prompt)
        {prompt}"""
        from_email = settings.EMAIL_HOST_USER
        print('this is from email:',from_email)
        recipient_list = ['rsanty.jw@gmail.com', 'efexzium@gmail.com']
        print('all config variables will get')        
        try:
            send_mail(subject, message, from_email, recipient_list)
            print('correo enviado')
        except Exception as e:
            print('correo no enviado porque:', e)