import os
import json
from zhsf.settings.settings import Settings
from zhsf.utils import util_functions as uf


def read_wenshu(wenshu_path):
    '''迭代器模式，参考：https://github.com/faif/python-patterns/blob/master/patterns/behavioral/observer.py
    
    为什么是迭代器，而不是函数，因为获得每个对象后，我的处理的未定的。
    
    给定文书目录，读取这个目录下所有文件，
    解析文件中所有文书，返回文书的详情。
    
    Args:
        wenshu_path: 文书目录。
        
    Returns:
        返回文件路径，文书位置，文书内容。
        
    Raises:
    '''
    wenshu_file_list = list()
    for (dirpath, dirnames, filenames) in os.walk(wenshu_path):
        wenshu_file_list.extend([os.path.join(dirpath, filename) for filename in filenames])
        
    for wenshu_file in wenshu_file_list:
        with open(wenshu_file, encoding='utf-8') as fp:
            details = json.load(fp)['details']
        
        for idx, detail in enumerate(details):
            ws_doc = detail.get('encryptResult')
            if ws_doc:
                yield wenshu_file, idx, ws_doc


def read_wenshu_with_filter(wenshu_path, filter):
    ws_settings = Settings()

    for wenshu_file, idx, ws_doc in read_wenshu(wenshu_path):
        # 遍历过程中过滤
        if filter.get(uf.get_relative_path(wenshu_file + "," + str(idx), ws_settings.wenshu_path)):
            continue
        yield wenshu_file, idx, ws_doc
