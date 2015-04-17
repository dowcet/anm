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
            try:
                asset_page = requests.get(asset_page_url, timeout=30)
                return asset_page
            except requests.exceptions.Timeout:
                print(asset_page_url,'Timed Out!')
            except requests.exceptions.ConnectionError:
                print(asset_page_url,'Connection Error!')
            with open(asset_page_file, "wb") as file:
                file.write(asset_page.text)
        # read the asset page file into BS
        print "Attempting to read", asset_page_file
        try:
            asset_page = BS(open(asset_page_file))
            # get the URL of the asset PDF
            iframe_src = asset_page.find('iframe')['src']
            if "pdf" in iframe_src:
                asset.props["pdf_url"] = re.search("(?P<url>http?://[^\s]+)", iframe_src).group("url")
        # get the table with the other properties
        #table_non = BS(asset_page.find_all('table', {'class' : "non"}))
        #table_non_rows = table_non.find_all('tr')
        # COME BACK TO THIS
        except:
            print "Failed to define properties for asset", asset.asset_num
        return asset

def get_all_asset_nums(search_url):
    result_list = []
    asset_list = []
    if not "http://" in search_url:
        search_page = open(search_url)
    else:
        search_page = requests.get(search_url)
    search_page = BS(search_page)
    hrefs = search_page.find_all(href=re.compile("asset"))
    for result in hrefs:
        result_nums = re.findall(r'\d+', str(result))
        if len(result_nums[0]) > 4:
            asset_list.append(result_nums[0])
    return sorted(dedupe(asset_list))

# fastest according to  http://stackoverflow.com/questions/480214/how-do-you-remove-duplicates-from-a-list-in-python-whilst-preserving-order
def dedupe(num_list):
    seen = set()
    seen_add = seen.add
    return [ x for x in num_list if not (x in seen or seen_add(x))]

search_url = "oil_palm_search.html"
asset_num_list = get_all_asset_nums(search_url)
for asset_num in asset_num_list:
    asset = anm_asset(asset_num)
    if len(asset.asset_num) > 5:
        asset.get_props()
        pdf_dest = "./pdf/" + str(asset.asset_num) + ".pdf"
        if os.path.exists(pdf_dest):
            print pdf_dest, "already exists"
        elif 'pdf_url' in asset.props:
            if not os.path.exists("./pdf/" + str(asset.asset_num) + ".pdf"):
                print "Downloading PDF from", asset.props['pdf_url'], "to ./pdf/"+ str(asset.asset_num)+".pdf" 
                try:
                    rq = urllib2.Request(asset.props['pdf_url'])
                    res = urllib2.urlopen(rq)
                    pdf = open("./pdf/" + str(asset.asset_num) + ".pdf", 'wb')
                    pdf.write(res.read())
                    pdf.close()
                except:
                    print "Failure to download", pdf_url
            else: 
                print "./pdf/" + str(asset.asset_num) + ".pdf already exists!"

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
