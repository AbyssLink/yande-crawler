import json
import logging
import os
import random
import time
from datetime import datetime
from urllib.parse import urlparse

import requests
from tqdm import tqdm

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
    """

    :param tags_:
    :param start_:
    :param end_:
    :param path_:
    """
    if not os.path.exists(path_):
        logger.warning(f"Download Path='{path_}' does not exist, use default path={default_path}\n")
        path_ = default_path
        if not os.path.exists(default_path):
            os.makedirs("download")
    try:
        now = datetime.now()
        count = 1
        file_size = 0
        for i in range(start_, end_ + 1):
            yande = Yande(tags_=tags_, page_=i)
            logger.info(f"Request API URL = {yande.url()}")
            r = requests.get(yande.url(), headers=headers)
            status = r.status_code
            if status == 200:
                posts = json.loads(r.content)['posts']
                logger.info(f"Page# {i} : {str(len(posts))} images will be downloaded...\n")

                for post_info in posts:
                    logger.info(f"Img# {count}")
                    download_pic(url_=post_info['file_url'], id_=post_info['id'], tags_=post_info['tags'],
                                 size_=post_info["file_size"], path_=path_)
                    count = count + 1
                    file_size = file_size + post_info["file_size"]
                end = datetime.now()
                logger.info(
                    f"Task complete, all_file_size = {str(round(file_size / 1024 / 1024, 2))}MiB, "
                    f"used_time = {str(round((end - now).total_seconds() / 60, 2))}Minutes, "
                    f"average_speed = {str(round((file_size / 1024) / (end - now).total_seconds(), 2))}KiB")
            else:
                logger.error(f"HTTP_STATUS: {status}. Can't get yande.re post API list")
                time.sleep(1)
    except KeyboardInterrupt:
        exit(0)


def download_pic(url_: str, path_: str, tags_: str, id_: str, size_: float):
    """

    :param url_:
    :param path_:
    :param tags_:
    :param id_:
    :param size_:
    """
    sleep_time = round(random.random() * 10, 2)
    logger.info(f"Timed sleep for {str(sleep_time)}s")
    time.sleep(sleep_time)
    logger.info(f"Start downloading id = {id_} Size = {str(round(size_ / 1024 / 1024, 2))}MiB, please wait.")

    r = requests.get(url=url_, headers=headers, stream=True)
    status = r.status_code

    if status == 200:
        # Total size in bytes.
        total_size = int(r.headers.get('content-length', 0))
        block_size = 1024  # 1 Kibibyte
        t = tqdm(total=total_size, unit='iB', unit_scale=True)

        file_extension = os.path.splitext(urlparse(url_).path)[1]
        base_name = f"yande.re {id_} {optimize_tags(tags_=tags_)}{file_extension}"
        file_path = os.path.join(path_, base_name)

        try:
            with open(file_path, 'wb') as f:
                for data in r.iter_content(block_size):
                    t.update(len(data))
                    f.write(data)
        except Exception as e:
            logger.error(e)

        t.close()
        if total_size != 0 and t.n != total_size:
            logger.error("ERROR, something went wrong")

        logger.info(f"Download successfully.\n")
    else:
        logger.error(f"HTTP_STATUS: {status}. file in {url_} failed to download. "
                     f"Retry in 1 sec. {url_}")
        time.sleep(1)


def save_info(info_: dict, path_: str):
    path_ = os.path.join(path_, str(datetime.now().strftime(f"%m-%d-%Y %H_%M_%S")))


def optimize_tags(tags_: str):
    """
    optimize the tags string, prevent path errors and filenames from being too long
    :param tags_:
    """
    tags_ = tags_.replace('/', '_')
    tags_ = tags_.replace(':', '_')
    # Limit file name length for 120 character
    if len(tags_) <= 120:
        return tags_
    else:
        tag_list = tags_.split(' ')
        new_tags = ''
        index = 0
        while len(new_tags) < 120:
            if new_tags != '':
                new_tags = new_tags + ' ' + tag_list[index]
            else:
                new_tags = new_tags + tag_list[index]
            index = index + 1
        return new_tags


def test():
    download_pic(
        url_='https://files.yande.re/image/57cb51d1f8e85cd99c34af016b687d40/yande.re%20601083%20ass%20breast_hold'
             '%20doi_tamako%20feet%20iyojima_anzu%20koori_chikage%20masuzu_aki%20megane%20naked%20nipples'
             '%20nogi_wakaba%20pubic_hair%20pussy%20uesato_hinata%20uncensored.png', id_='601083',
        tags_='aces8492unsung akihara_sekka ass breast_hold doi_tamako feet fujimori_mito hanamoto_yoshika '
              'iyojima_anzu kohagura_natsume koori_chikage masuzu_aki megane naked nipples nogi_wakaba '
              'nogi_wakaba_wa_yuusha_de_aru pubic_hair pussy shiratori_utano takashima_yuuna uesato_hinata uncensored '
              'yuuki_yuuna_wa_yuusha_de_aru yuuki_yuuna_wa_yuusha_de_aru:_hanayui_no_kirameki',
        size_=3097256, path_=default_path)


if __name__ == "__main__":
    tags = input("Search Tags = ")
    start_page = input("Start Page = ")
    end_page = input("End Page = ")
    path = input("Download Path = ")
    main_download(tags_=tags, start_=int(start_page), end_=int(end_page), path_=path)
