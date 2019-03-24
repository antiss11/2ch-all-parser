import requests
import json
import os
from lxml import html
import threading
import time


TIME_SLEEP = 20
THREADS_JSON_LINK = 'https://2ch.hk/b/threads.json'
THREADS_PARSED = False


def mkdir(dirname):
    try:
        os.mkdir(str(dirname))
    except FileExistsError:
        pass


def get_page(url):
    page_text = requests.get(url).text
    return page_text


def deserealize_json(text):
    return json.loads(text)


def get_threads_num(obj):
    threads = obj['threads']
    return [thread['num'] for thread in threads]


def norm_thread_link(arg):
    return 'https://2ch.hk/b/res/{0}.html'.format(arg)


def norm_img_link(link):
    return 'https://2ch.hk{0}'.format(link)


def get_html_tree(html_code):
    return html.fromstring(html_code)


def get_media_rlinks(tree):
    return tree.xpath('//a[@class="post__image-link"]')


def create_path(*args):
    return os.path.normpath(os.path.join(*args))


def downloader(parent_folder, folder, lock, *args):
    print(threading.active_count())
    for link in args:
        name = link.split("/")[-1]
        path = create_path(parent_folder, folder, name)
        with open(path, "wb") as file:
            data = requests.get(link, stream=True)
            for chunk in data:
                file.write(chunk)


def parse_thread(thread_num):
    normal_link = norm_thread_link(thread_num)
    thread_page = get_page(normal_link)
    thread_tree = html.fromstring(thread_page)
    r_media_links = get_media_rlinks(thread_tree)
    media_cutlinks = [obj.get('href') for obj in r_media_links]
    media_fullinks = [norm_img_link(link) for link in media_cutlinks]
    return media_fullinks


class Main:
    def __init__(self, parent_dir):
        self.parent_dir = parent_dir

    def main(self):
        thread_list = []
        page = get_page(THREADS_JSON_LINK)
        json_load = deserealize_json(page)
        self.threads_num = get_threads_num(json_load)
        for thread_num in self.threads_num[]:
            dir = os.path.join(parent_dir, thread_num)
            if os.path.exists(dir) and os.path.isdir(dir):
                pass
            elif os.path.exists(dir) is False:
                mkdir(os.path.join(parent_dir, thread_num))
        lock = threading.Lock()
        for thread_num in self.threads_num[]:
            print(thread_num)
            links = parse_thread(thread_num)
            folder_name = links[0].split("/")[-2]
            thread = threading.Thread(target=downloader, args=(parent_dir, folder_name, lock, *links)).start()
            thread_list.append(thread)
        for thread in thread_list:
            thread.join()
        global THREADS_PARSED
        THREADS_PARSED = True


if __name__ == '__main__':
    parent_dir = input('Enter the path to save: ')
    parent_dir = os.path.normpath(parent_dir)
    a = Main(parent_dir)
    a.main()
    while True:
        if THREADS_PARSED is True:
            a.main()
            time.sleep(TIME_SLEEP)
        else:
            time.sleep(3)



