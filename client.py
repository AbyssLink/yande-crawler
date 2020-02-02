from yande import Yande

if __name__ == "__main__":
    tags = input("Search Tags = ")
    start_page = input("Start Page = ")
    end_page = input("End Page = ")
    path = input("Download Path = ")
    process_num = input("Process Num = ")
    yande = Yande()
    yande.set_path(path_=path)
    yande.set_multiple_process(process_num)
    yande.crawl_pages_by_tag(tags_=tags, start_page_=int(start_page), end_page_=int(end_page))
