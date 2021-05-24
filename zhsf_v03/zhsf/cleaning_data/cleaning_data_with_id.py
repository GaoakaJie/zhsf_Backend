import re
import json
from os import walk
from os.path import join

from zhsf.settings.settings import Settings
from zhsf.utils import iterator
from zhsf.utils import util_functions as uf
from zhsf.utils import my_html_parser


def get_best_doc(idxs, docs):
    max_len = max(map(len, docs))
    scores = map(lambda x: len(x) / max_len * 100, docs)
    scores = list(scores)

    pattern = re.compile(r'[×\*某]')
    for i, doc in enumerate(docs):
        occ_times = len(re.findall(pattern, doc))
        scores[i] -= 3 * occ_times

    top = scores.index(max(scores))
    return idxs[top]


def get_wenshu_htmls(wenshu_details):
    wenshu_htmls = [[idx, detail.get('qwContent')] for idx, detail in enumerate(wenshu_details) if detail.get('qwContent')]
    result = list()
    for idx, html in wenshu_htmls:
        parser = my_html_parser.MyHTMLParser()
        parser.feed(html)
        if parser.parse_result and '\n'.join(parser.parse_result):
            result.append([idx, '\n'.join(parser.parse_result)])
    return result


def choose_longest(wenshu_details):
    lens = list(map(len, wenshu_details))
    return lens.index(max(lens))


def check_best_wenshu_detail(pos_list):
    wenshu_details = [uf.read_wenshu_detail(wenshu_pos) for wenshu_pos in pos_list]
    wenshu_htmls = get_wenshu_htmls(wenshu_details)

    if len(wenshu_htmls) == 0:
        best_idx = choose_longest(wenshu_details)
    else:
        idxs, htmls = list(zip(*wenshu_htmls))
        best_idx = get_best_doc(idxs, htmls)
        
    return best_idx


def make_id2path(ws_settings):
    id2path = dict()
    for wenshu_file, idx, ws_doc in iterator.read_wenshu(ws_settings.wenshu_path):
        docId = ws_doc['s5']

        if id2path.get(docId):
            id2path[docId].append(wenshu_file + "," + str(idx))
        else:
            id2path[docId] = [wenshu_file + "," + str(idx)]
    return id2path


@uf.timing_deco
def remain_distinct_id():
    ws_settings = Settings()
    id2path = make_id2path(ws_settings)

    low_q_pos = list()
    for docId in id2path:
        if len(id2path[docId]) > 1:
            best_idx = check_best_wenshu_detail(id2path[docId])
            id2path[docId].pop(best_idx)
            low_q_pos.extend([uf.get_relative_path(pos, ws_settings.wenshu_path) for pos in id2path[docId]])

    return low_q_pos


if __name__ == '__main__':
    low_q_pos = remain_distinct_id()

    ws_settings = Settings()
    uf.write_json_file(low_q_pos, ws_settings.id_filter)