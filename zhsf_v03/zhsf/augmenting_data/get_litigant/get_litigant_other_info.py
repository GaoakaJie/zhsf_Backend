import os
import re

from zhsf.settings.settings import Settings
from zhsf.utils import util_functions as uf


def get_part(litigant, roles):
    role = re.split('（.*?）', litigant['role'])[0]
    return roles[role]


def determine_people(basic_info, litigant):
    return re.search(r'[男女]', basic_info) or re.search(r'出生', basic_info) or \
            re.search(r'农民', basic_info) or re.search(r'被刑事拘留', basic_info) or \
            re.search(r'被逮捕', basic_info) or (litigant['name'] and len(litigant['name']) <=3)


def determine_company(basic_info):
    return re.search(r'公司', basic_info) or re.search(r'有限', basic_info) or \
            re.search(r'法定代表人', basic_info) or re.search(r'董事', basic_info)


def determine_edu_institution(basic_info):
    return re.search(r'大学', basic_info) or re.search(r'研究所', basic_info)


def get_litigant_category(litigant):
    '''获取当事人的类型
    
    {1: '自然人', 2: '企事业法人', 3: '教研机构', 4: '其他'}
    不够精准，尤其是教研机构
    
    '被告西安市雁塔区铺尚村村委会', '被告西安市雁塔区铺尚村第三村民小组' 属于什么？
    
    Args:
        each_litigant_info: 每个当事人的信息
        
    Returns:
        返回当事人类型
        
    Except: 
    '''
    basic_info = re.split('\n', litigant['other'], maxsplit=1)[0]
    if determine_people(basic_info, litigant):
        return 1
    if determine_company(basic_info):
        return 2
    if determine_edu_institution(basic_info):
        return 3
    return 4


def get_representatives(litigant):
    role_p = re.compile(r'^[^\[]{0,4}(' + '代表人' + '(（[^（）]{1,15}）)?)' + '[：:]?(.*?)[，。,\n]', re.M)
    result = re.findall(role_p, litigant['other'])
    return [r[2] for r in result]


def get_attorney_ps(litigant):
    attorney_ps = list()
    for line in re.split(r'\n', litigant['other']):
        if '代理人' in line or '辩护人' in line:
            attorney_ps.append(line)
    return attorney_ps


def get_firm_p(name):
    return re.compile('[，,]([^，,]+?' + name + ').*$')


def get_attorney_firm_from_attorney_p(attorney_p):
    if re.search(get_firm_p('事务所'), attorney_p):
        attorney_p_head, firm, _ = re.split(get_firm_p('事务所'), attorney_p)
    elif re.search(get_firm_p('服务所'), attorney_p):  # '服务所?'不行，不能仅仅是服务二字
        attorney_p_head, firm, _ = re.split(get_firm_p('服务所'), attorney_p)
    else:
        attorney_p_head = attorney_p
        firm = None
    return attorney_p_head, firm


def get_role_p(name):
    return re.compile(r'^[^\[\n]*(' + name + '(（[^（）]{1,15}）)?)[：:]?', re.M)


def get_attorney_name_from_attorney_p(attorney_p_head, firm):
    attorney_p_middle = None
    for r in ['代理人', '辩护人']:
        if re.search(get_role_p(r), attorney_p_head):
            attorney_p_middle = re.split(get_role_p(r), attorney_p_head)[-1]
    
    '''
    if firm:
        name = re.split(r'[，,、]', attorney_p_middle)
    else:
        try:
            tmp = re.split(r'[，,。]', attorney_p_middle)[0]
            name = re.split(r'、', tmp)
        except:
            print(attorney_p_head, firm)
    
    name = None
    try:
        tmp = re.split(r'[，,。]', attorney_p_middle)[0]
        name = re.split(r'、', tmp)
    except:
        print(attorney_p_head)
        print(firm)
    '''
    if attorney_p_middle:
        tmp = re.split(r'[，,。]', attorney_p_middle)[0]
        name = re.split(r'、', tmp)
    else:
        name = []
    return name


def get_attorney_type_by_firm(firm):
    if firm:
        if '事务所' in firm:
            return '律师'
        elif '服务所' in firm:
            return '基层法律服务工作者'
    return None



def create_attorney_with_info_and_add2list(firm, name, attorney_type, attorneys):
    for n in name:
        attorney = dict()
        attorney['name'] = n
        if firm:
            attorney['firm'] = firm
        if attorney_type:
            attorney['type'] = attorney_type

        attorneys.append(attorney)


def get_attorneys(attorney_lines):
    attorneys = list()
    for attorney_p in attorney_lines:
        attorney_p_head, firm = get_attorney_firm_from_attorney_p(attorney_p)
        name = get_attorney_name_from_attorney_p(attorney_p_head, firm)
        attorney_type = get_attorney_type_by_firm(firm)

        create_attorney_with_info_and_add2list(firm, name, attorney_type, attorneys)
        
    return attorneys


def get_attorney_litigant_part(cal):
    parts = list()
    for idx, r in enumerate(['原告', '被告', '第三人']):
        if re.search(r, cal):
            parts.append(str(idx+1))
    return parts


def add_commom_attorney2litigant(ws_litigants, docId):
    for cal in ws_litigants[docId]['CAL']:
        common_attorneys = get_attorneys([cal])
        parts = get_attorney_litigant_part(cal)
        for part in parts:
            for litigant in ws_litigants[docId]['LP']:
                if litigant['part'] == part:
                    litigant['attorneys'].extend(common_attorneys)


def add_lawyer2different_set(litigant, attorneys_part):
    for attorney in litigant['attorneys']:
        if attorney.get('type') and attorney['type'] == '律师':
            attorneys_part.add(attorney['name'] + '#' + attorney['firm'])


def add_attorney2set(attorneys_part1, attorneys_part2, ws_litigants, docId):
    for litigant in ws_litigants[docId]['LP']:
        if litigant['part'] == '1':
            add_lawyer2different_set(litigant, attorneys_part1)
        elif litigant['part'] == '2':
            add_lawyer2different_set(litigant, attorneys_part2)


def add_opposite_lawyer_set(litigant, attorneys_part):
    for attorney in litigant['attorneys']:
        if attorney.get('type') and attorney['type'] == '律师' and attorneys_part:
            attorney['opposite_name'] = list(attorneys_part)
            attorney['opposite_firm'] = [re.split("#", attorney_combination)[-1] 
                                                for attorney_combination in attorneys_part]


def add_opposite_lawyer_set2litigant_attorney(attorneys_part1, attorneys_part2, ws_litigants, docId):
    for litigant in ws_litigants[docId]['LP']:
        if litigant['part'] == '1':
            add_opposite_lawyer_set(litigant, attorneys_part2)
        elif litigant['part'] == '2':
            add_opposite_lawyer_set(litigant, attorneys_part1)


def add_opposite_lawyer2litigant_attorney(ws_litigants, docId):
    attorneys_part1 = set()
    attorneys_part2 = set()
    add_attorney2set(attorneys_part1, attorneys_part2, ws_litigants, docId)
    add_opposite_lawyer_set2litigant_attorney(attorneys_part1, attorneys_part2, ws_litigants, docId)



@uf.timing_deco
def get_litigant_other_info(year):
    ws_settings = Settings()
    ws_litigants = uf.read_json_file(os.path.join(ws_settings.litigant_split, str(year) + '.json'))
    roles = uf.read_json_file(ws_settings.litigant_roles)

    for docId in ws_litigants:
        for litigant in ws_litigants[docId]['LP']:
            litigant['part'] = get_part(litigant, roles)
            litigant['category'] = get_litigant_category(litigant)
            litigant['representatives'] = get_representatives(litigant)
            litigant['attorneys'] = get_attorneys(get_attorney_ps(litigant))
        add_commom_attorney2litigant(ws_litigants, docId)
        add_opposite_lawyer2litigant_attorney(ws_litigants, docId)
    return ws_litigants


if __name__ == '__main__':
    ws_settings = Settings()

    for year in range(2011, 2019):
        uf.write_json_file(get_litigant_other_info(year), os.path.join(ws_settings.litigant_other_info, str(year) + '.json'))