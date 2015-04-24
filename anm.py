#!/usr/bin/env python

import argparse
import os
import re
import urllib2
import requests
import csv
from bs4 import BeautifulSoup as BS

class anm_asset:
    "A class to represent an asset found at http://ofa.arkib.gov.my"
    def __init__(self, asset_no):
        self.asset_no = asset_no
        self.page_url = "http://ofa.arkib.gov.my/ofa/group/asset/"+str(asset_no)
        self.page_file = "./asset_pages/"+str(asset_no)+".html"
        # Currently using this dictionary for pdf_url only because I haven't figure out how to iterate a dictionary when it is an attribute 
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
            pdf_url = "Not Found"
        if not pdf_url == "Not Found":
            print "Pdf for asset", self.asset_no, "is available at", pdf_url
        return pdf_url

    def parse_table_data(self):
        #print "Parsing table data..."
        props_dict = {}
        #target_keys_list = ['Tajuk', 'Penerimaan', 'Media Asal', 'Sumber', 'Tarikh', 'Jenis Rekod', 'Kategori', 'Subkategori', 'Lokasi']
        target_keys_dict = {'Tajuk': 'title', 'No Penerimaan': 'request_num', 'Media Asal': 'media', 'Sumber': 'source', 'Tarikh': 'date', 'Jenis Rekod': 'rec_type', 'Kategori': 'cat', 'Subkategori': 'subcat', 'Lokasi': 'location', 'Deskripsi': 'description', 'Subjek': 'subject', 'Mukasurat Akses': 'access_page', 'Hit' : 'hits'}
        table_data = self.page_soup.find("legend", text="Butiran Bahan").next_sibling.next_sibling.find_all("td")
        # get a clean list of results 
        hit_list = []
        for cell in table_data:
            cell_text = " ".join(cell.text.split())
            if cell_text == '':
                cell_text = "Not Found"
            if cell_text != ":":
                hit_list.append(cell_text)
        # make a dictionary from the cleaned list
        count = 0
        for hit in hit_list:
            count = count + 1
            if count % 2 != 0:
                new_key = hit
            else:
                props_dict[target_keys_dict[new_key]] = hit
        props_dict["pdf_url"] = self.get_pdf_url()
        return props_dict

    def get_props(self, args):
        props_dict = {}
        #print "getting properties..."
        # make sure we have the file, download if needed
        downloaded = self.download_page()
        # read the asset page file into BS
        if downloaded and os.path.exists(self.page_file):
            #print "reading", self.page_file
            self.page_soup = BS(open(self.page_file))
            try:
                props_dict = self.parse_table_data()
            except:
                print "could not parse table data!"
                props_dict["failure"] = "could not parse"
        else:
            print "could not find file!"
            props_dict["failure"] = "file missing!"
        return props_dict

### end methods of anm_asset ###


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

def dump_search_to_csv(search_file_name):
    asset_no_list = parse_search_page(search_file_name)
    with open('assets.csv', 'w') as outfile:
        # 1) first write the column headings
        # 1.a) this is not a good way to do this, but for a quick fix I am pasting the following dict from above 
        target_keys_dict = {'Tajuk': 'title', 'No Penerimaan': 'request_num', 'Media Asal': 'media', 'Sumber': 'source', 'Tarikh': 'date', 'Jenis Rekod': 'rec_type', 'Kategori': 'cat', 'Subkategori': 'subcat', 'Lokasi': 'location', 'Deskripsi': 'description', 'Subjek': 'subject', 'Mukasurat Akses': 'access_page', 'Hit' : 'hits'}
        # 1.b) translate this dict into a list, adding other columns before and after 
        fieldnames = ["asset_no"]
        for key in target_keys_dict:
            fieldnames.append(target_keys_dict[key])
        fieldnames.append('pdf_url')
        # 1.c) finally write the column headings to the file
        writer = csv.DictWriter(outfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        # 2) now add each asset to the csv file
        print "Looking for", len(asset_no_list), "assets..."
        for asset_no in asset_no_list:
            # get props for asset
            temp_asset = anm_asset(asset_no)
            temp_prop_dict = temp_asset.get_props()
            # next two lines didn't work, need to find out why
            #if 'pdf_url' in temp_asset.props and not pdf_check(temp_asset):
               # download_pdf(temp_asset)
            # include asset_no to dict
            if "failure" in temp_prop_dict:
                print "skipping asset", asset_no+":", temp_prop_dict["failure"]
            else:
                try:
                    temp_prop_dict["asset_no"] = asset_no
                    writer.writerow(temp_prop_dict)
                except:
                    raise # was: print asset_no, "failed!"

def busted_parse_search_page(search_file, args):
    # 1) parse search results 
    asset_no_list = parse_search_results(search_file, args)
    # 2) declare all asset objects
    for asset_no in asset_no_list:
        asset = anm_asset(asset_no, args)
    # 3) get properties of each object, downloading asset page if no local copy is found
    if len(asset.asset_no) > 5:
        asset.get_props(args)
        # 4) download pdf if none locally
        if not pdf_check(asset) and not args.local:
            download_pdf(asset)
        else: 
            print "./pdf/" + str(asset.asset_no) + ".pdf already exists!"

#def fetch_search(search_string):

# I should figure out why the duplicates are happening, but for now...
# fastest way to remove duplicates from a list according to  http://stackoverflow.com/questions/480214/how-do-you-remove-duplicates-from-a-list-in-python-whilst-preserving-order
def dedupe(num_list):
    seen = set()
    seen_add = seen.add
    return [ x for x in num_list if not (x in seen or seen_add(x))]

def download_asset_page(asset):
    if os.path.exists(asset.page_file):
        download_success = True
    else:
        download_success = False
        if not os.path.exists("./asset_pages"):
            print "making asset_pages folder"
            os.makedirs("./asset_pages")
        print "Fetching", asset.page_url 
        try:
            asset_page_response = requests.get(asset.page_url, timeout=30)
            with open(asset.page_file, "wb") as page:
                page.write(asset_page_response.text)
                download_success = True
        except requests.exceptions.Timeout:
            #download_success = False
            print(asset.page_url,'Timed Out!')
        except requests.exceptions.ConnectionError:
            #download_success = False
            print(asset.page_url,'Connection Error!')
        except:
            #download_success = False
            print "Could not write", asset.page_file
    return download_success

def parse_search_results(search_file_name):
    asset_list = []
    result_soup = BS(open(search_file_name))
    hrefs = result_soup.find_all(href=re.compile("asset"))
    for result in hrefs:
        result_nums = re.findall(r'\d+', str(result))
        if len(result_nums[0]) > 4:
            asset_list.append(result_nums[0])
    return sorted(dedupe(asset_list))

def parse_args():
    parser = argparse.ArgumentParser(
    description='Search records at ANM and save results to a csv file. By default html search results and individual asset pages are also stored locally.')
    parser.add_argument('--search_string', help='string to search')
    parser.add_argument('--search_file_name', help='custom local filename for search file; default is "<search_string>.html"')
    parser.add_argument("-l", "--local", help="process local files only, no search or download",action="store_true")
    parser.add_argument("-u", "--unlimited", help="Do not limit to first 5,000 results",action="store_true")
    parser.add_argument("-v", "--verbose", help="extra verbose output",action="store_true")
    # MAYBE: parser.add_argument("-r", "--remote", help="do not save 
    # search or asset pages locally")  
    args = parser.parse_args()
    return args

def get_search_file_name(args):
    if args.search_file_name == None:
        if ".html" in args.search_string:
            search_file_name = "./search_pages/"+args.search_string
        else:
            search_file_name = "./search_pages/"+args.search_string+".html"
        if " " in search_file_name:
            search_file_name = search_file_name.replace(" ","_")
    else:
        search_file_name = args.search_file_name
    return search_file_name

def search_needed(search_file_name, args):
    if os.path.exists(search_file_name):
       needed = False
       print search_file_name, "found."
    else:
        needed = True
        if args.local:
            print "Search file not found in local mode. Cannot proceed. Run without -l to search via http."
    return needed

def do_search(search_file_name, args):
    if args.verbose:
        print "doing search"
    if args.unlimited:
        search_url = "http://ofa.arkib.gov.my/ofa/group/index?OfaSolr_page=1&pageSize=10000000000"
    else:
        search_url = "http://ofa.arkib.gov.my/ofa/group/index?OfaSolr_page=1&pageSize=5000"
    query = "q="+(args.search_string.replace(" ","+"))
    print "Posting search..."
    try:
        response = requests.post(search_url, data=query)
        with open(target_file, "wb") as page:
            page.write(response.text)
    except requests.exceptions.Timeout:
        print(search_file_name,'Timed Out!')
    except requests.exceptions.ConnectionError:
        print(search_file_name,'Connection Error!')
    except:
        print "Could not write", search_file_name
    
if __name__ == '__main__':
    try:
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
    except:
        print "Running from", os.getcwd()
    # 1) Ensure that we have a search string
    args = parse_args()
    print args
    if args.search_string == None:
        args.search_string = raw_input("Please enter a search string or path to a search results file: ")
    # 2) Ensure that we have a local search page filename
    search_file_name = get_search_file_name(args)
    # 3) pull search page from the web if needed
    if search_needed(search_file_name, args):
        do_search(search_file_name, args)
    # 4) parse the search results to get a list of asset numbers
    asset_list = parse_search_results(search_file_name)
    print asset_list
