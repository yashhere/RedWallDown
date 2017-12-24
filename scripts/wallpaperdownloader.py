import os
import shutil
import requests
import praw
import click
# import pillow 
from PIL import Image
from io import BytesIO

def configure():
    wallpaper_directory = '.reddit_wallpapers/'
    datapath = os.path.expanduser('~') + "/" + wallpaper_directory
    if not os.path.exists(datapath):
        os.makedirs(datapath)

def refineURL(url):
    if url.endswith('png', 0, len(url)) or url.endswith('jpg', 0, len(url)):
        return url
    else:
        return ""

@click.command()
@click.option('-c', '--count', default=20, help='number of images to download', nargs=1)
@click.option('-t', '--time', default=15, help='Time (in minutes) for each wallpaper', nargs=1)
@click.option('-r', '--subreddit', nargs=1, default="earthporn", help="The subreddit to download wallpapers from, defaults to earthporn")
def wallpaperdownloader(subreddit, count, time):
    reddit = praw.Reddit('bot1', user_agent='testscript by /u/im_y')
    subreddit = reddit.subreddit(subreddit).hot(limit=6)
    # print(subreddit.__dict__.keys())

    downloadLinks = []
    for submission in subreddit:
        data = {}
        url = refineURL(submission.url)
        
        if url:
            data['url'] = url
        else:
            continue

        data['title'] = submission.title
        data['width'] = submission.preview['images'][0]['source']['width']
        data['height'] = submission.preview['images'][0]['source']['height']
        downloadLinks.append(data)

    print(downloadLinks)

    i = 1
    for link in downloadLinks:
        print("--------------------------------------------------------------------")
        print("Downloading image - ", link['title'])
        response = requests.get(link['url'], stream=True)
        ext = link['url'].split('.')[-1]
        img = Image.open(BytesIO(response.content))
        # print(img.__dict__.keys())
        print(img.size)
        if link['width'] < 1280 or link['height'] < 960:
            continue

        with open('img' + str(i) + '.' + ext, 'wb') as out_file:
            img.save(out_file)
            i = i + 1

if __name__ == '__main__':
    configure()
    wallpaperdownloader()