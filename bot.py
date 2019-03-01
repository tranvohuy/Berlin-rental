import tweepy
from datetime import date, datetime
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
import gspread_dataframe as gsdf

from immo import immosearch


from os import environ


# We set up Heroku Scheduler daily (there is no weekly). 
# Hence to do the work weekly, we should have a trick.
# If today is not a Friday, exit the script, do nothing else.
if date.today().weekday()!=4:
    print('Today is not Friday. No search!')
    exit()


def get_client():
    scopes = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    json_creds = environ['google_cred']
    creds_dict = json.loads(json_creds)
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\\\n", "\n")
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scopes)
    gc = gspread.authorize(creds)
    return gc
    




if __name__=='__main__':
    gc = get_client()
    sh = gc.open('Berlin-rental')
    timestamp = datetime.strftime(datetime.now(), '%Y-%m-%d')
    #check whether to do the search or not
    #if yes, then proceed
    
    df = immosearch()

    wks = sh.add_worksheet(title = timestamp, rows = df.shape[0], cols = df.shape[1])
    gsdf.set_with_dataframe(wks, df)
