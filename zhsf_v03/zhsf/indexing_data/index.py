import os
import re
from elasticsearch.helpers import bulk
from elasticsearch.helpers.errors import BulkIndexError

from zhsf.utils import iterator
from zhsf.settings.settings import Settings
from zhsf.utils import util_functions as uf
from zhsf.augmenting_data import augment_easy_field as aug
from zhsf.cleaning_data.cleaning_data_with_ncl import get_litigant


def delete_no_need_field(ws_doc, mappingSettings={}):
    mapping_fields = mappingSettings['properties']
    return {k: v for k, v in ws_doc.items() if mapping_fields.get(k) and v}


def add_aug_court_data(ws_doc, court_map):
    court_name = ws_doc.get('s2')
    if court_name:
        real_court_info = court_map.get(re.sub(' +', '', court_name))

        if real_court_info:
            for k in real_court_info:
                ws_doc[k] = real_court_info[k]


def add_aug_cause_data(ws_doc, docId, cause_per_year):
    cause_id = cause_per_year.get(docId)
    if cause_id:
        ws_doc['cause_id'] = cause_id
    if ws_doc.get('wenshuAy'):
        cause = [wenshuAy['text'] for wenshuAy in ws_doc['wenshuAy']]
        ws_doc['cause'] = cause


def add_litigant_attorney_name_firm(litigant):
    if litigant.get('attorneys'):
        for attorney in litigant['attorneys']:
            if attorney.get('name') and attorney.get('firm'):
                attorney['name_firm'] = attorney['name'] + '#' + attorney['firm']


def add_aug_litigant_data(ws_doc, docId, litigant_per_year):
    litigant_info = litigant_per_year.get(docId)
    if litigant_info:
        # ws_doc['litigant'] = [{k: v for k, v in litigant.items() if v and k != 'other'} for litigant in litigant_info['LP']]
        ws_doc['litigant'] = list()
        for litigant in litigant_info['LP']:
            add_litigant_attorney_name_firm(litigant)
            ws_doc['litigant'].append({k: v for k, v in litigant.items() if v and k != 'other'})


def add_aug_litigant_paragraph_data(ws_doc, docId, litigant_paragraph_per_year):
    litigant_paragraph = litigant_paragraph_per_year.get(docId)
    if litigant_paragraph:
        ws_doc['s53'] = litigant_paragraph


def add_aug_claims_data(ws_doc, docId, claims_per_year):
    claims = claims_per_year.get(docId)
    if claims and claims.get('undertake_mode'):
        ws_doc['claims_type'] = claims['undertake_mode']


def add_aug_result_type_data(ws_doc, docId, result_type_per_year):
    result_type = result_type_per_year.get(docId)
    if result_type:
        ws_doc['case_result_type'] = result_type


def add_aug_relevant_doc(ws_doc, relevant_mapping):
    num = ws_doc.get('s7')
    litigant = get_litigant(ws_doc.get('s17'))
    judgement_date = ws_doc.get('s31')
    if num and litigant and judgement_date:
        num_mark = num + ',' + litigant
        relevant_doc = relevant_mapping.get(num_mark)
        if relevant_doc and relevant_doc.get('judgement_date'):
            relevant_doc['hearing_cycle'] = uf.date_delta(relevant_doc['judgement_date'], judgement_date)
            if relevant_doc['hearing_cycle'] != 0:
                ws_doc['xgws'] = relevant_doc


def add_aug_data2doc(ws_doc, court_map, relevant_mapping, cause_per_year, 
            litigant_paragraph_per_year, litigant_per_year, claims_per_year,
            result_type_per_year):
    docId = ws_doc['s5']
    add_aug_court_data(ws_doc, court_map)
    add_aug_cause_data(ws_doc, docId, cause_per_year)
    add_aug_litigant_paragraph_data(ws_doc, docId, litigant_paragraph_per_year)
    add_aug_litigant_data(ws_doc, docId, litigant_per_year)
    add_aug_claims_data(ws_doc, docId, claims_per_year)
    add_aug_result_type_data(ws_doc, docId, result_type_per_year)
    add_aug_relevant_doc(ws_doc, relevant_mapping)
    aug.add_aug_officers_data(ws_doc)
    aug.add_aug_judicial_procedure(ws_doc)
    aug.add_aug_law_and_article(ws_doc)
    aug.add_aug_is_final(ws_doc)
    aug.add_aug_keywords_data(ws_doc)


def read_prepare_data4all_year(ws_settings):
    low_q_pos_dict = uf.make_filter(ws_settings.clt_filter)
    setting_and_mapping = uf.read_setting_and_mapping_file(ws_settings.settings_and_mappings_file)
    court_map = uf.read_json_file(ws_settings.court_map_table)
    relevant_mapping = uf.read_json_file(ws_settings.aug_relevant_mapping)
    return low_q_pos_dict, setting_and_mapping, court_map, relevant_mapping


def read_prepare_data4year(ws_settings, year):
    cause_per_year = uf.read_json_file(os.path.join(ws_settings.aug_cause, str(year) + '.json'))
    litigant_paragraph_per_year = uf.read_json_file(os.path.join(ws_settings.aug_litigant_paragraph, str(year) + '.json'))
    litigant_per_year = uf.read_json_file(os.path.join(ws_settings.litigant_other_info, str(year) + '.json'))
    claims_per_year = uf.read_json_file(os.path.join(ws_settings.aug_claims, str(year) + '.json'))
    result_type_per_year = uf.read_json_file(os.path.join(ws_settings.aug_case_result_type, str(year) + '.json'))
    return cause_per_year, litigant_paragraph_per_year, litigant_per_year, \
            claims_per_year, result_type_per_year


def generate_ws_docs(batch_size, year, low_q_pos_dict, setting_and_mapping, court_map, relevant_mapping):
    ws_settings = Settings()
    cause_per_year, litigant_paragraph_per_year, litigant_per_year, \
            claims_per_year, result_type_per_year = read_prepare_data4year(ws_settings, year)

    ws_docs = list()
    for wenshu_file, idx, ws_doc in iterator.read_wenshu_with_filter(
            os.path.join(ws_settings.wenshu_path, str(year)), low_q_pos_dict):
        
        add_aug_data2doc(ws_doc, court_map, relevant_mapping, cause_per_year, 
                litigant_paragraph_per_year, litigant_per_year, claims_per_year, result_type_per_year)
        ws_doc = delete_no_need_field(ws_doc, setting_and_mapping['mappings'])
        
        ws_docs.append(ws_doc)
        
        if len(ws_docs) >= batch_size:
            yield ws_docs
            ws_docs = list()
    if ws_docs:
        yield ws_docs


def recreate_index(es, index_name, body):
    try:
        es.indices.delete(index_name)
    except:
        print("索引还未创建。")
    print("现在开始创建索引...")
    es.indices.create(index_name, body)


def check_index_exists():
    return True


def index_docs(es, index_name, docs):
    assert check_index_exists()
    for doc in docs:
        es.index(index_name, doc)
    es.indices.flush(index_name)


def hand_bulk_except(bulk_list, e):
    '''处理 BulkIndexError，即 bulk 索引文件的错误。
    
    处理方式：建一个文件夹，把想 bulk 索引的内容存入文件。
    并打印错误内容和错误类型。
    
    Args:
        bulk_list: 想 bulk 索引的内容。
    Returns: 无
    Raises:
    '''
    ws_settings = Settings()
    uf.write_json_file(bulk_list, ws_settings.error_log)
    print(e)
    print(type(e))


def bulk_docs(es, docs_with_index_name):
    assert check_index_exists()
    try:
        bulk(es, docs_with_index_name)
    except BulkIndexError as e:
        hand_bulk_except(docs_with_index_name, e)


@uf.timing_deco
def insert_wenshu_by_year(year, ws_settings, es, low_q_pos_dict, setting_and_mapping, court_map, relevant_mapping):
    for ws_docs in generate_ws_docs(ws_settings.batch_size, year, low_q_pos_dict, setting_and_mapping, court_map, relevant_mapping):
        ws_docs = [{'_index': ws_settings.index_name, '_id': ws_doc['s5'], '_source': ws_doc} for ws_doc in ws_docs]
        bulk_docs(es, ws_docs)


@uf.timing_deco
def insert_wenshu():
    ws_settings = Settings()

    es = uf.get_es(ws_settings)
    low_q_pos_dict, setting_and_mapping, court_map, relevant_mapping = read_prepare_data4all_year(ws_settings)

    # recreate_index(es, ws_settings.index_name, setting_and_mapping)

    for year in range(2011, 2019):
        insert_wenshu_by_year(year, ws_settings, es, low_q_pos_dict, setting_and_mapping, court_map, relevant_mapping)


if __name__ == '__main__':
    insert_wenshu()