import os
import smtplib
from email.mime.text import MIMEText
from email.header import Header

def send_email(subject, content, to_addr):
    smtp_server = os.environ["SMTP_SERVER"]
    smtp_port = int(os.environ["SMTP_PORT"])
    from_addr = os.environ["FROM_ADDR"] 
    app_password = os.environ["APP_PASSWORD"]

    msg = MIMEText(content, "plain", "utf-8")
    msg["Subject"] = Header(subject, "utf-8")
    msg["From"] = from_addr
    msg["To"] = to_addr

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(from_addr, app_password)
        server.sendmail(from_addr, [to_addr], msg.as_string())


send_email("Job Completed", "任务状态:成功", os.environ["to_addr"])
