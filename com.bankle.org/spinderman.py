import requests
import os
from lxml import html

from multiprocessing.dummy import Pool as ThreadPool
import time



def header(referer):
    headers = {
        'Host': 'i.meizitu.net',
        'Pragma': 'no-cache',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/59.0.3071.115 Safari/537.36',
        'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
        'Referer': '{}'.format(referer),
    }
    return headers


#get all pages
def getpages():
    main_page = "https://www.mzitu.com/"
    selector = html.fromstring(requests.get(main_page).content)

    count = selector.xpath("//div[@class='nav-links']/a[last()-1]/text()")[0]
    page_urls = []
    for i in range(int(count)):
        page_urls.append('http://www.mzitu.com/page/{}'.format(i+1))

    return page_urls


def get_detail_per_page(pageurl):

    selector = html.fromstring(requests.get(pageurl).content)

    urls = []
    for i in selector.xpath("//ul[@id='pins']/li/a/@href"):
        urls.append(i)
    return urls


# get all images from some theme and title
def get_images(url):
    curselector = html.fromstring(requests.get(url).content)

    # all numbs of images
    total = curselector.xpath("//div[@class='pagenavi']/a[last()-1]/span/text()")[0]
    title = curselector.xpath("//h2[@class='main-title']/text()")[0]

    # collect images url
    jpg_list = []

    for i in range(int(total)):
        link = "{}/{}".format(url, i+1)

        # load the link html
        item = html.fromstring(requests.get(link).content)
        jpg_url = item.xpath("//div[@class='main-image']/p/a/img/@src")[0]
        jpg_list.append(jpg_url)

    return title, jpg_list


# download the image to the destination dir
def download(title, jpg_list, dir):
    print("{},{}".format(title, jpg_list[0]))
    start = 1
    count = len(jpg_list)

    # create the dir if not exits
    if not os.path.exists(dir):
        os.makedirs(dir)

    # currentDir
    current_dir = u"【%sP】%s" % (str(count), title)
    currentPath = "%s/%s" % (dir, current_dir)
    if not os.path.exists(currentPath):
        os.mkdir(currentPath)

    # download all image
    for url in jpg_list:
        file_name = str(url).split("/")[-1]
        write_file = u"{}/{}/{}".format(dir, current_dir, file_name)

        print("start download %s and %s index %s" % (current_dir, file_name, start))
        if os.path.exists(write_file):
            print("%s has exists, continue next download " % write_file)
            continue

        with open(write_file, "wb+") as jpg_file:
            jpg_file.write(requests.get(url, headers=header(url)).content)
            start += 1

        time.sleep(0.2)


def retrieve_images():
    parentpath = "/Users/lyf/Documents"

    pageurls = getpages()
    for pageurl in pageurls:  # divide main page

        page_details_url = get_detail_per_page(pageurl)
        print("====== %s ========" % pageurl)
        #  we have retrieve all page detail url of current page,then we can retrieve the images from detail url
        for page_detail_url in page_details_url:

            image_category = get_images(page_detail_url)
            with ThreadPool(4) as pool:
                pool.starmap(download, [(image_category[0], image_category[1], parentpath)])


            # download(image_category[0], image_category[1], parentpath)


retrieve_images()



