from zhsf.utils import iterator
from zhsf.settings.settings import Settings
from zhsf.utils import util_functions as uf
from zhsf.cleaning_data.cleaning_data_with_ncl import make_ncl2path
from zhsf.cleaning_data.cleaning_data_with_ncl import get_litigant


def get_more_value_date(d):
    result = dict()
    for k in d:
        if len(d[k]) > 1:
            result[k] = d[k]
    return result


@uf.timing_deco
def test_ncl():
    ws_settings = Settings()
    
    ncl2path = make_ncl2path(ws_settings)

    result = get_more_value_date(ncl2path)
    return result


def add_value2nl2path(nl2path, wenshu_file, idx, encryptwenshu_docs):
    num = encryptwenshu_docs.get('s7')
    litigant = get_litigant(encryptwenshu_docs.get('s17'))

    if num and litigant:
        nl = num + ',' + litigant
        if nl2path.get(nl):
            nl2path[nl].append(wenshu_file + "," + str(idx))
        else:
            nl2path[nl] = [wenshu_file + "," + str(idx)]


def make_nl2path(ws_settings):
    nl2path = dict()

    low_q_pos_dict = uf.make_filter(ws_settings.ncl_filter)
    for wenshu_file, idx, encryptwenshu_docs in iterator.read_wenshu_with_filter(ws_settings.wenshu_path_test, low_q_pos_dict):
        add_value2nl2path(nl2path, wenshu_file, idx, encryptwenshu_docs)
    return nl2path


@uf.timing_deco
def check_distinct_nl():
    ws_settings = Settings()
    nl2path = make_nl2path(ws_settings)
    print(len(nl2path))

    result = dict()
    for nl in nl2path:
        if len(nl2path[nl]) > 1:
            result[nl] = nl2path[nl]
    return result


if __name__ == '__main__':
    result = check_distinct_nl()

    ws_settings = Settings()
    uf.write_json_file(result, ws_settings.test_outputs + '是否还存在案号相同-当事人相同的案件.json')