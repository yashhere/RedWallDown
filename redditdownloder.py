#!/usr/bin/env python

import requests
import praw
import shutil

def refineURL(url):
    if url.endswith('png', 0, len(url)) or url.endswith('jpg', 0, len(url)):
        return url
    else:
        return ""

reddit = praw.Reddit('bot1', user_agent='testscript by /u/im_y')

subreddit = reddit.subreddit('earthporn').hot(limit=10)
# print(subreddit.__dict__.keys())

downloadLinks = []
for submission in subreddit:
    downloadLinks.append(submission.url)

len = len(downloadLinks)
response = requests.get(downloadLinks[0], stream=True)
with open('img' + '.' + 'jpg', 'wb') as out_file:
    shutil.copyfileobj(response.raw, out_file)

# print(downloadLinks)