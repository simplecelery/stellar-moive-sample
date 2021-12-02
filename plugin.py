import csv
import os
import codecs
import io

PAGE_SIZE = 18

class Plugin:
    def __init__(self):
        self.categories = set()
        self.data = []
        self.q = ''
        self.current_category = '全部'
        self.page = 1         

    def read_file(self, path):
        size = min(32, os.path.getsize(path))
        raw = open(path, 'rb').read(size)
        encoding = 'utf-8-sig' if raw.startswith(codecs.BOM_UTF8) else 'utf-8'
        with io.open(path, 'r', encoding=encoding) as file:
            return file.read()

    def load_data(self, str):           
        f = io.StringIO(str) 
        reader = csv.reader(f, delimiter=',', quotechar='\"')
        for row in reader:
            name, cover, summary, category, src = row
            if category:
                self.categories.add(category)
            sources = []
            for line in src.split('#'):
                line = line.strip()
                if line:
                    sname = url = ''
                    items = line.split('$')
                    if len(items) == 1:
                        sname, url = '正片', line
                    else:
                        sname, url, *_ = items
                    sources.append((sname, url))
            yield name, cover, summary, category, sources

    def load_data_from_local(self):
        data_path = os.path.join(os.path.dirname(__file__), 'data.csv')
        self.data = list(self.load_data(self.read_file(data_path)))   

    @property
    def filtered_data(self):
        qs = self.data
        q = self.q
        if q:
            qs = (i for i in qs if q in i[0]) 
        if self.current_category != '全部':
            qs = (i for i in qs if i[3] == self.current_category)
        return list(qs)
            
    @property
    def paged_data(self):
        page = self.page - 1
        return self.filtered_data[page * PAGE_SIZE : page * PAGE_SIZE + PAGE_SIZE]

    @property
    def page_count(self):
        return (len(self.filtered_data) + PAGE_SIZE - 1) // PAGE_SIZE

    @property
    def cur_page(self):
        return f'第 {self.page} 页'

    @property
    def max_page(self):
        return f'共 { self.page_count } 页'


if __name__ == '__main__':
    plugin = Plugin()
    print(plugin.data)