import json


class CauseOfCasePath(object):
    '''案由也是有等级的，按等级从上往下是一棵树，获取案由路径上各等级案由
    
    案由的标准文件参考：json_file/案由2019-11-06.json
    任给一个案由ID列表，获取每个案由ID及其上级案由，加入到 source 字典中。
    自下而上的访问适合用节点列表，并借助 ID->pos 的字典。
    
    '''
    
    def __init__(self, cause_of_case_standard_file):
        '''初始化案由路径类，构造 node_list 和 id2pos_dict
        
        Args:
            path: 案由的标准文件，读取文件，文件中保存案由的列表，列表的每个元素是一个字典，可以看成一个节点。
        
        Returns:
        
        Raises:
        '''
        with open(cause_of_case_standard_file, encoding='utf-8') as fp:
            self.node_list = json.load(fp)  # 读取以前拿到的案由标准表，它是一个列表
            
        self.id2pos_dict = dict()  # 构建字典：id -> pos
        for pos, node in enumerate(self.node_list):
            id = node['id']
            self.id2pos_dict[id] = pos
        
        
    def get_path_with_ayname(self, id):
        '''根据案由ID获取案由路径，也就是案由本级及上级所有案由
        
        id -> pos -> node -> parent_id -> parent_pos -> parent_node -> ...
        其中最关键的是 id -> pos
        
        Args:
            id，案由ID
            
        Returns:
            path：它是一个列表，每个元素是路径上每个案由的 ID 和内容组成的元组
            
        Raises:
        '''
        path = list()
        
        pos = self.id2pos_dict[id]
        node = self.node_list[pos]
        path.append((id, node['text']))
        
        parent_id = node['parent']
        while parent_id != '#':
            parent_pos = self.id2pos_dict[parent_id]
            parent_node = self.node_list[parent_pos]
            path.append((parent_id, parent_node['text']))
            
            parent_id = parent_node['parent']
            
        return path


    def get_path(self, id):
        path = list()
        
        pos = self.id2pos_dict[id]
        node = self.node_list[pos]
        path.append(id)
        
        parent_id = node['parent']
        while parent_id != '#':
            parent_pos = self.id2pos_dict[parent_id]
            parent_node = self.node_list[parent_pos]
            path.append(parent_id)
            
            parent_id = parent_node['parent']
            
        return path