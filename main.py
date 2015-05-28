#!/usr/bin/env python
#
# The Hylia Anime Music Scraper
#
# Requires :
#  - Python 2.7
#    http://python.org
#  - Requests
#    http://docs.python-requests.org/en/latest/index.html
#  - BeautifulSoup
#    http://www.crummy.com/software/BeautifulSoup/
#
import os
import sys
import time
import threading
import urllib
import random
import requests
import BeautifulSoup
import progressBar

###
# Global Config
###

session  = None
root_dir = os.path.join(os.path.abspath("."), "out")
thread_limit  = 6
current_count = 0

#!# End Config #!#

# Misc Functions

def start_bar(total):
    global current_count
    bar = progressBar.progressBar(total)
    while current_count < total:
        sys.stdout.write("\r[+] %s %d/%d" % (bar.get_bar(current_count), current_count+1, total))
        sys.stdout.flush()
        time.sleep(0.2)
    sys.stdout.write("\r[+] %s %d/%d" % (bar.get_bar(total), total, total))
    sys.stdout.flush()

def sanitize_filename(string):
    bad_chars = ["\\", "/", ":", "*", "?", "\"", "<", ">", "|"]
    for char in bad_chars:
        string = string.replace(char, "_")

    html_elements = {"&amp;": "&",
                     "&quot;": "\"",
                     "&nbsp;": " ",
                     "&raquo;": ""}
    for key in html_elements:
        val = html_elements[key]
        string = string.replace(key, val)

    return string.strip()

def show_status(message):
    sys.stdout.write("[+] %s, " % message)
    sys.stdout.flush()

def get_random_useragent():
    base_agent = "Mozilla/%.1f (Windows; U; Windows NT 5.1; en-US; rv:%.1f.%.1f) Gecko/%d0%d Firefox/%.1f.%.1f"
    return base_agent % ((random.random() + 5),
                         (random.random() + random.randint(1, 8)), random.random(),
                         random.randint(2000, 2100), random.randint(92215, 99999),
                         (random.random() + random.randint(3, 9)), random.random())

# Main Functions

def download_album(album_url):
    global thread_limit, current_count, threshold_time

    # Grab album page
    album_page = session.get(album_url).content
    album_soup = BeautifulSoup.BeautifulSoup(album_page)
    album_name = album_soup.head.title.string
    album_name = album_name.split(" MP3 - Download ")[0]
    album_name = sanitize_filename(album_name)

    print
    print "-" * 80
    print "[+] Downloading album -- %s" % album_name
    print "-" * 80
    print

    # Create album root
    album_root = os.path.join(root_dir, album_name)
    if not os.path.exists(album_root):
        os.mkdir(album_root)

    # Index album art URLs
    show_status("Indexing album art image URLs")
    image_urls = []
    for tag in album_soup.findAll("a"):
        if not tag.find("img") or "album_" not in tag['href']:
            continue
        image_urls.append(tag['href'])
    print "Done"

    # Download album images
    if len(image_urls) == 0:
        print "[+] No album art found ;_;"
    else:
        print "[+] Downloading album art now..."
        current_count = 0
        threading.Thread(target=start_bar, args=(len(image_urls), )).start()
        for url in image_urls:
            while threading.activeCount() >= thread_limit:
                time.sleep(0.1)
            threading.Thread(target=download_image, args=(url, album_root)).start()

        while threading.activeCount() > 1:
            time.sleep(0.1)
        print

    # Index MP3 URls
    show_status("Indexing MP3 page URLs")
    page_urls = []
    for tag in album_soup.findAll("a"):
        if not tag["href"] or not tag["href"].endswith(".mp3"):
            continue
        page_urls.append(tag['href'])
    print "Done"

    # Download MP3s
    if len(page_urls) == 0:
        print "[+] No songs found ;_;"
    else:
        print "[+] Downloading MP3s now..."
        current_count = 0
        threading.Thread(target=start_bar, args=(len(page_urls), )).start()
        for url in page_urls:
            while threading.activeCount() >= thread_limit:
                time.sleep(0.1)
            threading.Thread(target=download_song, args=(url, album_root)).start()

        while threading.activeCount() > 1:
            time.sleep(0.1)
        print



    print
    print "=" * 80

def download_image(image_url, album_root):
    global current_count

    for i in range(3):
        try:
            file_name = image_url.split("/")[-1]
            file_path = os.path.join(album_root, file_name)

            if not os.path.exists(file_path):
                image_data = session.get(image_url).content
                f = open(file_path, "wb")
                f.write(image_data)
                f.close()

        except:
            time.sleep(3)
            continue
        break

    current_count += 1
    
def download_song(page_url, album_root):
    global current_count

    for i in range(3):
        try:
            page = session.get(page_url).content
            soup = BeautifulSoup.BeautifulSoup(page)

            mp3_url = None
            for tag in soup.findAll("a"):
                if not tag['href'] or not "Download to Computer" in str(tag):
                    continue
                mp3_url = tag['href']
                break
            if not mp3_url:
                break

            file_name = mp3_url.split("/")[-1]
            file_name = urllib.unquote(file_name)
            file_path = os.path.join(album_root, file_name)

            if not os.path.exists(file_path):
                image_data = session.get(mp3_url).content
                f = open(file_path, "wb")
                f.write(image_data)
                f.close()

        except:
            time.sleep(3)
            continue
        break

    current_count += 1


if __name__ == '__main__':
    # Set up session and out directory
    session = requests.session()
    session.headers["User-Agent"] = get_random_useragent()
    if not os.path.exists(root_dir): os.mkdir(root_dir)

    # Load album URLs into memory
    albums = open("albums.txt", 'r').read().split("\n")
    albums = filter(len, albums)

    # Start downloading albums
    for album_url in albums:
        download_album(album_url)

    # All done
    print
    print "-" * 85
    print "[+] All done..."
    raw_input("[+] Press enter to exit...")