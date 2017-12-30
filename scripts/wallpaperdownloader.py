import os
import shutil
import requests
import praw
import argparse
import subprocess
import random
import platform
import sys
import ctypes
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


def set_wallpaper_in_linux(image_path):
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


def set_wallpaper_in_windows(image_path):
    SPI_SETDESKWALLPAPER = 20
    ctypes.windll.user32.SystemParametersInfoW(
        SPI_SETDESKWALLPAPER, 0, image_path, 0)


def set_wallpaper_in_osx(image_path):
    osxcmd = 'osascript -e \'tell application "System Events" to set picture of every desktop to "' + image_path + '" \''
    os.system(osxcmd)


def configure():
    global datapath
    datapath = os.path.expanduser('~') + "/" + wallpaper_directory
    if not os.path.exists(datapath):
        os.makedirs(datapath)


def refine_url(url):
    if url.endswith('png', 0, len(url)) or url.endswith('jpg', 0, len(url)):
        return url
    else:
        return ""


def links(subreddit, count, sort_method, width, height):
    reddit = praw.Reddit('wallpaper-downloader')
    if sort_method == "new":
        subreddit = reddit.subreddit(subreddit).new(limit=count + 10)
    elif sort_method == "top":
        subreddit = reddit.subreddit(subreddit).top('week', limit=count + 10)
    elif sort_method == "controversial":
        subreddit = reddit.subreddit(
            subreddit).controversial('week', limit=count + 10)

    download_links = []
    for submission in subreddit:
        if count == 0:
            break

        data = {}
        url = refine_url(submission.url)

        if url:
            data['url'] = url
            count = count - 1
        else:
            continue

        data['title'] = submission.title
        data['width'] = submission.preview['images'][0]['source']['width']
        data['height'] = submission.preview['images'][0]['source']['height']
        download_links.append(data)

    return download_links


def download_wallpaper(link, width, height):
    all_images = [int(f.split('.')[0]) for f in os.listdir(
        datapath) if os.path.isfile(os.path.join(datapath, f))]

    if not all_images:
        i = 1
    else:
        i = max(all_images) + 1

    response = requests.get(link['url'], stream=True)
    ext = link['url'].split('.')[-1]
    img = Image.open(BytesIO(response.content))

    if link['width'] < width or link['height'] < height:
        return ""

    image_path = datapath + '/' + str(i) + '.' + ext
    with open(image_path, 'wb') as out_file:
        img.save(out_file)
        i = i + 1
    print("Downloaded Image: ", image_path)
    # print("Number of images downloaded: %d", i)


def reddit_wallpapers(subreddit, count, time, sort_method, width, height):
    download_links = links(subreddit, count, sort_method, width, height)
    print(len(download_links))
    link = ""
    while True:
        if download_links:
            link = random.choice(download_links)
            download_links.remove(link)
            download_wallpaper(link, width, height)
            # print(len(download_links))

        if not link:
            continue

        random.shuffle(os.listdir(datapath))
        image_path = datapath + '/' + random.choice(os.listdir(datapath))

        print("Setting up wallpaper %s", image_path)
        if platform.system() == 'Darwin':
            set_wallpaper_in_osx(image_path)
        elif platform.system() == 'Windows':
            set_wallpaper_in_windows(image_path)
        elif platform.system() == 'Linux':
            print("Selecting Linux")
            set_wallpaper_in_linux(image_path)
        else:
            print('Platform not recognized')
            sys.exit()

        print("DONE")
        sleep(time * 60)


def main():
    description = "Set Wallpapers downloaded from Reddit"
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument("-r", "--subreddit", default="earthporn", type=str, nargs='?',
                        help="The subreddit to download wallpapers from, defaults to earthporn")
    parser.add_argument("-t", "--time", type=int, default=15, nargs='?',
                        help="Time (in minutes) for each wallpaper")
    parser.add_argument("-c", "--count", type=int, default=15, nargs='?',
                        help="Number of images to download")
    parser.add_argument("-s", "--sort", default="new", type=str, nargs='?',
                        help="sort methods, values are new, hot, controversial")
    parser.add_argument("-w", "--width", default=1920 ,type=int, nargs='?', help="Select minimum width of the images(in px)")
    parser.add_argument("-ht", "--height", default=1080 ,type=int, nargs='?', help="Select minimum height of the images(in px)")
    args = parser.parse_args()

    subreddit = args.subreddit
    count = args.count
    duration = args.time
    sort_method = args.sort
    width = args.width
    height = args.height

    configure()
    reddit_wallpapers(subreddit, count, duration, sort_method, width, height)

if __name__ == '__main__':
    main()
