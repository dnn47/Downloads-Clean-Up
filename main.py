import os
from datetime import datetime, timedelta
import schedule
import time
from config import emailSender, emailPassword, emailReceiver
from email.message import EmailMessage
import ssl
import smtplib
import logging

def clean(targetDate):
    path = os.path.expanduser("~\Downloads")

    fullPath = os.path.abspath(path)
    try:
        files = os.listdir(fullPath)

        for fileName in files:
            filePath =  os.path.join(fullPath, fileName)
            fileDate = datetime.fromtimestamp(os.path.getmtime(filePath))
    
            if fileDate < targetDate:
                if os.path.isfile(filePath):
                    os.remove(filePath)
                    logging.info(f"Removed file: {filePath}")
                elif os.path.isdir(filePath):
                    clearDir(filePath)
                    os.rmdir(filePath)
                    logging.info(f"Removed dir: {filePath}")
        
    except Exception as e:
        logging.error(f"Error during cleaning: {e}")

def clearDir(path):
    files = os.listdir(path)

    for fileName in files:
        filePath =  os.path.join(path, fileName)
        if os.path.isdir(filePath):
            clearDir(filePath)
            os.rmdir(filePath)
        else:
            logging.info(f"Removed file: {filePath}")
            os.remove(filePath)

def sendEmail(emailReceiver, emailBody, emailSubject):
    try:
        email = EmailMessage()
        email['From'] = emailSender
        email['To'] = emailReceiver
        email['Subject'] = emailSubject
        email.add_alternative(emailBody, subtype='html')

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(emailSender, emailPassword)
            smtp.sendmail(emailSender, emailReceiver, email.as_string())

        logging.info("Email to "+ emailReceiver + " was sent successfully")
    except Exception as e:
        logging.error(f"Error sending email: {e}")
        
def alert():
    sendEmail(emailReceiver, emailBody="Cleaning Downloads Tomorrow", emailSubject="Cleaning Downloads Tomorrow")

def job(date):
    logging.info(f"----- {date} -----")
    targetDate = date - timedelta(days=90)
    clean(targetDate)
    sendEmail(emailReceiver, emailBody="Downloads Cleaned. Check cleaning script for files that were deleted", emailSubject="Downloads Cleaned")
    logging.info(f"--------------------------------------")

logging.basicConfig(filename='script_log.txt', level=logging.INFO)

while True:
    date = datetime.now()
    jobDate = date + timedelta(days=90)
    alertDate = jobDate - timedelta(days=1)

    schedule.every().day.at(alertDate.strftime("%H:%M")).do(alert)
    schedule.every().day.at(jobDate.strftime("%H:%M")).do(job, date)

    schedule.run_pending()
    time.sleep(1)
