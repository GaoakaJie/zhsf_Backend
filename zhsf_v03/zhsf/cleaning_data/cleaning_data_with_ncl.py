import re
import json

from zhsf.utils import iterator
from zhsf.settings.settings import Settings
from zhsf.utils import util_functions as uf
from zhsf.cleaning_data.cleaning_data_with_id import check_best_wenshu_detail


def get_litigant(litigant_list):
    if not litigant_list:
        return None
    else:
        result = list()
        for name in litigant_list:
            if len(name) <= 4:
                result.append(name[:1])
            else:
                result.append(name)
        result.sort()
        return ','.join(result)


def get_real_court(court_name, court_map):
    if court_name:
        real_court_info = court_map.get(re.sub(' +', '', court_name))
        if real_court_info:
            return real_court_info['court_name']

    return None


def add_value2ncl2path(ncl2path, wenshu_file, idx, ws_doc, court_map):
    num = ws_doc.get('s7')
    court = get_real_court(ws_doc.get('s2'), court_map)
    litigant = get_litigant(ws_doc.get('s17'))

    if num and court and litigant:
        ncl = num + ',' + court + ',' + litigant
        if ncl2path.get(ncl):
            ncl2path[ncl].append(wenshu_file + "," + str(idx))
        else:
            ncl2path[ncl] = [wenshu_file + "," + str(idx)]


def make_ncl2path(ws_settings):
    ncl2path = dict()

    court_map = uf.read_json_file(ws_settings.court_map_table)
    low_q_pos_dict = uf.make_filter(ws_settings.id_filter)

    for wenshu_file, idx, ws_doc in iterator.read_wenshu_with_filter(ws_settings.wenshu_path, low_q_pos_dict):
        add_value2ncl2path(ncl2path, wenshu_file, idx, ws_doc, court_map)
    return ncl2path


@uf.timing_deco
def remain_distinct_ncl():
    ws_settings = Settings()
    ncl2path = make_ncl2path(ws_settings)

    with open(ws_settings.id_filter, encoding='utf-8') as fp:
        low_q_pos = json.load(fp)

    for ncl in ncl2path:
        if len(ncl2path[ncl]) > 1:
            best_idx = check_best_wenshu_detail(ncl2path[ncl])
            ncl2path[ncl].pop(best_idx)
            low_q_pos.extend([uf.get_relative_path(pos, ws_settings.wenshu_path) for pos in ncl2path[ncl]])

    return low_q_pos


if __name__ == '__main__':
    low_q_pos = remain_distinct_ncl()

    ws_settings = Settings()
    uf.write_json_file(low_q_pos, ws_settings.ncl_filter)