import os
import shutil
import requests
import praw
import click
import subprocess
from PIL import Image
from io import BytesIO

wallpaper_directory = '.reddit_wallpapers/'
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
    datapath = os.path.expanduser('~') + "/" + wallpaper_directory
    if not os.path.exists(datapath):
        os.makedir(datapath)

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

        with open(datapath + '/' + 'img' + str(i) + '.' + ext, 'wb') as out_file:
            img.save(out_file)
            i = i + 1

if __name__ == '__main__':
    datapath = configure()
    wallpaperdownloader()