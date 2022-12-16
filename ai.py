from bs4 import BeautifulSoup
import requests
import re
import json
import random
import datetime

def getFirst(url, index):
    print("GET for: " + url)
    page = requests.get(url)
    stringHtml = page.text

    f = open("demofile2.html", "w")
    f.write(stringHtml)
    f.close()

    x = re.search(r"assets.mountWidget\('slot-16', (.*)\)", stringHtml) 
    #print(x.group(1))

    f = open("group.json", "w")
    f.write(x.group(1))
    f.close()

    # get {index} item
    jsonGroup = json.loads(x.group(1))
    firstUrl = jsonGroup['prefetchedData']['aapiGetDealsList'][0]['entities'][index]['entity']['details']['entity']['landingPage']['url']
    substring = jsonGroup['prefetchedData']['aapiGetDealsList'][0]['entities'][index]['entity']['details']['entity']['price']['details']
    
    #
    title = jsonGroup['prefetchedData']['aapiGetDealsList'][0]['entities'][index]['entity']['details']['entity']['title']
    url = jsonGroup['prefetchedData']['aapiGetDealsList'][0]['entities'][index]['entity']['details']['entity']['landingPage']['url']
    image = jsonGroup['prefetchedData']['aapiGetDealsList'][0]['entities'][index]['entity']['details']['entity']['images'][0]['physicalId']
    imageExt = jsonGroup['prefetchedData']['aapiGetDealsList'][0]['entities'][index]['entity']['details']['entity']['images'][0]['extension']
    image = 'https://m.media-amazon.com/images/I/'+image+'.'+imageExt
    promotionWip = jsonGroup['prefetchedData']['aapiGetDealsList'][0]['entities'][index]['entity']['badge']['entity']['label']['content']['fragments']
    promotion = ''.join(list(map(lambda x: x['text'], promotionWip)))

    price = ""
    priceCurrency = ""
    try:
        price = jsonGroup['prefetchedData']['aapiGetDealsList'][0]['entities'][index]['entity']['details']['entity']['price']['details']['basisPrice']['moneyValueOrRange']['value']['amount']
        price = price.replace('\n', '').replace(' ', '').replace(',', '.').replace('\u202f', '').replace('\u00a0\u20ac', '')
        priceCurrency = jsonGroup['prefetchedData']['aapiGetDealsList'][0]['entities'][index]['entity']['details']['entity']['price']['details']['basisPrice']['moneyValueOrRange']['value']['currencyCode']
    except KeyError:
        print("no basis price")

    priceDeal = ""
    priceDealCurrency = ""
    try: 
        priceDeal = jsonGroup['prefetchedData']['aapiGetDealsList'][0]['entities'][index]['entity']['details']['entity']['price']['details']['dealPrice']['moneyValueOrRange']['value']['amount']
        priceDeal = priceDeal.replace('\n', '').replace(' ', '').replace(',', '.').replace('\u202f', '').replace('\u00a0\u20ac', '')
        priceDealCurrency = jsonGroup['prefetchedData']['aapiGetDealsList'][0]['entities'][index]['entity']['details']['entity']['price']['details']['dealPrice']['moneyValueOrRange']['value']['currencyCode']
    except KeyError:
        print("no deal price")
    #

    isCollection = False

    #print(str(substring))
    #print(substring.get("basisPrice", None))
    value = substring.get("basisPrice", None)
    if value is None: 
        isCollection = True

    if isCollection:
        try:
            print("is a collection")

            urlCollection = 'https://www.amazon.fr'+firstUrl
            print("go into collection: " + urlCollection)

            page = requests.get(urlCollection)
            stringHtml = page.text

            #f = open("demofile3.html", "a")
            #f.write(stringHtml)
            #f.close()

            soup = BeautifulSoup(stringHtml, 'html.parser')
            items = soup.find_all('span', class_='a-list-item')

            # for link in items:
            #    print(link)

            print('extract first item')
            #print(items[0])

            indexNested = 0
            firstItem = items[indexNested]
            title = firstItem.find_all('img', class_='octopus-dlp-asin-image')[0]['alt']
            url = firstItem.find_all('a', class_='a-link-normal')[0]['href']
            image = firstItem.find_all('img', class_='octopus-dlp-asin-image')[0]['src']
            imageExt = ""
            promotionWip = firstItem.find_all('div', class_='oct-deal-badge-label')[0].find_all('span')
            promotion = ''.join(list(map(lambda x: x.text, promotionWip)))

            priceDeal = ""
            priceDeal = firstItem.find_all('span', class_='a-offscreen')[0].text
            priceDeal = priceDeal.replace('\n', '').replace(' ', '').replace(',', '.').replace('\u202f', '').replace('\u00a0\u20ac', '')
    
            priceDealCurrency = firstItem.find_all('span', class_='a-price-symbol')[0].text.replace('\u20ac', 'EUR')
    
            price = ""
            price = firstItem.find_all('span', class_='a-text-strike')[0].text
            price = price.replace('\n', '').replace(' ', '').replace(',', '.').replace('\u202f', '').replace('\u00a0\u20ac', '')
            
            priceCurrency = firstItem.find_all('span', class_='a-price-symbol')[0].text.replace('\u20ac', 'EUR')

        except IndexError:
            print("not a collection")

    #print('\n')
    #print(title)
    #print(url)
    #print(image)
    #print(promotion)
    #print(price)
    #print(priceDeal)
    #print('\n')

    jsonFile = {}
    jsonFile["title"] = title
    jsonFile["url"] = url
    jsonFile["image"] = image
    jsonFile["imageExt"] = imageExt
    jsonFile["promotion"] = promotion
    jsonFile["price"] = price
    jsonFile["priceCurrency"] = priceCurrency
    jsonFile["priceDeal"] = priceDeal
    jsonFile["priceDealCurrency"] = priceDealCurrency

    return jsonFile

def findAndAddItem(url, index): 
    try:
        item = getFirst(url, index)
        item['date'] =  datetime.datetime.now()

        print(item['title'])

        if len(data['items']) > 0:
            find = filter(lambda c: c['title'] == item['title'],  data['items'])

            if len(list(find)) > 0:
                print('already exist')
            else:
                print('add item')
                data["items"].insert(0, item)
        else:
            print('add item')
            data["items"].insert(0, item)

    except Exception as e:
        print("error")


def pickHardAndAddTo(data): 
    f = open('hard.json')
    hardData = json.load(f)
    f.close()

    try:
        item = random.choice(hardData['items'])
        item['date'] =  datetime.datetime.now()

        print(item['title'])

        if len(data['items']) > 0:
            find = filter(lambda c: c['title'] == item['title'],  data['items'])

            if len(list(find)) > 0:
                print('already exist')
            else:
                print('add item')
                data["items"].insert(0, item)
        else:
            print('add item')
            data["items"].insert(0, item)

    except Exception as e:
        print("error")


def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

#main

game = 'https://www.amazon.fr/gp/goldbox?ie=UTF8&pf_rd_p=a1f294b4-3de9-4f2e-8561-165ecd4cc2af&pf_rd_r=4D301S34YY420TNQ7VME&pf_rd_s=auto-subnav-flyout-xiste-content-5&pf_rd_t=SubnavFlyout&ref_=sn_gfs_co_auto-xiste_51375011_1&deals-widget=%257B%2522version%2522%253A1%252C%2522viewIndex%2522%253A0%252C%2522presetId%2522%253A%2522deals-collection-all-deals%2522%252C%2522departments%2522%253A%255B%2522530490%2522%255D%252C%2522sorting%2522%253A%2522BY_SCORE%2522%257D'
phone = 'https://www.amazon.fr/gp/goldbox?ie=UTF8&pf_rd_p=a1f294b4-3de9-4f2e-8561-165ecd4cc2af&pf_rd_r=4D301S34YY420TNQ7VME&pf_rd_s=auto-subnav-flyout-xiste-content-5&pf_rd_t=SubnavFlyout&ref_=sn_gfs_co_auto-xiste_51375011_1&deals-widget=%257B%2522version%2522%253A1%252C%2522viewIndex%2522%253A0%252C%2522presetId%2522%253A%2522deals-collection-all-deals%2522%252C%2522departments%2522%253A%255B%252214060661%2522%255D%252C%2522sorting%2522%253A%2522BY_SCORE%2522%257D'
pc = ' https://www.amazon.fr/gp/goldbox?ie=UTF8&pf_rd_p=a1f294b4-3de9-4f2e-8561-165ecd4cc2af&pf_rd_r=4D301S34YY420TNQ7VME&pf_rd_s=auto-subnav-flyout-xiste-content-5&pf_rd_t=SubnavFlyout&ref_=sn_gfs_co_auto-xiste_51375011_1&deals-widget=%257B%2522version%2522%253A1%252C%2522viewIndex%2522%253A0%252C%2522presetId%2522%253A%2522deals-collection-all-deals%2522%252C%2522departments%2522%253A%255B%2522429879031%2522%255D%252C%2522sorting%2522%253A%2522BY_SCORE%2522%257D'
headphone = ' https://www.amazon.fr/gp/goldbox?ie=UTF8&pf_rd_p=a1f294b4-3de9-4f2e-8561-165ecd4cc2af&pf_rd_r=4D301S34YY420TNQ7VME&pf_rd_s=auto-subnav-flyout-xiste-content-5&pf_rd_t=SubnavFlyout&ref_=sn_gfs_co_auto-xiste_51375011_1&deals-widget=%257B%2522version%2522%253A1%252C%2522viewIndex%2522%253A0%252C%2522presetId%2522%253A%2522deals-collection-all-deals%2522%252C%2522departments%2522%253A%255B%252214054961%2522%255D%252C%2522sorting%2522%253A%2522BY_SCORE%2522%257D'

# read 
f = open('sample.json')
data = json.load(f)
f.close()

findAndAddItem(game, 0)
findAndAddItem(game, 1)
findAndAddItem(phone, 0)
findAndAddItem(pc, 0)
findAndAddItem(headphone, 0)

# pickHardAndAddTo(data)

# remove old items
data["items"] = data["items"][0:20]

f = open("sample.json", "w")
f.write(json.dumps(data, indent='\t', default = myconverter))
f.close()
