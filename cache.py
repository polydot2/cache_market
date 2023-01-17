from bs4 import BeautifulSoup
import requests
import re
import json
import random
import xml.etree.ElementTree as ET
import datetime

# get generic images
def getimg(title):
    images = {}    
    images["fnac"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2e/Fnac_Logo.svg/1984px-Fnac_Logo.svg.png"
    images["leclerc"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ed/Logo_E.Leclerc_Sans_le_texte.svg/120px-Logo_E.Leclerc_Sans_le_texte.svg.png"
    images["veepee"] = "https://codepromo.lexpress.fr/images/224x/images/v/veepee.png"
    images["leroy"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Leroy_Merlin.svg/langfr-1920px-Leroy_Merlin.svg.png"

    for key in images:
        if key in title.lower():
            return images[key] 

    return None

# get generic links
def getlink(title):
    images = {}    
    images["fnac"] = "https://www.fnac.com"
    images["leclerc"] = "https://www.eleclerc.com"
    images["veepee"] = "https://www.veepee.com"
    images["leroy"] = "https://www.leroy.com"

    for key in images:
        if key in title.lower():
            return images[key] 

    return None

# get deals
def getFirst(url, index):
    print("GET for: " + url)
    page = requests.get(url)
    stringHtml = page.text

    #f = open("demofile2.html", "w")
    #f.write(stringHtml)
    #f.close()

    x = re.search(r"assets.mountWidget\('slot-16', (.*)\)", stringHtml) 
    #print(x.group(1))

    #f = open("group.json", "w")
    #f.write(x.group(1))
    #f.close()

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
    f = open('./cache/hard.json')
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

## deals

game = 'https://www.amazon.fr/gp/goldbox?ie=UTF8&pf_rd_p=a1f294b4-3de9-4f2e-8561-165ecd4cc2af&pf_rd_r=4D301S34YY420TNQ7VME&pf_rd_s=auto-subnav-flyout-xiste-content-5&pf_rd_t=SubnavFlyout&ref_=sn_gfs_co_auto-xiste_51375011_1&deals-widget=%257B%2522version%2522%253A1%252C%2522viewIndex%2522%253A0%252C%2522presetId%2522%253A%2522deals-collection-all-deals%2522%252C%2522departments%2522%253A%255B%2522530490%2522%255D%252C%2522sorting%2522%253A%2522BY_SCORE%2522%257D'
phone = 'https://www.amazon.fr/gp/goldbox?ie=UTF8&pf_rd_p=a1f294b4-3de9-4f2e-8561-165ecd4cc2af&pf_rd_r=4D301S34YY420TNQ7VME&pf_rd_s=auto-subnav-flyout-xiste-content-5&pf_rd_t=SubnavFlyout&ref_=sn_gfs_co_auto-xiste_51375011_1&deals-widget=%257B%2522version%2522%253A1%252C%2522viewIndex%2522%253A0%252C%2522presetId%2522%253A%2522deals-collection-all-deals%2522%252C%2522departments%2522%253A%255B%252214060661%2522%255D%252C%2522sorting%2522%253A%2522BY_SCORE%2522%257D'
pc = ' https://www.amazon.fr/gp/goldbox?ie=UTF8&pf_rd_p=a1f294b4-3de9-4f2e-8561-165ecd4cc2af&pf_rd_r=4D301S34YY420TNQ7VME&pf_rd_s=auto-subnav-flyout-xiste-content-5&pf_rd_t=SubnavFlyout&ref_=sn_gfs_co_auto-xiste_51375011_1&deals-widget=%257B%2522version%2522%253A1%252C%2522viewIndex%2522%253A0%252C%2522presetId%2522%253A%2522deals-collection-all-deals%2522%252C%2522departments%2522%253A%255B%2522429879031%2522%255D%252C%2522sorting%2522%253A%2522BY_SCORE%2522%257D'
headphone = ' https://www.amazon.fr/gp/goldbox?ie=UTF8&pf_rd_p=a1f294b4-3de9-4f2e-8561-165ecd4cc2af&pf_rd_r=4D301S34YY420TNQ7VME&pf_rd_s=auto-subnav-flyout-xiste-content-5&pf_rd_t=SubnavFlyout&ref_=sn_gfs_co_auto-xiste_51375011_1&deals-widget=%257B%2522version%2522%253A1%252C%2522viewIndex%2522%253A0%252C%2522presetId%2522%253A%2522deals-collection-all-deals%2522%252C%2522departments%2522%253A%255B%252214054961%2522%255D%252C%2522sorting%2522%253A%2522BY_SCORE%2522%257D'

# read 
f = open('./cache/sample.json')
data = json.load(f)
f.close()

findAndAddItem(game, 0)
findAndAddItem(game, 1)
findAndAddItem(phone, 0)
findAndAddItem(pc, 0)
findAndAddItem(headphone, 0)

# pickHardAndAddTo(data)

# remove old items
data["items"] = data["items"][0:30]

f = open("./cache/sample.json", "w")
f.write(json.dumps(data, indent='\t', default = myconverter))
f.close()


## bon plans
url = "https://www.bons-plans-malins.com/feed/"
print("GET for: " + url)
page = requests.get(url)

tree = ET.ElementTree(ET.fromstring(page.content))
#tree = ET.parse('sample.xml')
root = tree.getroot().find('channel')

default = '%Y-%m-%d %X'
items = []

for itemX in root.findall('item'):
    print(itemX)
    item = {}
    item["title"] = itemX.find('title').text
    item["pubDate"] = itemX.find('pubDate').text
    item["date"] = datetime.datetime.strptime(item["pubDate"], '%a, %d %b %Y %H:%M:%S %z').strftime(default)
    item["description"] = itemX.find('description').text
    item["link"] = getlink(item["title"])

    item["category"] = []
    for category in itemX.findall('category'):
        item["category"].append(category.text)

    item["image"] = getimg(item["title"])
    items.append(item)

jsonobject = { "items" : items }

f = open("./cache/out.json", "w")
f.write(json.dumps(jsonobject, indent=4))
f.close()

##
url = "https://www.maxdebonsplans.fr/feed/"
print("GET for: " + url)
page = requests.get(url)

tree = ET.ElementTree(ET.fromstring(page.content))

#tree = ET.parse('sample2.xml')
root = tree.getroot().find('channel')

items = []

for itemX in root.findall('item'):
    print(itemX)
    item = {}
    item["title"] = itemX.find('title').text
    item["pubDate"] = itemX.find('pubDate').text
    item["date"] = datetime.datetime.strptime(item["pubDate"], '%a, %d %b %Y %H:%M:%S %z').strftime(default)
    item["description"] = itemX.find('description').text
    item["link"] = getlink(item["title"])

    item["category"] = []
    for category in itemX.findall('category'):
        item["category"].append(category.text)

    item["image"] = getimg(item["title"])
    items.append(item)

jsonobject = { "items" : items }

f = open("./cache/out2.json", "w")
f.write(json.dumps(jsonobject, indent=4))
f.close()
