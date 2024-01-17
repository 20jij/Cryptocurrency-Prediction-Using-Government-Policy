import requests
from bs4 import BeautifulSoup
import os
import dateutil.parser as dparser

def ripwrite(name, link):
    sURL="https://www.irs.gov"+link
    sURL = requests.get(sURL)
    shtml = sURL.text
    i = 0
    while os.path.exists("./data_tax/"+f"{name}-{i}.html"):
        i += 1
    #sf = open("./data_tax/"+name+".html", "wb")
    sf = open("./data_tax/"+f"{name}-{i}.html", "wb")
    sf.write(shtml.encode('utf8'))
    sf.close()

#cryptocurrency, bitcoin, crypto, blockchain
word = "cryptocurrency"
strURL = "https://www.irs.gov/site-index-date-search?search="+word+"&field_pup_historical_1=All&field_pup_historical=All"
myURL = requests.get(strURL)
html = myURL.text

f = open("data_irs.csv", "a")
#writer = csv.writer(f)

soup = BeautifulSoup(html, 'html.parser')
text = soup.findAll('div',{'class':'views-row'})
pText = soup.find('li',{'class':'pager__item pager__item--last'}).find('a')['href']
p = int(pText[pText.rfind("=")+1:len(pText)])

i = 0
for page in range(0,p):
    if page>0:
        myURL = requests.get(strURL+"&page="+str(page))
        html = myURL.text
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.findAll('div',{'class':'views-row'})

    for item in text:
        links = item.find('a')['href']
        desc = item.find('div',{'class':'search-excerpt'}).text.strip()
        dnloc = desc.find(",")
        ddloc = desc.find("—")
        if (ddloc - dnloc)>15:
            dname = desc[:dnloc].strip()
            ddate = desc[dnloc+1:ddloc].strip()
            #ddate = dparser.parse(desc)
        elif ddloc<20:
            dname = links[links.rfind("-")+1:]+str(i)
            ddate = desc[:ddloc].strip()
        row = '"'+dname+'","'+ddate+'","'+links+'","'+desc+'"\n'
        print(row)
        if len(ddate)<20:
            #writer.writerow(row)
            f.write(row)
            ripwrite(dname, links)
        else:
            print("NOT SAVED")
        i=i+1
    
f.close()
