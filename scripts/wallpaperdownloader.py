import os
import shutil
import requests
import praw
import argparse
import subprocess
import random
import platform
import sys
import time
from PIL import Image
from io import BytesIO

wallpaper_directory = '.reddit_wallpapers'
datapath = ""

ARG_MAP = {
    'feh': ['feh', ['--bg-center'], '%s'],
    'gnome': ['gsettings',
                ['set', 'org.gnome.desktop.background', 'picture-uri'],
                'file://%s'],
    'cinnamon': ['gsettings',
                    ['set', 'org.cinnamon.desktop.background', 'picture-uri'],
                    'file://%s'],
    'mate': ['gsettings',
              ['set', 'org.mate.desktop.background', 'picture-uri'],
              'file://%s']
}

WM_BKG_SETTERS = {
    'spectrwm': ARG_MAP['feh'],
    'scrotwm': ARG_MAP['feh'],
    'wmii': ARG_MAP['feh'],
    'i3': ARG_MAP['feh'],
    'awesome': ARG_MAP['feh'],
    'awesome-gnome': ARG_MAP['gnome'],
    'gnome': ARG_MAP['gnome'],
    'ubuntu': ARG_MAP['gnome'],
    'unity': ARG_MAP['gnome'],
    'cinnamon': ARG_MAP['cinnamon'],
    'mate': ARG_MAP['mate']
}

def setWallpaperInLinux(image_path):
    desktop_environ = os.environ.get('DESKTOP_SESSION', '')
    print("desktop_environ is: %s" % desktop_environ)
    if desktop_environ and desktop_environ in WM_BKG_SETTERS:
        wp_program, args, filepath = WM_BKG_SETTERS.get(desktop_environ, [None, None])
        pargs = [wp_program] + args + [filepath % image_path]
        subprocess.call(pargs)
    elif desktop_environ in ['xfce']:
        os.system("xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor0/image-show -s ''")
        os.system("xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor0/image-path -s '%s'" % image_path)
    else:
        wp_program, args, filepath = WM_BKG_SETTERS['i3']
        pargs = [wp_program] + args + [filepath % image_path]
        subprocess.call(pargs)

def setWallpaperInWindows(image_path):
    SPI_SETDESKWALLPAPER = 20
    ctypes.windll.user32.SystemParametersInfoA(SPI_SETDESKWALLPAPER, 0, image_path, 3)

def setWallpaperInMac(image_path):
    osxcmd = 'osascript -e \'tell application "System Events" to set picture of every desktop to "' + image_path + '" \''
    os.system(osxcmd)

def configure():
    global datapath
    datapath = os.path.expanduser('~') + "/" + wallpaper_directory
    # print(datapath)
    if not os.path.exists(datapath):
        os.makedirs(datapath)

def refineURL(url):
    if url.endswith('png', 0, len(url)) or url.endswith('jpg', 0, len(url)):
        return url
    else:
        return ""

def downloadWallpapers(subreddit, count):
    reddit = praw.Reddit('bot1', user_agent='testscript by /u/im_y')
    subreddit = reddit.subreddit(subreddit).hot(limit=count)
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

    i = 1
    for link in downloadLinks:
        print("--------------------------------------------------------------------")
        print("Downloading image - ", link['title'])
        response = requests.get(link['url'], stream=True)
        ext = link['url'].split('.')[-1]
        img = Image.open(BytesIO(response.content))
        # print(img.__dict__.keys())
        if link['width'] < 2000 or link['height'] < 1300:
            continue

        image_path = datapath + '/' + 'img' + str(i) + '.' + ext
        print(image_path)
        with open(image_path, 'wb') as out_file:
            img.save(out_file)
            i = i + 1

    print("Number of images downloaded: %d", i)
    print("finished downloading wallpapers")

def redditWallpapers(subreddit, count, time):
    downloadWallpapers(subreddit, count)

    image_path = datapath + '/' + random.choice(os.listdir(datapath))

    print("Selected Image %s" % image_path)
    if platform.system() == 'Darwin':
        setWallpaperInMac(image_path)
    elif platform.system() == 'Windows':
        setWallpaperInWindows(image_path)
    elif platform.system() == 'Linux':
        print("Selecting Linux")
        setWallpaperInLinux(image_path)
    else:
        print('Platform not recognized')
        sys.exit()

def main():
    description = "Set trending reddit images as wallpapers"
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument("-r", "--subreddit", default="wallpapers", type=str, nargs='?',
                        help="The subreddit to download wallpapers from, defaults to earthporn")
    parser.add_argument("-t", "--time", type=int, default=15, nargs='?',
                        help="Time (in minutes) for each wallpaper")
    parser.add_argument("-count", "--count", type=int, default=20, nargs='?',
                        help="Number of images to download")
    args = parser.parse_args()

    subreddit = args.subreddit
    count = args.count
    duration = args.time

    configure()
    redditWallpapers(subreddit, count, duration)

if __name__ == '__main__':
    main()
