import os

from zhsf.utils import iterator
from zhsf.utils.cause_of_case_path import CauseOfCasePath
from zhsf.settings.settings import Settings
from zhsf.utils import util_functions as uf


def add_cause(cause, cause_path_finder, docId, wenshuAy_list):
    for wenshuAy in wenshuAy_list:
        if not cause.get(docId):
            cause[docId] = cause_path_finder.get_path(wenshuAy['value'])
        else:
            cause[docId].extend(cause_path_finder.get_path(wenshuAy['value']))


@uf.timing_deco
def get_cause(year):
    ws_settings = Settings()
    cause_path_finder = CauseOfCasePath(ws_settings.cause_of_case_standard_file)
    low_q_pos_dict = uf.make_filter(ws_settings.clt_filter)

    cause = dict()
    for wenshu_file, idx, ws_doc in iterator.read_wenshu_with_filter(
            os.path.join(ws_settings.wenshu_path, str(year)), low_q_pos_dict):
        
        docId = ws_doc['s5']
        if ws_doc.get('wenshuAy'):
            add_cause(cause, cause_path_finder, docId, ws_doc.get('wenshuAy'))

    return cause


if __name__ == '__main__':
    ws_settings = Settings()

    for year in range(2011, 2019):
        uf.write_json_file(get_cause(year), os.path.join(ws_settings.aug_cause, str(year) + '.json'))