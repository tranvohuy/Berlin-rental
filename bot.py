import tweepy
from datetime import date, datetime
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
import gspread_dataframe as gsdf

from immo import immosearch
import matplotlib.pyplot as plt
from pandas.plotting import table
import pandas as pd
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
    

def update_tweet(file_table):
   
    consumer_key= environ['consumer_key']
    consumer_secret = environ['consumer_secret']
    access_key = environ['access_key']
    access_secret = environ['access_secret']
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)
    
    api.update_with_media(file_table, status = 'Avg cold/warm rents in some districts in Berlin, according to rental ads in Immobilienscout24') 


    
def group_rooms(n):
    if n<2:
        return '#rooms<2'
    if n==2:
        return '2'
    if n<3:
        return '2.5'
    if n==3:
        return '3'
    if n>3:
        return '>3'


def make_table(df):
   
    impt_quarters=['Wilmersdorf (Wilmersdorf)', 'Schmargendorf (Wilmersdorf)', 'Grunewald (Wilmersdorf)', 
                   'Charlottenburg (Charlottenburg)',
                   'Mitte (Mitte)' , 'Wedding (Wedding)', 
                   'Tiergarten (Tiergarten)',
                   'Siemensstadt (Spandau)', 
                   'Haselhorst (Spandau)',    'Spandau (Spandau)', 
                   'Zehlendorf (Zehlendorf)', 'Wannsee (Zehlendorf)',
                   'Nikolassee (Zehlendorf)', 'Steglitz (Steglitz)',
                   'Prenzlauer Berg (Prenzlauer Berg)', 'Friedrichshain (Friedrichshain)'  ]

    df_quarter = df[df['quarter'].isin(impt_quarters)]
    df_quarter.rename(columns = {'quarter':'district'}, inplace = True)

    newcolumn = df_quarter['numberOfRooms'].apply(group_rooms)
    df_quarter = df_quarter.assign(Rooms=newcolumn) 

    #force these columns values to numeric, not string
    df_quarter[['price', 'warmprice']] = df_quarter[['price','warmprice']].apply(pd.to_numeric, errors='coerce', axis=1)

    df_summary = df_quarter[['Rooms', 'district', 'price', 'warmprice']].groupby(['district', 'Rooms'], as_index=False).mean()
    cols = ['#rooms<2', '2', '2.5', '3', '>3']
    df_summary_new = pd.DataFrame(columns= cols, index = impt_quarters)
    for index, row in df_summary.iterrows():
      df_summary_new.loc[row['district'], row['Rooms']] = '%.1f€/%.1f€' %(row['price'],row['warmprice'])


    fig, ax = plt.subplots(figsize=(15, 7)) # set size frame
    plt.title(timestamp+u':average cold/warm rent')
    ax.xaxis.set_visible(False)  # hide the x axis
    ax.yaxis.set_visible(False)  # hide the y axis
    ax.set_frame_on(False)  # no visible frame, uncomment if size is ok
    tabla = table(ax, df_summary_new, loc='upper right', colWidths=[0.08]*len(df_summary_new.columns))  # where df is your data frame
    tabla.auto_set_font_size(False) # Activate set fontsize manually
    tabla.set_fontsize(13) # if ++fontsize is necessary ++colWidths
    tabla.scale(2, 2) # change size table

    plt.savefig(file_table, transparent=True)
   

if __name__=='__main__':
    timestamp = datetime.strftime(datetime.now(), '%Y-%m-%d')

    gc = get_client()
    
    
    sh = gc.open('Berlin-rental')
    df = immosearch()
    wks = sh.add_worksheet(title = timestamp, rows = df.shape[0], cols = df.shape[1])
    gsdf.set_with_dataframe(wks, df)
    
#---------------
#for testing
#    wks = gc.open('Berlin-rental').get_worksheet(3)
#    df = gsdf.get_as_dataframe(wks)
#--------------
    file_table = 'table.png'
    make_table(df)
    update_tweet(file_table)
