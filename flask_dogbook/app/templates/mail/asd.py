from flask_mail import Message
from app import mail
msg = Message('test subject',sender='lllvvvvvcheng@163.com',recipients=['lllvvvvvcheng@163.com'])
msg.body = 'text body'
msg.html = '<b>HTML</b>'
with app.app_context():
    mail.send(msg)