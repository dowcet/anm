import os
import re
import urllib2
import requests
from bs4 import BeautifulSoup as BS

class anm_asset:
    "A class to represent an asset found at http://ofa.arkib.gov.my"
    def __init__(self, asset_num):
        self.asset_num = asset_num
        self.props = {}

    def get_props(asset):
        # init a dictionary for whatever properties we want
        asset_num = str(asset.asset_num)
        print "defining props for", asset_num
        # set path for the file of the page for this asset 
        asset_page_file = "./asset_pages/"+str(asset_num)+".html"
        # make the folder for asset page files if it doesn't exist
        if not os.path.exists("./asset_pages"):
            print "making asset_pages folder"
            os.makedirs("./asset_pages")
        # get and save the asset page file if it doesn't exist
        if not os.path.exists(asset_page_file):
            asset_page_url = "http://ofa.arkib.gov.my/ofa/group/asset/"+str(asset_num)
            print "Fetching", asset_page_url 
            asset_page = requests.get(asset_page_url)
            print asset_page
            with open(asset_page_file, "wb") as file:
                file.write(asset_page.text)
        # read the asset page file into BS
        print "reading", asset_page_file 
        asset_page = BS(open(asset_page_file))
        # get the URL of the asset PDF
        iframe_src = asset_page.find('iframe')['src']
        if "pdf" in iframe_src:
            asset.props["pdf_url"] = re.search("(?P<url>http?://[^\s]+)", iframe_src).group("url")
        # get the table with the other properties
        #table_non = BS(asset_page.find_all('table', {'class' : "non"}))
        #table_non_rows = table_non.find_all('tr')
        # COME BACK TO THIS
        return asset

def get_all_asset_nums(search_url):
    asset_list = []
    if not "http://" in search_url:
        search_page = open(search_url)
    else:
        search_page = requests.get(search_url)
    search_page = BS(search_page)
    hrefs = search_page.find_all(href=re.compile("asset"))
    for result in hrefs:
        asset_list.append((re.findall(r'\d+', str(result))))
    return asset_list

# ('div', {'class' : 'category-box-item-title-02'}):
#         box = BS(box)
#         print box.find_all('a')['href']
        # for result in hrefs:
        #     assetlist.append(re.findall(r'\d+', hrefs))
    # print asset_list
    # return asset_list

search_url = "oil_palm_search.html"
asset_num_list = get_all_asset_nums(search_url)
for asset_num in asset_num_list:
    asset = anm_asset(asset_num[0])
    if len(asset.asset_num) > 5:
        print "Getting properties for asset", asset.asset_num
        asset.get_props()
#    print asset.asset_num, asset.props
        pdf_dest = "./pdf/" + str(asset.asset_num) + ".pdf"
        if os.path.exists(pdf_dest):
            print pdf_dest, "already exists"
        elif 'pdf_url' in asset.props:
            print "Downloading PDF from", asset.props['pdf_url']
            rq = urllib2.Request(asset.props['pdf_url'])
            res = urllib2.urlopen(rq)
            pdf = open("./pdf/" + str(asset.asset_num) + ".pdf", 'wb')
            pdf.write(res.read())
            pdf.close()

#         self.title = 
#         # No Penerimaan
#         self.request_num = 
#         # Media Asal
#         self.orig_media = 
#         # Subjek
#         self.subject = 
#         # Sumber
#         self.source = 
#         # Tarikh
#         self.date = 
#         # Jenis Rekod
#         self.type = 
#         # Mukasurat Akses
#         self.page = 
#         # Kategori
#         self.cat = 
#         # Subkategori
#         self.subcat = 
#         # Lokasi
#         self.location =
#          URL to download PDF
#         self.pdf = 
