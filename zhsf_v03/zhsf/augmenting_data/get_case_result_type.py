import re
import os

from zhsf.utils import iterator
from zhsf.settings.settings import Settings
from zhsf.utils import util_functions as uf
from zhsf.augmenting_data.augment_easy_field import add_aug_judicial_procedure


def get_reject_plaintiff_cnt(case_result):
    if re.search(r'[一1]、', case_result):
        case_result_core = re.findall(r'[一二三四五1-5]、.*?[；。]', case_result, re.S)
    else:
        case_result_core = re.split("。", case_result, maxsplit=1)[0:1]

    reject_plaintiff_cnt = 0
    for i in case_result_core:
        if re.search(r'驳回[^，。；]{0,20}原告', i):
            reject_plaintiff_cnt += 1

    return reject_plaintiff_cnt, case_result_core


def support_rate2plaintiff(reject_plaintiff_cnt, case_result_core):
    if reject_plaintiff_cnt == len(case_result_core):
        return "全部驳回原告"
    elif reject_plaintiff_cnt > 0:
        return "部分支持原告"
    elif len(case_result_core) > 1:
        return "全部支持原告"
    elif re.search(r'被告[^，。；]{0,10}犯[^，。；]{0,6}罪', case_result_core[0]):
        return "全部支持原告"
    elif re.search(r'被告[^，。；]+?原告', case_result_core[0]):
        return "全部支持原告"
    return None


def get_doc_result_type_proc1(case_result):
    if re.search(r'撤诉[^，。；]{0,6}处理', case_result) or re.search(r'准许[^，。；]*?撤回', case_result):
        return "准许撤诉"
    elif re.search(r'驳回[^，。；]{0,20}起诉', case_result):
        return "驳回起诉"

    reject_plaintiff_cnt, case_result_core = get_reject_plaintiff_cnt(case_result)

    return support_rate2plaintiff(reject_plaintiff_cnt, case_result_core)


def get_doc_result_type_proc2(case_result):
    if re.search(r'驳回', case_result) and re.search(r'维持[^，。；]{0,6}原判', case_result):
        return "二审维持原判"
    elif re.search(r'撤销', case_result):
        if re.search(r'发回[^，。；]{0,20}重审', case_result):
            return "二审发回重审"
        elif re.search(r'改判', case_result):
            if re.search(r'维持', case_result) or re.search(r'第.项', case_result):
                return "二审部分改判"
            else:
                return "二审改判"
    return None


def get_doc_result_type_proc3(case_result):
    if re.search(r'驳回', case_result) and re.search(r'维持[^，。；]{0,6}原判', case_result):
        return "再审维持原判"
    elif re.search(r'终结再审', case_result) and re.search(r'恢复[^，。；]{0,6}原判决', case_result):
        return "再审维持原判"
    elif re.search(r'发回[^，。；]*?重审', case_result):
        return "再审发回重审"
    elif re.search(r'撤销', case_result) and re.search(r'改判', case_result):
        if re.search(r'维持', case_result) or re.search(r'第.项', case_result):
            return "再审部分改判"
        else:
            return "再审改判"
    return None


def get_doc_result_type(ws_doc, case_result):
    add_aug_judicial_procedure(ws_doc)

    if ws_doc['spcx_category'] == '一审':
        return get_doc_result_type_proc1(case_result)
    elif ws_doc['spcx_category'] == '二审':
        return get_doc_result_type_proc2(case_result)
    elif ws_doc['spcx_category'] == '再审':
        return get_doc_result_type_proc3(case_result)
    return None


@uf.timing_deco
def get_case_result_type(year):
    ws_settings = Settings()
    low_q_pos_dict = uf.make_filter(ws_settings.clt_filter)

    result_mapping = dict()
    for wenshu_file, idx, ws_doc in iterator.read_wenshu_with_filter(
            os.path.join(ws_settings.wenshu_path, str(year)), low_q_pos_dict):
        
        docId = ws_doc['s5']
        case_result = ws_doc.get('s27')
        if case_result:
            result_type = get_doc_result_type(ws_doc, case_result)
            if result_type:
                result_mapping[docId] = result_type
    return result_mapping


if __name__ == '__main__':
    ws_settings = Settings()

    for year in range(2011, 2019):
        uf.write_json_file(get_case_result_type(year), 
                os.path.join(ws_settings.aug_case_result_type, str(year) + '.json'))