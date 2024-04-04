# This script came out of a need to pull ~700 pages worth of json event objects from an API that paginates the results.
# Hitting each page sequentially would take way too long so I leveraged grequests, but grequests could only handle a 100 or so urls at a time.
# Taking the number of total pages and generating a list of lists of these page-specific urls was the key.

import grequests
import requests
import ruamel.yaml
import sys

# grequests can't handle more than 100 or urls at a time, so we break them up into chunks
def generate_lists_of_url_lists(urls):
    list_of_url_lists = []
    sublist = []
    for url in urls:
        sublist.append(url)
        if len(sublist) == 100:
            list_of_url_lists.append(sublist)
            sublist = []
    if sublist:
        list_of_url_lists.append(sublist)
    return list_of_url_lists

url = "https://some-api-with-paginated-results.com/api/documents"
headers = {
    'Authorization': 'Bearer <some-auth-token-if-necessary>'
}
response = requests.request("GET", url, headers=headers)
total_pages = response.json()['page']['totalPages']

urls = []

# Create a list of all the page-specific urls
for page in range(total_pages):
    page += 1
    urls.append(f"https://some-api-with-paginated-results.com/api/documents&page={page}")

url_list_breakdown = generate_lists_of_url_lists(urls)

json_objects = []

# Iterate over the list of url lists, making 'get' requests against each list of urls, and storing the returned json event objects
for url_list in url_list_breakdown:
    rs = (grequests.get(url, headers=headers) for url in url_list)
    objects = grequests.map(rs)
    for object in objects:
        json_objects.append(object.json())

# Writing the json event objects to a yaml file
yaml = ruamel.yaml.YAML()
with open('json-objects.yml', 'w') as outfile:
    yaml.dump(json_objects, outfile)