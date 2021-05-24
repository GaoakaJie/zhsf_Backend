import os
import re

from zhsf.utils import iterator
from zhsf.settings.settings import Settings
from zhsf.utils import util_functions as uf


def is_litigation_record(litigation_record, html_p):
    if not litigation_record:
        return False
    else:
        len1 = len(litigation_record) // 3
        len2 = len(litigation_record) // 3 * 2

        return re.search(re.escape(litigation_record[: len1]), html_p) \
                or re.search(re.escape(litigation_record[len1: len2]), html_p) \
                or re.search(re.escape(litigation_record[len2: ]), html_p)


def is_pass_litigation_record(html_p):
    return '审理终结' in html_p or '本院受理后' in html_p or '进行了审理' in html_p or '本院在审理' in html_p \
            or '审理查明' in html_p or '本院认为' in html_p or '判决如下' in html_p or '决定如下' in html_p \
            or '纠纷一案' in html_p or '本院依法组成' in html_p


def need_stop(litigation_record, html_p):
    stop = is_litigation_record(litigation_record, html_p) or uf.is_case_num_in(html_p) or is_pass_litigation_record(html_p)
    return stop


def is_bad_litigant_paragraph(litigant_paragraph):
    is_whole_wenshu = ('审判长' in litigant_paragraph or '审判员' in litigant_paragraph \
            or '陪审员' in litigant_paragraph) and '书记员' in litigant_paragraph
    is_wenshu_head = re.search(r'人民法院.{1,10}书', litigant_paragraph, re.S)
    return is_whole_wenshu or is_wenshu_head


def slice_html4litigant_p(litigation_record, html_paragraphs):
    litigant_paragraph = ""
    if len(html_paragraphs) <= 3:
        return litigant_paragraph

    for html_p in html_paragraphs[3:]:  # 前3行为法院名称、文书类型、案号
        if need_stop(litigation_record, html_p):
            break

        else:
            litigant_paragraph += html_p + "\n"
            
    if is_bad_litigant_paragraph(litigant_paragraph):  # 适当数据清洗，也就是匹配到最后的说明出现了问题，丢弃。
        litigant_paragraph = ""
            
    return litigant_paragraph


@uf.timing_deco
def get_litigant_paragraph(year):
    ws_settings = Settings()
    low_q_pos_dict = uf.make_filter(ws_settings.clt_filter)

    litigant_p = dict()
    for wenshu_file, idx, ws_doc in iterator.read_wenshu_with_filter(
            os.path.join(ws_settings.wenshu_path, str(year)), low_q_pos_dict):
        
        docId = ws_doc['s5']
        litigation_record = ws_doc.get('s23')
        html_paragraphs = uf.get_wenshu_pure_html_paragraphs(ws_doc)
        litigant_paragraph = slice_html4litigant_p(litigation_record, html_paragraphs)
        if litigant_paragraph:
            litigant_p[docId] = litigant_paragraph

    return litigant_p


if __name__ == '__main__':
    ws_settings = Settings()

    for year in range(2011, 2019):
        uf.write_json_file(get_litigant_paragraph(year), 
                os.path.join(ws_settings.aug_litigant_paragraph, str(year) + '.json'))