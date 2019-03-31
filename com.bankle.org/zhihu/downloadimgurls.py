import csv
from queue import Queue
import requests
import os
import threading

url_queue = Queue()
with open('image_urls.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    for row in reader:
        url_queue.put((row))

headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36'
    }

base_dir = "/Users/lyf/Documents/"


def get_proxy():

    try:
        get_proxy_utl = 'http://91.225.165.4/57021'
        res = requests.get(get_proxy_utl)
        if res.status_code == 200:
            print('get ip from proxy pool: %s' % res.text)
            proxies = {'http': 'http://' + res.text}
            return proxies
        else:
            return None
    except Exception as e:
        print('error when get id from proxy pool！！ %s' % e)
        return None


def download_pictures():

    question_id_dict = {}
    with open('questions_id_list.txt', "r") as f:
        temp_reader = f.readlines()

        for item in temp_reader:
            kv = item.split(":")
            question_id_dict[kv[0]] = kv[1]

    while True:
        try:
            item = url_queue.get(block=True, timeout=180)
            image_url, question_id = item

        except Exception as e:
            print("error %s " % e)
            break

        data = None
        request_time = 0

        while True:
            try:
                headers['referer'] = 'https://www.zhihu.com/question/' + question_id
                proxies = get_proxy()
                # print('代理IP: %s' % proxies)
                res = requests.get(image_url, proxies=proxies, headers=headers, timeout=3)
                print('response : %s, url: %s' % (res.status_code, image_url))
                if res.status_code == 200:
                    data = res.content
                    break
                else:
                    request_time += 1
                    if request_time > 5:
                        break
            except Exception as e:
                print('numbers for request: %s (%s)' % (request_time, e))
                request_time += 1
                if request_time > 5:
                    res = requests.get(image_url, headers=headers)
                    if res.status_code == 200:
                        data = res.content
                    break
                continue

        try:

            # name of question
            question_name = question_id_dict.get(question_id)
            # create the path with the name of question
            pic_dir = os.path.join(base_dir, question_name)
            if not os.path.exists(pic_dir):
                try:
                    os.makedirs(pic_dir)
                except Exception as e:
                    print("error %s " % e)
                    pass

            # name of image
            image_name = image_url.split('/')[-1]
            # path of image
            pic_path = os.path.join(pic_dir, image_name)
            if data:
                with open(pic_path, 'wb') as f:
                    f.write(data)
                    print('download successful: ', image_name)
                    # time.sleep(0.3)
        except Exception as e:
            print('error when process storage the file has been downloaded, (%s)' % e)
            continue


def main():
    for i in range(15):
        td = threading.Thread(target=download_pictures)
        td.start()


if __name__ == '__main__':
    main()
