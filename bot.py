import pandas as pd
import time
from os import environ
from datetime import datetime
import gspread_dataframe as gsdf

from utils import connect_to_google_sheet, workingday, send_email
from immo import immosearch


if __name__ == '__main__':
    timestamp = datetime.strftime(datetime.now(), '%Y-%m-%d')

    if not workingday():
      print('We do not crawl the immo today')
      exit()
    try:
      gc = connect_to_google_sheet()
      
      sh = gc.open('Berlin_real_estate')
      df_haus = immosearch(haus_type='haus')
      df_wohnung = immosearch(haus_type='wohnung')
      df = pd.concat([df_haus, df_wohnung])
      wks = sh.add_worksheet(title = timestamp, rows = df.shape[0], cols = df.shape[1])
      gsdf.set_with_dataframe(wks, df)
    except Exception as e:
      print('Something is wrong.')
      send_email(msg='Something is wrong. Cannot crawl Immo today', subject='bothouse')
