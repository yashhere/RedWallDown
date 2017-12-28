import os
import shutil
import requests
import praw
import argparse
import subprocess
import random
import platform
import sys
from time import sleep
from PIL import Image
from io import BytesIO

wallpaper_directory = '.reddit_wallpapers'
datapath = ""

ARG_MAP = {
    'feh': ['feh', ['--bg-scale'], '%s'],
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
    if desktop_environ and desktop_environ in WM_BKG_SETTERS:
        wp_program, args, filepath = WM_BKG_SETTERS.get(
            desktop_environ, [None, None])
        pargs = [wp_program] + args + [filepath % image_path]
        subprocess.call(pargs)
    elif desktop_environ in ['xfce']:
        os.system(
            "xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor0/image-show -s ''")
        os.system(
            "xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor0/image-path -s '%s'" % image_path)
    else:
        wp_program, args, filepath = WM_BKG_SETTERS['i3']
        pargs = [wp_program] + args + [filepath % image_path]
        subprocess.call(pargs)


def setWallpaperInWindows(image_path):
    SPI_SETDESKWALLPAPER = 20
    ctypes.windll.user32.SystemParametersInfoA(
        SPI_SETDESKWALLPAPER, 0, image_path, 3)


def setWallpaperInMac(image_path):
    osxcmd = 'osascript -e \'tell application "System Events" to set picture of every desktop to "' + image_path + '" \''
    os.system(osxcmd)


def configure():
    global datapath
    datapath = os.path.expanduser('~') + "/" + wallpaper_directory
    if not os.path.exists(datapath):
        os.makedirs(datapath)


def refineURL(url):
    if url.endswith('png', 0, len(url)) or url.endswith('jpg', 0, len(url)):
        return url
    else:
        return ""


def links(subreddit, count, sort_method):
    reddit = praw.Reddit('wallpaper-downloader')
    if sort_method == "new":
        subreddit = reddit.subreddit(subreddit).new(limit=count + 10)
    elif sort_method == "top":
        subreddit = reddit.subreddit(subreddit).top('week', limit=count + 10)
    elif sort_method == "controversial":
        subreddit = reddit.subreddit(
            subreddit).controversial('week', limit=count + 10)

    downloadLinks = []
    for submission in subreddit:
        if count == 0:
            break

        data = {}
        url = refineURL(submission.url)

        if url:
            data['url'] = url
            count = count - 1
        else:
            continue

        data['title'] = submission.title
        data['width'] = submission.preview['images'][0]['source']['width']
        data['height'] = submission.preview['images'][0]['source']['height']
        downloadLinks.append(data)

    return downloadLinks


def downloadWallpaper(link):
    all_images = [int(f.split('.')[0]) for f in os.listdir(
        datapath) if os.path.isfile(os.path.join(datapath, f))]

    if not all_images:
        i = 1
    else:
        i = max(all_images) + 1

    response = requests.get(link['url'], stream=True)
    ext = link['url'].split('.')[-1]
    img = Image.open(BytesIO(response.content))

    if link['width'] < 1920 or link['height'] < 1080:
        return ""

    image_path = datapath + '/' + str(i) + '.' + ext
    with open(image_path, 'wb') as out_file:
        img.save(out_file)
        i = i + 1
    print("Downloaded Image: ", image_path)
    print("Number of images downloaded: %d", i)


def redditWallpapers(subreddit, count, time, sort_method):
    downloadLinks = links(subreddit, count, sort_method)
    print(len(downloadLinks))
    link = ""
    while True:
        if downloadLinks:
            link = random.choice(downloadLinks)
            downloadLinks.remove(link)
            downloadWallpaper(link)

        if link:
            print("Downloaded Wallpaper")
        else:
            continue

        random.shuffle(os.listdir(datapath))
        image_path = datapath + '/' + random.choice(os.listdir(datapath))

        print("Setting up wallpaper %s", image_path)
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

        print("DONE")
        sleep(time * 60)


def main():
    description = "Set Wallpapers downloaded from Reddit"
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument("-r", "--subreddit", default="wallpapers", type=str, nargs='?',
                        help="The subreddit to download wallpapers from, defaults to earthporn")
    parser.add_argument("-t", "--time", type=int, default=15, nargs='?',
                        help="Time (in minutes) for each wallpaper")
    parser.add_argument("-count", "--count", type=int, default=5, nargs='?',
                        help="Number of images to download")
    parser.add_argument("-s", "--sort", default="new", type=str, nargs='?',
                        help="sort methods, values are new, hot, controversial")
    args = parser.parse_args()

    subreddit = args.subreddit
    count = args.count
    duration = args.time
    sort_method = args.sort

    configure()
    redditWallpapers(subreddit, count, duration, sort_method)

if __name__ == '__main__':
    main()
