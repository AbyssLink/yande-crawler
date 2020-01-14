class Yande:
    def __init__(self, tags_: str, page_: int):
        super().__init__()
        self.__tags: str = tags_.replace(' ', '+')
        self.__url: str = f'https://yande.re/post.json?tags={str(tags_)}&api_version=2&page={str(page_)}'
        self.__page: str = str(page_)
        self.__info: dict = dict()

    def info(self):
        return self.__info

    def url(self):
        return self.__url
