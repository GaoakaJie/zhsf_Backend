from html.parser import HTMLParser


class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.parse_result = list()
        self.flag = 0
    
    def handle_starttag(self, tag, attrs):
        if tag == 'div' or tag == 'p' or tag == 'span':
            self.flag = 1
        else:
            self.flag = 0
            
    def handle_data(self, data):
        if self.flag == 1:
            if data.strip():
                self.parse_result.append(data.strip())
            self.flag = 0
        else:
            pass