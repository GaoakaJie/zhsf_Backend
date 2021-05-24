import json
from zhsf.settings.settings import Settings
from zhsf.utils import iterator
from zhsf.utils import util_functions as uf


def make_filter(ws_settings):
    with open(ws_settings.id_filter, encoding='utf-8') as fp:
        low_q_pos = json.load(fp)

    low_q_pos_dict = dict()
    for pos in low_q_pos:
        low_q_pos_dict[pos] = 1

    return low_q_pos_dict


def make_num_court2path(num_court2path, wenshu_file, idx, encryptwenshu_docs):
    num = encryptwenshu_docs.get('s7')
    court = encryptwenshu_docs.get('s2')

    if num and court:
        num_court = num + ',' + court
        if num_court2path.get(num_court):
            num_court2path[num_court].append(wenshu_file + "," + str(idx))
        else:
            num_court2path[num_court] = [wenshu_file + "," + str(idx)]


def get_more_value_date(d):
    result = dict()
    for k in d:
        if len(d[k]) > 1:
            result[k] = d[k]
    return result


@uf.timing_deco
def test_num_court():
    # 遍历文档，创建字典
    ws_settings = Settings()
    low_q_pos_dict = make_filter(ws_settings)
    num_court2path = dict()
    for wenshu_file, idx, encryptwenshu_docs in iterator.read_wenshu(ws_settings.wenshu_path_test):
        # 遍历过程中过滤
        if low_q_pos_dict.get(uf.get_relative_path(wenshu_file + "," + str(idx), ws_settings.wenshu_path_test)):
            continue
        make_num_court2path(num_court2path, wenshu_file, idx, encryptwenshu_docs)

    result = get_more_value_date(num_court2path)
    return result


if __name__ == '__main__':
    result = test_num_court()

    ws_settings = Settings()
    uf.write_json_file(result, ws_settings.test_outputs + '案号法院相同案件.json')