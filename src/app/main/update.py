import requests
import time
import os
import csv
import re
import json
from html.parser import HTMLParser

from ..defines import *

class MyHTMLParser(HTMLParser):
    in_page_body = False
    in_h2 = False
    in_p = False
    get_pre_h2 = False
    lines = []

    def myInit(self):
        self.in_page_body = True
        self.in_h2 = False
        self.in_p = False
        self.in_span = False
        self.get_pre_h2 = False
        self.lines = []
        self.title = ''

    def handle_starttag(self, tag, attrs):
        if tag == 'div' and attrs == [('class', 'page-body')]:
            self.in_page_body = True
        if not self.in_page_body:
            return
        if tag == 'h2':
            self.title = ''
            self.in_h2 = True
        elif tag == 'p':
            self.in_p = True

    def handle_endtag(self, tag):
        if not self.in_page_body:
            return
        if tag == 'div':
            self.in_page_body = False
        elif tag == 'h2':
            self.in_h2 = False
            if len(self.lines) > 0 and len(self.lines[-1]) == 0:
                print('[DEBUG]',self.lines[-2])
                self.lines.pop()
                self.lines.pop()
            if '2' in self.title and '.' in self.title:
                self.get_pre_h2 = True
                self.lines.append(self.title.strip().replace('（','(').replace('）',')').replace(' ', '').replace('\n',''))
                self.lines.append('')
        elif tag == 'p':
            self.in_p = False

    def handle_data(self, data):
        if not self.in_page_body:
            return
        if self.in_h2:
            self.title += data
        elif self.get_pre_h2 and self.in_p and '5' in data:
            self.lines[-1] += data.strip().replace('（','(').replace('）',')').replace(' ', '').replace('\n','')
        elif len(data.strip()) > 0:
            print('[DEBUG]', data)
            
def process_html(name, html):
    html = json.loads(html)['text']['cn_content']
    parser = MyHTMLParser()
    parser.myInit()
    parser.feed(html)
    out_file = os.path.join(save_path, salon_record_file % (name))
    print('WRITE', name, 'info to', out_file)
    with open(out_file, 'w', encoding='utf8') as f:
        f.write('\n'.join(parser.lines))

def update_text():
    update_time = time.time()
    failed = False

    if not os.path.exists(save_path):
        os.makedirs(save_path) 

    for record in salon_records:
        print('FETCH', record, 'info')
        try:
            html = requests.get(zy_article_url + record[1]).text
            process_html(record[0], html)
        except Exception as e:
            print('[ERROR] ', e)
            failed = True

    if not failed:        
        out_file = os.path.join(save_path, update_time_file)
        with open(out_file, 'w', encoding='utf8') as f: 
            f.write(str(update_time))

def get_map():
    sid_data = {}
    salons = {}
    sid_list_pattern = r'(\d+(\(\d+\))?、)*\d+(\(\d+\))?'
    sid_set = set()

    names = [x[0] for x in salon_records]
    for name in names:
        print('LOAD', name, 'data')
        in_file = os.path.join(save_path, salon_record_file % (name))
        sid_data[name] = []
        salons[name] = []
        with open(in_file, 'r', encoding='utf8') as f:
            for line in f.readlines():
                s = line.replace(' ', '').replace('\n', '').rstrip('、')
                if '.' in line:
                    title = line.strip('\n').strip(' ')
                    print('  Loading salon', title)
                    salons[name].append(title)
                    sid_data[name].append([])
                else:
                    sid_list = s.split('、')
                    sid_data_now = []
                    for sid in sid_list:
                        sid_now = ''
                        count_now = 0
                        if '(' in sid:
                            sid_now = sid.split('(')[0]
                            count_now = int(sid.split('(')[1].replace(')', ''))
                        else:
                            sid_now = sid
                            count_now = 1
                        for i in range(count_now):
                            sid_data[name][-1].append(sid_now)
                        if sid_now not in sid_set:
                            sid_set.add(sid_now)
                    # sid_data[name].append(sid_data_now)

    stus = {}
    for sid in sid_set:            
        stu = UniObject()
        stu.count_zy = 0
        stu.count_other = 0
        stu.acts_zy = []
        stu.acts_other = []
        for name in names:
            for i in range(len(salons[name])):
                num = sid_data[name][i].count(sid)
                if num == 0:
                    continue
                if name not in other_set: 
                    stu.acts_zy.append((salons[name][i], num))
                    stu.count_zy += num
                else:
                    stu.acts_other.append((salons[name][i], num))
                    stu.count_other += num
        stus[sid] = stu
    return stus

def check_update_time(app):
    update_time = 0.0
    with open(os.path.join(save_path, 'update_time.text'), 'r', encoding='utf8') as f:
        update_time = float(f.read())
    
    u_time = time.localtime(update_time)
    now_time = time.time()
    n_time = time.localtime(now_time)
    failed = False
    if (u_time.tm_year, u_time.tm_mon, u_time.tm_mday, u_time.tm_hour) != (n_time.tm_year, n_time.tm_mon, n_time.tm_mday, u_time.tm_hour):
        try:
            update_text()
            app.table = get_map()
            u_time = n_time
        except Exception as e:            
            failed = True
    if not failed:
        ret = time_str % (u_time.tm_year, u_time.tm_mon, u_time.tm_mday, u_time.tm_hour, u_time.tm_min, u_time.tm_sec)
    else:
        ret = 'Unknown'
    return ret
