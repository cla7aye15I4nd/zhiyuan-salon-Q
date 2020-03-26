import smtplib
import threading

from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

from ..defines import *

def send_file(receiver, name, filename):
    content = f"""
        亲爱的 {name}:
           您好
           这是您的致远沙龙统计表，清查收。
        
        自动发送 - 来自 zhiyuan-salon-Q
    """
    thread = threading.Thread(target=_send_file, 
                args=(sender_mail, sender_password,
                        receiver, content, mail_title, filename))
    thread.start()

def _send_file(sender, password, receiver, content, title, filename):

    server = smtplib.SMTP('smtp.sjtu.edu.cn', 587)
    server.set_debuglevel(1)

    server.ehlo('smtp.sjtu.edu.cn')
    server.login(sender, password)

    message = MIMEMultipart()

    text_part = MIMEText(content, 'plain', 'utf-8')

    file_part = MIMEApplication(read_file(filename))
    file_part.add_header('Content-Disposition',
                         'attachment', filename='致远沙龙统计表.xls')

    message.attach(text_part)
    message.attach(file_part)
    
    message['Subject'] = Header(title, 'utf-8')
    message['From'] = sender
    message['To'] = receiver

    server.sendmail(sender, receiver, message.as_string())
    server.quit()

def read_file(filename):
    with open(filename,'rb') as f:
        return f.read()
