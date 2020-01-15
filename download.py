import json
import logging
import os
import random
import time
from datetime import datetime
from urllib.parse import urlparse

import requests

from yande import Yande

logger = logging.getLogger('yande.re')
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler('yande.log')
fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)

headers: dict = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/75.0.3770.142 '
                  'Safari/537.36'
}

default_path: str = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'download')


def main_download(tags_: str, start_: int, end_: int, path_: str):
    if not os.path.exists(path_):
        logger.info("Path doesn't exist, use default path")
        path_ = default_path
        if not os.path.exists(default_path):
            os.makedirs("download")
    try:
        for i in range(start_, end_ + 1):
            yande = Yande(tags_=tags_, page_=i)
            logger.info(f"API URL = {yande.url()}")
            r = requests.get(yande.url(), headers=headers)
            status = r.status_code
            if status == 200:
                posts = json.loads(r.content)['posts']
                count = 1
                for post_info in posts:
                    logger.info(f"# {count}")
                    download_pic(url_=post_info['file_url'], id_=post_info['id'], tags_=post_info['tags'],
                                 size_=post_info["file_size"], path_=path_)
                    count = count + 1
            else:
                logger.error("Can't get yande.re post API list")
                time.sleep(1)
    except KeyboardInterrupt:
        exit(0)


def download_pic(url_: str, path_: str, tags_: str, id_: str, size_: float):
    sleep_time = round(random.random() * 10, 2)
    logger.info(f"Timed sleep for {str(sleep_time)}s")
    time.sleep(sleep_time)
    logger.info(f"Start Downloading id = {id_} Size = {str(round(size_ / 1024 / 1024, 2))}MB, please wait....")

    r = requests.get(url_, headers=headers)
    status = r.status_code

    if status == 200:
        file_extension = os.path.splitext(urlparse(url_).path)[1]
        base_name = f"yande.re {id_} {tags_.replace('/', '_')}{file_extension}"
        file_path = os.path.join(path_, base_name)
        with open(file_path, 'wb') as f:
            f.write(r.content)
        logger.info(f"Download Complete, Save path {file_path}")
    else:
        logger.error(f"HTTP_STATUS: {status}. file in {url_} failed to download. "
                     f"Retry in 1 sec. {url_}")
        time.sleep(1)


def save_info(info_: dict, path_: str):
    path_ = os.path.join(path_, str(datetime.now().strftime(f"%m-%d-%Y %H_%M_%S")))


if __name__ == "__main__":
    tags = input("Search Tags = ")
    start_page = input("Start Page = ")
    end_page = input("End Page = ")
    path = input("Download Path = ")
    main_download(tags_=tags, start_=int(start_page), end_=int(end_page), path_=path)
