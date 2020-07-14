from bs4 import BeautifulSoup
import json
import urllib.request as urllib2
from random import choice, randint
import pandas as pd
import time

AGENTS = ['Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1309.0 Safari/537.17',
        'Mozilla/5.0 (compatible; MSIE 10.6; Windows NT 6.1; Trident/5.0; InfoPath.2; SLCC1; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET CLR 2.0.50727) 3gpp-gba UNTRUSTED/1.0',
        'Opera/12.80 (Windows NT 5.1; U; en) Presto/2.10.289 Version/12.02',
        'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)',
        'Mozilla/3.0',
        'Mozilla/5.0 (iPhone; U; CPU like Mac OS X; en) AppleWebKit/420+ (KHTML, like Gecko) Version/3.0 Mobile/1A543a Safari/419.3',
        'Mozilla/5.0 (Linux; U; Android 0.5; en-us) AppleWebKit/522+ (KHTML, like Gecko) Safari/419.3',
        'Opera/9.00 (Windows NT 5.1; U; en)']


def urlquery(url: str):
    """
    Args:
        url (str): url of a website. For example: url = "www.cnn.com"
    Return:
        html of a website in a form of "bytes" instead of string.
    """
    try:
        sleeptime = float(randint(1, 6))/5
        time.sleep(sleeptime)

        agent = choice(AGENTS)
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', agent)]

        html = opener.open(url).read()
        time.sleep(sleeptime)
        
        return html

    except Exception as e:
        print(f'Something went wrong with Crawling:\n%{e}')


def immoscout24parser(url):
    
    """
    Args:
        url (str): url of a website. For example: url = "www.cnn.com"
    :param url:
    :return:
    """
    
    try:
        soup = BeautifulSoup(urlquery(url), 'html.parser')
        scripts = soup.findAll('script')
        for script in scripts:
            #print script.text.strip()
            if 'IS24.resultList' in script.text.strip():
                s = script.string.split('\n')
                for line in s:
                    #print('\n\n\'%s\'' % line)
                    if line.strip().startswith('resultListModel'):
                        resultListModel = line.strip('resultListModel: ')
                        immo_json = json.loads(resultListModel[:-1])

                        searchResponseModel = immo_json[u'searchResponseModel']
                        resultlist_json = searchResponseModel[u'resultlist.resultlist']
                        
                        return resultlist_json

    except Exception as e:
        print("Fehler in immoscout24 parser: %s" % e)

#we search whole Berlin
def immosearch(haus_type = 'haus', buying_type='Kauf') -> pd.DataFrame:
    """
    haus_type: 'haus', 'wohnung'
    buying_type: 'Kauf', 'Miete'. For real estate, buying_type should be 'Kauf
    """

    # a dictionary stores all ads
    immos = {}
    page = 0
    while True:
      page+=1
      url = f"https://www.immobilienscout24.de/Suche/de/berlin/berlin/{haus_type}-kaufen?pagenumber={page}"
      print(f"Searching {url}")
      resultlist_json = None
      while resultlist_json is None:
          try:
              resultlist_json = immoscout24parser(url)
              number_of_pages = int(resultlist_json[u'paging'][u'numberOfPages'])
              pageNumber = int(resultlist_json[u'paging'][u'pageNumber'])
          except:
              pass
      if page > number_of_pages:
          break

      # Get the data
      for resultlistEntry in resultlist_json['resultlistEntries'][0][u'resultlistEntry']:
          
          # realEstate will contain all info of an ad, identified by ID

          realEstate = {}
          realEstate['haus_wohnung'] = haus_type
          realEstate['creation'] = resultlistEntry[u'@creation']
          realEstate['modification'] = resultlistEntry[u'@modification']
          realEstate['publishdate'] = resultlistEntry[u'@publishDate']
          realEstate['realEstateID'] = resultlistEntry[u'realEstateId']
          
          realEstate_json = resultlistEntry[u'resultlist.realEstate']

          realEstate['title'] = realEstate_json['title']
          realEstate['address'] = realEstate_json['address']['description']['text']
          realEstate['postcode'] = realEstate_json['address']['postcode']
          realEstate['quarter'] = realEstate_json['address']['quarter']

          try:
              realEstate['lat'] = realEstate_json['address'][u'wgs84Coordinate']['latitude']
              realEstate['lon'] = realEstate_json['address'][u'wgs84Coordinate']['longitude']
          except:
              realEstate['lat'] = None
              realEstate['lon'] = None

          
          realEstate['private_offer'] = realEstate_json['privateOffer']
          realEstate['contact'] = " ".join([value for key, value in realEstate_json['contactDetails'].items() \
                                if key in  {'firstname', 'lastname', 'phoneNumber'}])
          if realEstate['private_offer'] == 'false':
            realEstate['realtor_Comp_name'] = realEstate_json['realtorCompanyName']
          else:
            realEstate['realtor_Comp_name'] = 'private'
          
          realEstate['price'] = realEstate_json['price']['value']
          realEstate['num_rooms']  = realEstate_json['numberOfRooms']
          realEstate['courtage'] = realEstate_json['courtage']['hasCourtage']
          realEstate['guest_toilet'] = realEstate_json['guestToilet']
          realEstate['cellar'] = realEstate_json['cellar']
          
          realEstate['company_customer_id'] = realEstate_json['companyWideCustomerId']
          realEstate['ID'] = realEstate_json[u'@id']


          realEstate['url'] = u'https://www.immobilienscout24.de/expose/%s' % realEstate['ID']
          
          

          immos[realEstate['ID']] = realEstate

      print(f'Scrape Page {page}/{number_of_pages} ({len(immos)} Immobilien {haus_type} {buying_type} found).')
      
      #end while
    print(f"Scraped {len(immos)} Immos")
    df = pd.DataFrame(immos).T
    df.index.name = 'ID'

    return df
  
