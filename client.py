from yande import Yande

if __name__ == "__main__":
    tags = input("Search Tags = ")
    start_page = input("Start Page = ")
    end_page = input("End Page = ")
    path = input("Download Path = ")
    yande = Yande(tags_=tags)
    yande.set_path(path_=path)
    yande.crawl_pages_by_tag(start_=int(start_page), end_=int(end_page))
