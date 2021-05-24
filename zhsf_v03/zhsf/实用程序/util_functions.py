import os
import re
import json
from time import time
from datetime import datetime
import pymysql
from elasticsearch import Elasticsearch

from zhsf.utils import my_html_parser
from zhsf.settings.settings import Settings


def get_relative_path(abs_path, pre_path):
    relpath = os.path.relpath(abs_path, pre_path)

    if '\\' in relpath:
        relpath = re.sub(r'\\', '/', relpath)

    return relpath


def read_wenshu_detail(wenshu_pos):
    wenshu_file, idx = re.split(',', wenshu_pos)
    with open(wenshu_file, encoding='utf-8') as fp:
        details = json.load(fp)['details']
        encryptResult = details[int(idx)].get('encryptResult')

    return encryptResult


def write_json_file(dict_or_list, filename):
    with open(filename, 'w', encoding='utf-8') as fp:
        json.dump(dict_or_list, fp, ensure_ascii=False, indent=4)


def read_json_file(filename):
    with open(filename, encoding='utf-8') as fp:
        return json.load(fp)


def timing_deco(func):
    def wrapper(*args, **kwargs):
        print("\n\n当前时间:", datetime.now())
        start = time()
        
        result = func(*args, **kwargs)
        
        end = time()
        delta_time = end - start
        if delta_time > 3600:
            print("Running consumes hours:", (end - start) / 3600)
        elif delta_time > 60:
            print("Running consumes minutes:", (end - start) / 60)
        else:
            print("Running consumes seconds:", (end - start))

        return result
        
    return wrapper


def get_wenshu_pure_html_paragraphs(wenshu_detail):
    html = wenshu_detail.get('qwContent')
    if html:
        parser = my_html_parser.MyHTMLParser()
        parser.feed(html)
        if parser.parse_result:
            return parser.parse_result
    return []


def get_wenshu_pure_html(wenshu_detail):
    html_paragraphs = get_wenshu_pure_html_paragraphs(wenshu_detail)
    return '\n'.join(html_paragraphs)


def make_filter(filter_file):
    with open(filter_file, encoding='utf-8') as fp:
        low_q_pos = json.load(fp)

    low_q_pos_dict = dict()
    for pos in low_q_pos:
        low_q_pos_dict[pos] = 1

    return low_q_pos_dict


def get_wenshu_pos_with_relpath(relpaths, wenshu_id):
    ws_settings = Settings()

    wenshu_pos_list = list()
    for relpath in relpaths:
        abs_path = os.path.join(ws_settings.wenshu_path4mysql, relpath)
        if '\\' in abs_path:
            abs_path = re.sub(r'\\', '/', abs_path)

        with open(abs_path, encoding='utf-8') as fp:
            details = json.load(fp)['details']
        for idx, detail in enumerate(details):
            if detail['docId'] == wenshu_id:
                wenshu_pos_list.append(abs_path + "," + str(idx))
                break
    return wenshu_pos_list


def wenshu_id2wenshu_pos(wenshu_id):
    connection = pymysql.connect(
            host='localhost',
            user='root',
            passwd='666666',
            db='wenshu_pm2_v3',
            port=3306,
            charset='utf8')
    with connection.cursor() as cursor:
        sql = 'SELECT * FROM judgements WHERE `doc_id` = %s'
        cursor.execute(sql, (wenshu_id))
        relpaths = [result[2] for result in cursor.fetchall()]

    wenshu_pos_list = get_wenshu_pos_with_relpath(relpaths, wenshu_id)
    return relpaths, wenshu_pos_list


def is_case_num_in(s):
    pattern = re.compile(r'（?\d{4}\D{1,4}\d{0,5}\D{1,3}\d{1,5}号')
    return re.search(pattern, s)


def read_setting_and_mapping_file(filename):
    with open(filename, encoding='utf-8') as fp:
        json_content = ""
        for line in fp.readlines():
            json_content += re.sub(r' *?//.*$', '', line)

    return json.loads(json_content)


def date_delta(str1, str2):
    date1 = datetime.strptime(str1, '%Y-%m-%d')
    date2 = datetime.strptime(str2, '%Y-%m-%d')
    return (date1 - date2).days


def get_es(settings):
    return Elasticsearch(
            [settings.es_host], 
            http_auth=settings.es_http_auth, 
            port=settings.es_port, 
            use_ssl=settings.es_use_ssl)