# attempting to translate json output into a CSV

import simplejson
import csv

# read the dict
with open('/home/dowcet/python/anm/oil_palm.json', 'r') as infile: 
    data = simplejson.load(infile)

# write it back out
with open('/home/dowcet/python/anm/oil_palm.csv', 'w') as outfile:
    fieldnames = ["asset_no"]
    failures = 0
    for asset in data:
        if fieldnames == ["asset_no"]:
            for key in data[asset]:
                fieldnames.append(key)
            writer = csv.DictWriter(outfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
            writer.writeheader()
        try:
           writer.writerow(data[asset])
        except:
           failures = failures+1
return failures, fieldnames
