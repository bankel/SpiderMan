import requests
import re
import time
import csv


img_regex = re.compile(r"""<img\s.*?\s?data-original\s*=\s*['|"]?([^\s'"]+).*?>""", re.I)


def get_questions_id_dict():
    question_id_dict = {}
    with open('questions_id_list.txt', "r") as f:
        temp_reader = f.readlines()

        for item in temp_reader:
            kv = item.split(":")
            question_id_dict[kv[0]] = kv[1]

    return question_id_dict


def write_2_cvs(image_urls_dict):
    with open("image_urls.csv", "w", encoding='utf-8', newline='') as f:
        csv_writer = csv.writer(f)
        for k, v in image_urls_dict.items():
            csv_writer.writerow([k, v])


def retrieve_images_url(questions_id_dict):
    # key is image url and value is id which the image belongs to
    image_url_dict = {}
    for question_id in questions_id_dict.keys():
        headers = {
            'referer': 'https://www.zhihu.com/question/' + question_id,
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36',
            'cookie': '_zap=0149ee1a-0793-4c5e-a841-a843604f4c94; d_c0="AABkTS_RIQ-PTi4FPyZWHCcgR0gWvCiBXi0=|1552747466"; q_c1=b1b713dd59e34cff9540cb30f3419272|1552747467000|1552747467000; capsion_ticket="2|1:0|10:1553996509|14:capsion_ticket|44:MGJjNzEyOWQ5ZmUxNGNhYWIyYWMyZmQzNWM5ODI4MmM=|1063b3d5d5c70c7301498fc40a2baed01b26e0bd68e7fe0b61cac2845e3c2dfe"; z_c0="2|1:0|10:1553996511|4:z_c0|92:Mi4xMGV2M0FBQUFBQUFBQUdSTkw5RWhEeVlBQUFCZ0FsVk4zMmlOWFFEMWlnSEZCaUVybnk3OVp4SHVVQWxvWGtyY3Zn|7110f0e6695c0a3a90cc213f271ac8fb6436de72680448d97516172787c2906b"; tst=r; _xsrf=abe6ca55-51f5-4291-8540-88d8ce02d14f; tgw_l7_route=66cb16bc7f45da64562a077714739c11'
        }

        for i in range(0, 1000, 5):
            try:
                request_url = 'https://www.zhihu.com/api/v4/questions/'+question_id+'/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_labeled%2Cis_recognized%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%2A%5D.topics&limit=5&offset='+str(i)+'&platform=desktop&sort_by=default'
                res = requests.get(request_url, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    if not data['data']:
                        print("%s there is no data response" % request_url)
                        break
                    for answer in data['data']:
                        content = answer.get('content', '')
                        if content:
                            images_list = img_regex.findall(content)

                            for image_url in images_list:
                                print("image url %s, question_id %s, %s" % (image_url, question_id, questions_id_dict[question_id]))
                                image_url_dict[image_url] = question_id
                else:
                    print("res_code %s, url is %s" % (res.status_code, request_url))
                time.sleep(0.2)
            except Exception as e:
                print('request error %s! url %s' % (e, request_url))
                time.sleep(0.2)
                continue

    return image_url_dict


def perform():
    questions_id_dict = get_questions_id_dict()
    images_url = retrieve_images_url(questions_id_dict)
    write_2_cvs(images_url)


if __name__ == '__main__':
    perform()

