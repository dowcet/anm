import os
import re
import urllib2
import requests
from bs4 import BeautifulSoup as BS

class anm_asset:
    "A class to represent an asset found at http://ofa.arkib.gov.my"
    def __init__(self, asset_num):
        self.asset_num = asset_num
        self.page_url = "http://ofa.arkib.gov.my/ofa/group/asset/"+str(asset_num)
        self.page_file = "./asset_pages/"+str(asset_num)+".html"
        self.props = {}

    def download_page(self):
        if not os.path.exists("./asset_pages"):
            print "making asset_pages folder"
            os.makedirs("./asset_pages")
        print "Fetching", asset.page_url 
        try:
            asset_page_response = requests.get(asset.page_url, timeout=30)
            with open(asset.page_file, "wb") as page:
                page.write(asset_page_response.text)
        except requests.exceptions.Timeout:
            print(asset.page_url,'Timed Out!')
        except requests.exceptions.ConnectionError:
            print(asset.page_url,'Connection Error!')
        except:
            print "Could not write", asset.page_file

    def get_props(self):
        # make the folder for asset page files if it doesn't exist
        if not os.path.exists(asset.page_file):
            asset.download_page()
        # read the asset page file into BS
        print asset.page_file
        if os.path.exists(asset.page_file):
            asset_page = BS(open(asset.page_file))
            # get the URL of the asset PDF
            try:
                asset.props["pdf_url"] = re.search("(?P<url>http?://[^\s]+)", asset_page.find('iframe')['src']).group("url")
                print "Pdf for asset", asset.asset.num, "is available at", asset.props["pdf_url"]
            except:
                print "No PDF info found for asset", asset.asset_num
            try:
                key = asset_page.find("legend", text="Butiran Bahan").next_sibling.next_sibling.tr.td.text
                content = asset_page.find("legend", text="Butiran Bahan").next_sibling.next_sibling.tr.td.next_sibling.next_sibling.next_sibling.next_sibling.text
                print key, content
            except:
                print "No table row text found for", asset.asset_num
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
