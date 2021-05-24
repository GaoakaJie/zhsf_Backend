import re
import os
from time import time

from zhsf.utils import iterator
from zhsf.settings.settings import Settings
from zhsf.utils import util_functions as uf
from zhsf.augmenting_data.augment_easy_field import add_aug_judicial_procedure


def get_pattern(undertake_mode):
    return re.compile(undertake_mode[0:2] + r'[^，；\n]{0,25}' + undertake_mode[2:4])


def get_undertake_mode(claims):
    claims['undertake_mode'] = list()
    undertake_mode_pattern = {
        "停止侵害": re.compile(r'停止' + r'[^，；\n]{0,25}' + r'侵'),
        "消除危险": re.compile(r'危险'),
        "返还财产": re.compile(r'返还'),
        "恢复原状": re.compile(r'恢复'),
        "赔偿损失": re.compile(r'赔偿'),
        "赔礼道歉": re.compile(r'道歉'),
        "消除影响": re.compile(r'消除'),
        "恢复名誉": re.compile(r'恢复'),
    }
    for k in undertake_mode_pattern:
        if re.search(undertake_mode_pattern[k], claims['content']):
            claims['undertake_mode'].append(k)


def get_claims_content(ws_doc, docId, cause_per_year):
    cause_id= cause_per_year.get(docId)
    add_aug_judicial_procedure(ws_doc)

    claims = dict()
    if cause_id and '9363' in cause_id and ws_doc['spcx_category'] == '一审' and ws_doc.get('s25'):
        match_result = re.search(r'请求[^，：]{0,5}[：1一][^\n]+?。', ws_doc['s25'])
        if match_result:
            claims['cause'] = cause_id
            claims['spcx_category'] = ws_doc['spcx_category']
            claims['content'] = match_result.group()

            get_undertake_mode(claims)
    return claims


@uf.timing_deco
def get_claims(year):
    ws_settings = Settings()
    low_q_pos_dict = uf.make_filter(ws_settings.clt_filter)
    cause_per_year = uf.read_json_file(os.path.join(ws_settings.aug_cause, str(year) + '.json'))

    cliams_mapping = dict()
    for wenshu_file, idx, ws_doc in iterator.read_wenshu_with_filter(
            os.path.join(ws_settings.wenshu_path, str(year)), low_q_pos_dict):
        
        docId = ws_doc['s5']
        claims = get_claims_content(ws_doc, docId, cause_per_year)
        if claims:
            cliams_mapping[docId] = claims

    return cliams_mapping


if __name__ == '__main__':
    ws_settings = Settings()

    for year in range(2011, 2019):
        uf.write_json_file(get_claims(year), 
                os.path.join(ws_settings.aug_claims, str(year) + '.json'))