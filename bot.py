import tweepy
from datetime import date, datetime
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
import gspread_dataframe as gsdf

from immo import immosearch


from os import environ
json_creds = environ['google_cred']
creds_dict = json.loads(json_creds)


def get_client():
    scopes = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
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
