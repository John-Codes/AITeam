from django.core.mail import send_mail
from django.conf import settings

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
        subject = 'A client has contacted AI Team through the decorator @myemail'
        message = f""" 
        Remember that those who send messages with this decorator is because they know it will come to us and will be waiting for a response
        The message is as follows
            {prompt}
            """
        from_email = settings.EMAIL_HOST_USER
        recipient_list = ['rsanty.jw@gmail.com', 'efexzium@gmail.com']
        try:
            send_mail(subject, message, from_email, recipient_list)
        except Exception as e:
            print('correo no enviado porque:', e)