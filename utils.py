import gspread
from os import environ
# use creds to create a client to interact with the Google Drive API
from oauth2client.service_account import ServiceAccountCredentials
import json

def connect_to_google_sheet():

  scopes = ['https://spreadsheets.google.com/feeds',
          'https://www.googleapis.com/auth/drive']
  
  json_creds = environ['google_cred']
  creds_dict = json.loads(json_creds)
  creds_dict["private_key"] = creds_dict["private_key"].replace("\\\\n", "\n")
  creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scopes)
  gc = gspread.authorize(creds)
  
  return gspread.authorize(creds)
  
  
from os import environ
'''
smtplib is a less secure method than google auth. 
To use google auth, see https://github.com/shankarj67/python-gmail-api
'''
import smtplib

def send_email(msg: str, subject: str = None):
    #ads_msgs: a list of strings.
    gmail_bot = environ['gmail_bot']
    gmail_bot_pwd = environ['gmail_bot_pwd']

    sent_from = gmail_bot
    
    to = environ['email_to']
    to = to.replace(',',' ')
    
    #to is a list of emails.
    #to = ['user1@amail.com', 'user2@bmail.com']
    to = to.split()
    
    '''
    Example for the value in 'email_to': 'user1@amail.com, user2@gmai.com'
    Each email is separated by a commas ','. Blank spaces are allowed
    'user1@amail.com,     user2@gmai.com' is also valid
    'user1@gmail.com,    user2@dkjf.com' is also valid
    'user1@gmail.com,    user2@dkjf.com,' is also valid
    '''
    
    print(to)
    email_text = """Subject:%s\n\n  %s""" % (subject, msg)
    print(email_text)
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_bot, gmail_bot_pwd)
        #https://docs.python.org/2/library/smtplib.html#smtplib.SMTP.sendmail
        server.sendmail(sent_from, to, email_text.encode())
        server.close()
        print('Email sent.')
    except Exception as e:
        print('Something went wrong with emails: ', e)
        

from datetime import date

def workingday() -> bool:
    
    date_to_num ={
        'Monday': 0,
        'Tuesday': 1,
        'Wednesday': 2,
        'Thursday': 3,
        'Friday': 4,
        'Saturday': 5,
        'Sunday': 6,
    }
    num_to_date = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
                   'Saturday', 'Sunday']

    dates_to_crawl = ['Monday']
    weekday = date.today().weekday()

    print(f'Today is {num_to_date[weekday]}.')
    if weekday not in [date_to_num[date] for date in dates_to_crawl]:
      print(f'Today is not {str(dates_to_crawl)}. No search!')
      return False

    return True
