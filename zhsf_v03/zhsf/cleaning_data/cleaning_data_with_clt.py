import re
import json

from zhsf.utils import iterator
from zhsf.settings.settings import Settings
from zhsf.utils import util_functions as uf


def get_exact_litigant(litigant_list):
    result = list()
    if not litigant_list:
        return None
    else:
        for name in litigant_list:
            if re.search(r'[×\*某]', name):
                return None
        litigant_list.sort()
        return ",".join(litigant_list)


def add_value2clt2path(clt2path, wenshu_file, idx, ws_doc):
    court = ws_doc.get('s2')
    litigant = get_exact_litigant(ws_doc.get('s17'))
    title = ws_doc.get('s1')

    if court and litigant and title:
        clt = court + ',' + litigant + ',' + title
        if clt2path.get(clt):
            clt2path[clt].append(wenshu_file + "," + str(idx))
        else:
            clt2path[clt] = [wenshu_file + "," + str(idx)]


def make_clt2path(ws_settings):
    clt2path = dict()
    low_q_pos_dict = uf.make_filter(ws_settings.ncl_filter)
    for wenshu_file, idx, ws_doc in iterator.read_wenshu_with_filter(ws_settings.wenshu_path, low_q_pos_dict):
        add_value2clt2path(clt2path, wenshu_file, idx, ws_doc)
    return clt2path


def choose_max_num(post_list):
    num_list = list()
    for wenshu_pos in post_list:
        num = uf.read_wenshu_detail(wenshu_pos).get('s7')
        if not num:
            num_list.append("")
        else:
            num_list.append(num)
    return num_list.index(max(num_list))


@uf.timing_deco
def remain_distinct_clt():
    ws_settings = Settings()
    clt2path = make_clt2path(ws_settings)

    with open(ws_settings.ncl_filter, encoding='utf-8') as fp:
        low_q_pos = json.load(fp)

    for clt in clt2path:
        if len(clt2path[clt]) > 1:
            best_idx = choose_max_num(clt2path[clt])
            clt2path[clt].pop(best_idx)
            low_q_pos.extend([uf.get_relative_path(pos, ws_settings.wenshu_path) for pos in clt2path[clt]])

    return low_q_pos


if __name__ == '__main__':
    low_q_pos = remain_distinct_clt()

    ws_settings = Settings()
    uf.write_json_file(low_q_pos, ws_settings.clt_filter)