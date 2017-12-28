# Reddit Wallpaper Downloader
Automatically fetches the latest, top trending and high quality images from reddit and sets them as your desktop wallpaper!

![]()

## Installation
```bash
git clone https://github.com/yashhere/RedWallDown
cd RedWallDown
python setup.py install
```

## Usage
```bash
redwalldown
```

### Default Behaviour
* Downloads wallpapers from 'earthporn' subreddit.
* Downloads 15 wallpapers at a time.
* Does not overwrite wallpapers already downloaded.
* Changes wallpaper at an interval of 15 minutes.
* Downloads wallpapers from 'new' category.
* Downloads images of resolution greater than 1920x1080.

### Options Available
To select top 25 controversial wallpapers from 'spaceporn' subreddit, and set time duration of 10 minutes
```bash
redwalldown -r spaceporn -t 10 -c 25 -s controversial
```

#### Other Options
```bash
usage: redwalldown [-h] [-r [SUBREDDIT]] [-t [TIME]] [-c [COUNT]] [-s [SORT]]

Set Wallpapers downloaded from Reddit

optional arguments:
  -h, --help            show this help message and exit
  -r [SUBREDDIT], --subreddit [SUBREDDIT]
                        The subreddit to download wallpapers from, defaults to
                        earthporn
  -t [TIME], --time [TIME]
                        Time (in minutes) for each wallpaper
  -c [COUNT], --count [COUNT]
                        Number of images to download
  -s [SORT], --sort [SORT]
                        sort methods, values are new, hot, controversial
```

### Automatically start the script on startup
Run this command in terminal
```bash
crontab -e -u ${USER}
```

Now add the following line to your cron file
```bash
@reboot redwalldown
```

### License
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


