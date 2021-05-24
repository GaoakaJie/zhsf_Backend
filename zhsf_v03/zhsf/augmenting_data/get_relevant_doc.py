import re
import os

from zhsf.utils import iterator
from zhsf.settings.settings import Settings
from zhsf.utils import util_functions as uf
from zhsf.cleaning_data.cleaning_data_with_ncl import get_litigant


def clean_num_and_court(num, court):
    return num.group(0), re.sub(r'不服', '', court.group(1))


def add_value2relevant_mapping(relevant_mapping, ws_doc):
    litigation_record = ws_doc.get('s23')
    if litigation_record:
        num = uf.is_case_num_in(litigation_record)
        litigant = get_litigant(ws_doc.get('s17'))
        if num and litigant:
            num_mark = num.group(0) + ',' + litigant
            relevant_mapping[num_mark] = {'id': ws_doc['s5'],
                                     'num': ws_doc.get('s7'),
                                     'judgement_date': ws_doc.get('s31')}


@uf.timing_deco
def make_relevant_mapping():
    ws_settings = Settings()
    relevant_mapping = dict()

    low_q_pos_dict = uf.make_filter(ws_settings.clt_filter)
    for year in range(2001, 2019):
        for wenshu_file, idx, ws_doc in iterator.read_wenshu_with_filter(
            os.path.join(ws_settings.wenshu_path, str(year)), low_q_pos_dict):

            add_value2relevant_mapping(relevant_mapping, ws_doc)

    uf.write_json_file(relevant_mapping, ws_settings.aug_relevant_mapping)


if __name__ == '__main__':
    make_relevant_mapping()