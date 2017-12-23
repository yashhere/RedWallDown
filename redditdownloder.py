#!/usr/bin/env python

import requests
from bs4 import BeautifulSoup

# link = requests.get("https://www.reddit.com/r/EarthPorn/", stream=True)
# print(link.content)

c = open("result", "r+")
data = c.read()
soup = BeautifulSoup(data)

samples = soup.find_all("a", "title")
print(samples)