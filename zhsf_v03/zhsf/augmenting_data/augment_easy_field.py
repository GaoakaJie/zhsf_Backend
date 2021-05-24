import re


def add_collegial_panel_members(ws_doc, officers):
    if ws_doc.get('s23') and re.search(r'合议', ws_doc['s23']) and len(officers) > 1:
        for idx, officer in enumerate(officers):
            officer['collegial_panel_members'] = [i.get('name_court') for i in officers[:idx] + officers[(idx + 1):]]


def add_aug_officers_data(ws_doc):
    '''根据尾部文本获取各个法官的职位和名称
    '''
    officers = list()
    
    rear = ws_doc.get('s28')
    if rear:
        for line in re.split(r'\n', rear):
            line = re.sub(r'\s', '', line)
            for i in ['审判长', '审判员', '人民陪审员']:
                if i in line:
                    tmp = re.split(i + r'：?', line)
                    officer = {"position": tmp[0] + i, "name": tmp[1]}
                    if ws_doc.get("court_name"):
                        officer['name_court'] = tmp[1] + "|" + ws_doc['court_name']
                    officers.append(officer)
                    break
            
    if officers:
        add_collegial_panel_members(ws_doc, officers)
        ws_doc['officers'] = officers


def add_aug_judicial_procedure(ws_doc):
    '''根据文书中 s9 和 s10 两个字段，获取审判程序
    
    审判程序大类就是根据字符串中是否有这个字来判断。
    '''
    procedure = ""
    
    if ws_doc.get('s9'):
        ws_doc['lvl1_spcx'] = ws_doc['s9']
        procedure += ws_doc['s9']
        
    if ws_doc.get('s10'):
        ws_doc['lvl2_spcx'] = ws_doc['s10']
        procedure += ws_doc['s10']
        
    for i in ["一审", "二审", "再审"]:
        if i in procedure:
            ws_doc['spcx_category'] = i
            break
    if not ws_doc.get('spcx_category'):
        ws_doc['spcx_category'] = "其他审理程序"


def add_aug_law_and_article(ws_doc):
    if ws_doc.get('s47'):
        ws_doc['legal_basis'] = [{"article": i['tkx'], 
                                  "law": i['fgmc'], 
                                  "law_article": (i['fgmc'] + i['tkx'])} for i in ws_doc['s47'] if i.get('tkx') and i.get('fgmc')]


def add_aug_is_final(ws_doc):
    if ws_doc.get('s27'):
        if re.search(r'本[^，。；]*?终审', ws_doc['s27']) or re.search(r'为终审', ws_doc['s27']):
            ws_doc['is_final_judgment'] = True



def add_aug_keywords_data(ws_doc):
    if ws_doc.get('s45'):
        ws_doc['keywords'] = ws_doc['s45']