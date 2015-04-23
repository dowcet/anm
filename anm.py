import os
import re
import urllib2
import requests
import json
from bs4 import BeautifulSoup as BS

class anm_asset:
    "A class to represent an asset found at http://ofa.arkib.gov.my"
    def __init__(self, asset_no):
        self.asset_no = asset_no
        self.page_url = "http://ofa.arkib.gov.my/ofa/group/asset/"+str(asset_no)
        self.page_file = "./asset_pages/"+str(asset_no)+".html"
        self.props = {}

### start methods of anm_asset ###

    def download_page(self):
        if os.path.exists(self.page_file):
            download_success = True
        else:
            download_success = False
            if not os.path.exists("./asset_pages"):
                print "making asset_pages folder"
                os.makedirs("./asset_pages")
            print "Fetching", self.page_url 
            try:
                asset_page_response = requests.get(self.page_url, timeout=30)
                with open(self.page_file, "wb") as page:
                    page.write(asset_page_response.text)
                download_success = True
            except requests.exceptions.Timeout:
                #download_success = False
                print(self.page_url,'Timed Out!')
            except requests.exceptions.ConnectionError:
                #download_success = False
                print(self.page_url,'Connection Error!')
            except:
                #download_success = False
                print "Could not write", self.page_file
        return download_success

    def get_pdf_url(self):
        try:
            pdf_url = re.search("(?P<url>http?://[^\s]+)", self.page_soup.find('iframe')['src']).group("url")
        except:
            #print "No PDF info found for asset", self.asset_no
            pdf_url = ""
        if not pdf_url == "":
            print "Pdf for asset", self.asset_no, "is available at", pdf_url
        return pdf_url

    def parse_table_data(self):
        #print "Parsing table data..."
        props_dict = {}
        target_keys_list = ['Tajuk', 'Penerimaan', 'Media Asal', 'Sumber', 'Tarikh', 'Jenis Rekod', 'Kategori', 'Subkategori', 'Lokasi']
        target_keys_dict = {'Tajuk': 'title', 'Penerimaan': 'request_num', 'Media Asal': 'media', 'Sumber': 'source', 'Tarikh': 'date', 'Jenis Rekod': 'rec_type', 'Kategori': 'cat', 'Subkategori': 'subcat', 'Lokasi': 'location'}
        table_data = self.page_soup.find("legend", text="Butiran Bahan").next_sibling.next_sibling.find_all("td")
        key_found = False
        for cell in table_data:
            cell_text = " ".join(cell.text.split())
            if key_found == False:
                for key in target_keys_list:
                    if key_found == False:
                        if key in cell_text:
                            new_key = key
                            key_found = True
            elif not re.search('^ +', cell_text) and not re.search('^:+', cell_text) and cell_text != "":
                #print target_keys_dict[new_key]+":", cell_text
                props_dict[target_keys_dict[new_key]] = cell_text
                key_found = False
        props_dict["pdf_url"] = self.get_pdf_url()
        return props_dict

    def get_props(self):
        #print "getting properties..."
        # make sure we have the file, download if needed
        downloaded = self.download_page()
        # read the asset page file into BS
        if downloaded and os.path.exists(self.page_file):
            print "reading", self.page_file
            self.page_soup = BS(open(self.page_file))
            try:
                props_dict = self.parse_table_data()
            except:
                print "could not parse table data!"
                props_dict = "fail!"
        return props_dict

### end methods of anm_asset ###

def get_all_asset_nos(search_url):
    print "getting list of asset numbers"
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

# I should figure out why the duplicates are happening, but for now...
# fastest way to remove duplicates from a list according to  http://stackoverflow.com/questions/480214/how-do-you-remove-duplicates-from-a-list-in-python-whilst-preserving-order
def dedupe(num_list):
    seen = set()
    seen_add = seen.add
    return [ x for x in num_list if not (x in seen or seen_add(x))]

def pdf_check(asset):
    pdf_dest = "./pdf/" + str(asset.asset_no) + ".pdf"
    if os.path.exists(pdf_dest):
        print pdf_dest, "already exists"
    elif 'pdf_url' in asset.props:
        if os.path.exists("./pdf/" + str(asset.asset_no) + ".pdf"):
            return True
        else:
            return False

def download_pdf(asset):            
        print "Downloading PDF from", asset.props['pdf_url'], "to ./pdf/"+ str(asset.asset_no)+".pdf" 
        try:
            rq = urllib2.Request(asset.props['pdf_url'])
            res = urllib2.urlopen(rq)
            pdf = open("./pdf/" + str(asset.asset_no) + ".pdf", 'wb')
            pdf.write(res.read())
            pdf.close()
        except:
            print "Failure to download", pdf_url

def process_search_page(search_url):
    # 1) parse search results 
    search_url = "oil_palm_search.html"
    asset_no_list = get_all_asset_nos(search_url)
    # 2) declare all asset objects
    for asset_no in asset_no_list:
        asset = anm_asset(asset_no)
    # 3) get properties of each object, downloading asset page if no local copy is found
    if len(asset.asset_no) > 5:
        asset.get_props()
        # 4) download pdf if none locally
        if not pdf_check(asset):
            download_pdf(asset)
        else: 
            print "./pdf/" + str(asset.asset_no) + ".pdf already exists!"

def dump_from_search(search_url):
    asset_no_list = get_all_asset_nos(search_url)
    # a list of dictionaries, each holding the metadata for an asset
    asset_dict= {}
    with open('assets.json', 'w') as outfile: 
        json.dump([], outfile)
    for asset_no in asset_no_list:
        temp_asset = anm_asset(asset_no)
        temp_dict = temp_asset.get_props() 
        asset_dict[asset_no] = temp_dict
    with open('assets.json', 'w') as dumpfile:    
        json.dump(asset_dict, dumpfile)
