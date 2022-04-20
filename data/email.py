import smtplib
import socket
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
socket.getaddrinfo('127.0.0.1', 8080)


def generate_email(name, address, url, text=None):
    msg = MIMEMultipart()
    msg['From'] = "dashanov535@mail.ru"
    msg['To'] = address
    msg['Subject'] = 'PenguinCorp'
    if not text:
        body = f"{name.capitalize()}, Вы зарегистрировались на сайте Penguins Corp." \
               f"Для подтверждения своей почты перейдите по ссылке: " \
               f"{url}"
    else:
        body = text
    msg.attach(MIMEText(body, 'plain'))

    smtpObj = smtplib.SMTP('smtp.mail.ru', 587)
    smtpObj.starttls()
    smtpObj.login("dashanov535@mail.ru", "MJW6K5Swe42pE7WsBUsK")
    smtpObj.send_message(msg)
    smtpObj.quit()