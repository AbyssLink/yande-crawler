import json
import os
import random
import time
from datetime import datetime
from multiprocessing.pool import ThreadPool
from urllib.request import url2pathname

import requests
from loguru import logger
from tqdm import tqdm

log_dir = os.path.join(os.getcwd(), 'logs')
if not os.path.exists('logs'):
    os.makedirs("logs")
logger.add(os.path.join('logs', "file_{time}.log"))


class Yande:
    def __init__(self):
        super().__init__()
        self.__api_root: str = "https://yande.re/post.json?"
        self.__begin_time = datetime.now()
        self.__tags: str = ''
        self.__start_page: int = 1
        self.__end_page: int = 1
        self.__max_file_size: int = 20971520
        self.__total_downloads: int = 0
        self.__total_file_size: int = 0
        self.__info: dict = dict()
        self.__is_multiple_process: bool = False
        self.__process_num: int = 5
        self.__storage: str = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'download')
        self.__headers: dict = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/75.0.3770.142 '
                          'Safari/537.36'
        }

    def set_path(self, path_):
        """
        设置下载文件的保存路径
        :param path_:
        """
        if not os.path.exists(path_):
            logger.warning(f"Download Path='{path_}' does not exist, use default path='{self.__storage}'")
        else:
            self.__storage = path_

    def set_multiple_process(self, process_num_):
        """
        设置下载的线程数(1为单线程)
        :param process_num_:
        :return:
        """
        process_num_ = int(process_num_)
        if process_num_ == 1:
            self.__is_multiple_process = False
        else:
            self.__is_multiple_process = True
            self.__process_num = int(process_num_)

    def crawl_pages_by_tag(self, tags_: str, start_page_: int, end_page_: int):
        """
        爬取指定 tag 的指定页数内的图片
        :param tags_:
        :param start_page_:
        :param end_page_:
        """
        self.__tags = tags_.replace(' ', '+')
        self.__start_page = start_page_
        self.__end_page = end_page_

        try:
            self.__begin_time = datetime.now()
            for i in range(self.__start_page, self.__end_page + 1):
                self.crawl_page(i)
            end_time = datetime.now()
            logger.info(
                f"Task complete, all_file_size = {str(round(self.__total_file_size / 1024 / 1024, 2))}MiB, "
                f"used_time = {str(round((end_time - self.__begin_time).total_seconds() / 60, 2))}Minutes, "
                f"average_speed = "
                f"{str(round((self.__total_file_size / 1024) / (end_time - self.__begin_time).total_seconds(), 2))}KiB")
        except KeyboardInterrupt:
            exit(0)

    def crawl_page(self, page_num_: int):
        """
        爬取特定 tag 的单页内的图片
        :param page_num_:
        """
        url = f"{self.__api_root}tags={str(self.__tags)}&api_version=2&page={str(page_num_)}"
        r = requests.get(url, self.__headers)
        status = r.status_code
        if status == 200:
            posts = json.loads(r.content)['posts']
            amount = len(posts)
            logger.info(f"Request API URL = {url}")
            logger.info(f"Page# {page_num_} : {str(amount)} images will be downloaded...")

            if not self.__is_multiple_process:
                for post_info in posts:
                    pic_path = os.path.join(self.__storage, f"{self.__tags}", f"page{page_num_}")
                    if not (os.path.exists(pic_path)):
                        os.makedirs(pic_path)
                    self.retrieve_image(url_=post_info['file_url'], id_=post_info['id'], size_=post_info["file_size"],
                                        path_=pic_path)

            else:
                pic_path = os.path.join(self.__storage, f"{self.__tags}", f"page{page_num_}")
                if not (os.path.exists(pic_path)):
                    os.makedirs(pic_path)
                img_infos = []
                for post_info in posts:
                    img_info = {'id': post_info['id'], 'url': post_info['file_url'], 'path': pic_path,
                                'size': post_info["file_size"]}
                    img_infos.append(img_info)
                ThreadPool(self.__process_num).imap_unordered(self.retrieve_image_simple, img_infos)

        else:
            logger.error(f"HTTP_STATUS: {status}. Failed URL: {url}")
            time.sleep(1)

    def retrieve_image_simple(self, info_: dict):
        """
        下载特定图片（单线程）
        :param info_:
        :return:
        """
        # Timed Sleep
        sleep_time = round(random.random() * 3, 2)
        logger.info(f"Timed sleep for {str(sleep_time)}s")
        time.sleep(sleep_time)

        url_ = info_['url']
        path_ = info_['path']
        size_ = info_['size']
        id_ = info_['id']

        if size_ > self.__max_file_size:
            logger.warning('file size too large, jump over...')
            return None

        logger.info(f"Img# {self.__total_downloads + 1}")
        logger.info(f"Target id = {id_} Size = {str(round(size_ / 1024 / 1024, 2))}MiB")

        r = requests.get(url=url_, headers=self.__headers, stream=True)
        status = r.status_code
        if status == 200:
            file_name = url2pathname(os.path.basename(url_))
            file_path = os.path.join(path_, self.optimize_file_name(file_name))
            self.write_with_progress(file_path, r, size_)
        else:
            logger.error(f"HTTP_STATUS: {status}. Failed URL: {url_}")
            time.sleep(1)

    def retrieve_image(self, url_: str, id_: str, size_: float, path_: str):
        """
        下载特定的图片，progress bar 显示下载进度
        :param url_:
        :param id_:
        :param size_:
        :param path_:
        :return:
        """
        # Exclude images that are too large
        # Images Bigger then self.__max_file_size will not be download
        if size_ > self.__max_file_size:
            logger.warning('file size too large, jump over...')
            return None

        logger.info(f"Img# {self.__total_downloads + 1}")
        logger.info(f"Target id = {id_} Size = {str(round(size_ / 1024 / 1024, 2))}MiB")

        # Timed Sleep
        sleep_time = round(random.random() * 3, 2)
        logger.info(f"Timed sleep for {str(sleep_time)}s")
        time.sleep(sleep_time)

        # Download picture
        r = requests.get(url=url_, headers=self.__headers, stream=True)
        status = r.status_code
        if status == 200:
            file_name = url2pathname(os.path.basename(url_))
            file_path = os.path.join(path_, self.optimize_file_name(file_name))
            self.write_with_progress(file_path, r, size_)
        else:
            logger.error(f"HTTP_STATUS: {status}. Failed URL: {url_}")
            time.sleep(1)

    def write_with_progress(self, file_path_, request_, size_):
        """
        progress bar 显示方法
        :param file_path_:
        :param request_:
        :param size_:
        """
        # Total size in bytes.
        total_size = int(request_.headers.get('content-length', 0))
        block_size = 1024  # 1 Kibibyte
        t = tqdm(total=total_size, unit='iB', unit_scale=True)
        try:
            with open(file_path_, 'wb') as f:
                for data in request_.iter_content(chunk_size=block_size):
                    t.update(len(data))
                    f.write(data)
            self.__total_downloads += 1
            self.__total_file_size += size_
        except Exception as e:
            logger.error(e)
        t.close()
        if total_size != 0 and t.n != total_size:
            logger.error("ERROR, something went wrong")

    @staticmethod
    def optimize_file_name(name_: str):
        """
        优化文件名，替换文件系统不允许的字符
        :param name_:
        :return:
        """
        # Replace Invalid characters
        # Invalid Character list: " * : < > ? / \ |
        # TODO: optimize string replace method
        name_ = name_.replace('/', '_').replace(':', '_').replace('\\', '_'). \
            replace('|', '_').replace('*', '_').replace('?', '_').replace('<', '_').replace('>', '_')
        return name_

    def test_long_filename(self):
        """
        测试方法
        """
        self.__tags = 'aces8492unsung akihara_sekka ass breast_hold doi_tamako feet fujimori_mito hanamoto_yoshika '
        'iyojima_anzu kohagura_natsume koori_chikage masuzu_aki megane naked nipples nogi_wakaba '
        'nogi_wakaba_wa_yuusha_de_aru pubic_hair pussy shiratori_utano takashima_yuuna uesato_hinata uncensored '
        'yuuki_yuuna_wa_yuusha_de_aru yuuki_yuuna_wa_yuusha_de_aru:_hanayui_no_kirameki'
        self.retrieve_image(
            url_='https://files.yande.re/image/57cb51d1f8e85cd99c34af016b687d40/yande.re%20601083%20ass%20breast_hold'
                 '%20doi_tamako%20feet%20iyojima_anzu%20koori_chikage%20masuzu_aki%20megane%20naked%20nipples'
                 '%20nogi_wakaba%20pubic_hair%20pussy%20uesato_hinata%20uncensored.png', id_='601083',
            size_=3097256, path_=self.__storage)


if __name__ == '__main__':
    y = Yande()
    y.test_long_filename()
