# -*- coding: utf-8 -*-
"""
Created on Tue Nov 10 16:59:17 2020

@author: SKY_SHY
"""

import requests


from requests.auth import HTTPBasicAuth


from datetime import datetime as dt
from collections import Counter
from prettytable import PrettyTable
from datetime import timedelta


import time

class Timer():
    
    
    def __init__(self, a_req):
        self.req = a_req
        self.t_req = 60
        self.reqs_counter = 0
        self.n_reqs = 1
    
    def set_nreqs(self, n):
        self.n_reqs = n
        
    def set_treq(self, t):
        self.t_req = t
        
    def req_count(self):
        self.reqs_counter += 1
        
        
    def send_request(self, url, page = 1, per_page = 100, 
                     state = "closed", order="desc", since = '2008-01-01', 
                     until = str(dt.now())):
        
        objs = self.req.send_request(url, page=page, per_page=per_page, 
                                     state=state, order=order, since=since, 
                                     until=until)

        self.req_count()
        return objs
    

    
    def get_objs(self, url, page = 1, per_page = 100, state = "closed", 
                 order="desc", since = '2008-01-01', until = str(dt.now())):
        
        
        objs = self.send_request(url, page=page, per_page=per_page, 
                                      state=state, order=order, since=since, 
                                      until=until)
        
        if objs.status_code == 403:
            self.wait()
            
            objs = self.send_request(url, page=page, per_page=per_page, 
                                      state=state, order=order, since=since, 
                                      until=until)
        
        if objs.status_code == 401:
            raise ConnectionError("От пользователя поступил неправильный запрос или некорректная работа сервера")

            
            return self.send_request(url, page=page, per_page=per_page, 
                                      state=state, order=order, since=since, 
                                      until=until)
        return objs
    
    def wait(self,):
        self.n_reqs -= self.reqs_counter
        z = self.n_reqs*self.t_req
        print("Превышено количество запросов в ед. времени \n Подождите %s" % z + "секунд")
        time.sleep(z)
        self.reqs_counter = 0
        


class parseurl_PubRepo():
    
    def last_page_num(self, a_string):
        return int(a_string.split("; ")[1].split("&")[1][5:])
    
    def is_link(self, url, state = "closed", order="desc",
                        since = '2008-01-01', until = str(dt.now())):
        
        for p in range(1, 4):
            objs = tmr.get_objs(url, page=p, state=state, order=order, 
                                      since=since, until=until)
            
            length = len(objs.json())
            if length>0 and length<100:
                return 'next; last&page=%s' % p
            
        return 'next; last&page=0'
            
            
    
    def get_pages_links(self, url, state = "closed", order="desc",
                        since = '2008-01-01', until = str(dt.now())):
        
        
        objs = tmr.get_objs(url, state=state, order=order, 
                                      since=since, until=until)
        
        if 'link' in objs.headers:
            return objs.headers['link']
        
        return self.is_link(url, state=state, order=order, since=since,
                            until = until)
        

        
    
    def get_owner__repo(self, url):
        return url.split('/')[-2:]
    
    def get_type(self, a_req):
        return a_req.tyype
    
    def names(self, url, a_req):
        owner, repo = self.get_owner__repo(url)
        return dict(owner = self.get_owner__repo(url)[0], 
                    repo = self.get_owner__repo(url)[1], 
                    type = self.get_type(a_req))
    
    def clear_url(self,url):
        ind = url.find("git/")
        return url[:ind] + url[ind+4:]

pr = parseurl_PubRepo()
   
class Request():
    
    tyype = "pulls"
    allow_types = ("pulls", "issues", "commits", "branches-where-head")
    is_branches_search = False
    
    
    def ErrorType(self, a_type):
        if a_type not in self.allow_types:
            raise TypeError("был введён неверный тип. \n Долпустимые типы: %s, %s, %s, %s" 
                            % self.allow_types)
            
    def to_search_branches(self):
        self.is_branches_search = True
    
    def set_type(self, a_type):
        self.ErrorType(a_type)
        self.tyype = a_type
        
    def get_type(self,):
        return self.tyype
    

    
    def get_params(self, page = 1, per_page = 100, state = "closed", order="desc", 
                   since = '2008-01-01', until = str(dt.now())):
        
        return {"state":state, "page":page, "per_page": per_page, 
                "since": since, "until": until, "order": order}
    
    
    
    #uses in  commits, issues, pulls only
    def template_url(self,):
        return "https://api.github.com/repos/%(owner)s/%(repo)s/%(type)s"
    
    
    
    def get_request(self,):
        if self.tyype == "issues":
            return ISSUES()
        elif self.tyype == "commits":
            if self.is_branches_search:
                return COMMITS_N_BRANCHES()
            else:
                return COMMITS_ONLY()
        elif self.tyype == "branches-where-head":
            return BRANCHES()
        return PULLS()
    
    def request(self, url, page = 1, per_page = 100, state = "closed",
                order = "desc", since = '2008-01-01', until = str(dt.now())):
        
        return r1.get(self.template_url() % pr.names(url, self), params = 
                      self.get_params(page=page, per_page=per_page, state=state, 
                                      order=order, since=since, until=until))
    
    
    def send_request(self, url, page = 1, per_page = 100, state = "closed",
                order = "desc", since = '2008-01-01', until = str(dt.now())):
        return self.get_request().request(url, page=page, per_page=per_page, 
                                          state=state, order=order,
                                          since=since, until=until)
    
    def get_stat(self, items, state="closed", period = ('2008-01-01', str(dt.now())), branch_name = "master"):
        since, until = period
        pulls = self.get_recorder(state)
        print("---ПРОСМОТР РЕЗУЛЬТАТОВ")
        for item in items:

            if self.def_isstate(state, item, period):
                if self.tyype == "issues":
                    try: 
                        item['pull_request']
                    except KeyError: 
                        pulls[state]+=1
                        continue
                
                else:
                    pulls[state] += 1
                if state == "open":
                    if self.isold(item, until):
                        pulls["old"] += 1

        return pulls
    
    def stat(self, items, state = "closed", period = ('2008-01-01', str(dt.now())), branch_name = "master"):
        return self.get_request().get_stat(items, state = state, period = period, 
                                           branch_name = branch_name)
    
    
    
    def adding_stat(self, rec, stat):
        for cat in stat.keys():
            rec[cat] += stat[cat]
        return rec
    
    
    def add_stat(self,rec, stat):
        return self.get_request().adding_stat(rec, stat)
    
    
    def get_recorder(self, state="closed"):
        if state == "open":
            return {"open": 0, "old":0}
        return {"closed":0,}
    
    def recorder(self,state="closed"):
        return self.get_request().get_recorder(state=state)
    
    
    def printout(self, period, recs, branch_name = "master"):
        for cat in recs.keys():
            print("Количеcтво %s " % cat + self.tyype + ": %s" % recs[cat])
        print("за период %s --- %s"  % period)
        
    def printing(self, period, recs, branch_name="master"):
        return self.get_request().printout(period, recs, branch_name=branch_name)
    

class ITEMS(Request):
    
    
    def state(state):
        def isstate(self, st, item, period):
            if st == "open":
                return self.isopen(item, period)
            return self.isclosed(item, period)
        return isstate
    
    @state
    def def_isstate(self, st, item, period):
        pass
    
    
    def isclosed(self, item, period):
        since, until = period

        if item["closed_at"] >= since and item["closed_at"] <= until:
            return True
        return False
    
    def isopen(self, item, period):
        since, until = period
        if  item["created_at"] <= until:
            if item["closed_at"] == None:
                return True
            if not self.isclosed(item, period):
                return True
        return False
    
    def isold(self,item, until):
        deadline = dt.strptime(item['created_at'], "%Y-%m-%dT%H:%M:%SZ") + timedelta(days=self.days) 

        if item['closed_at'] == None and deadline > dt.strptime(until, "%Y-%m-%d"):
            return False
        
        if item['closed_at'] == None and deadline <= dt.strptime(until, "%Y-%m-%d"):
            return True
  
        if deadline < dt.strptime(item['closed_at'], "%Y-%m-%dT%H:%M:%SZ") and deadline <= dt.strptime(until, "%Y-%m-%d"):
            return True

        return False
        
        
class ISSUES(ITEMS):
    tyype = "issues"
    days = 14
    


class PULLS(ITEMS):
    
    tyype = "pulls"
    days = 30

    
class COMMITS(Request):
    
    tyype = "commits"
    
    
    def adding_stat(self, rec, stat):
        rec += stat
        return rec
    
    def get_recorder(self,state="closed"):
        return []
    
    
    def printout(self, period, recs, branch_name = ""):
        top_row = ["Участник", "Число коммитов за период: %s --- %s" % period 
                   + " в ветке '%s'" %  branch_name]
        recs = sorted(dict(Counter(recs)).items(), key = lambda x:x[1], reverse=True)[:30]
        tab = PrettyTable(top_row)
        for rec in recs:
            tab.add_row(rec)
            
        print(tab)
        
    
    
    def get_nameAuthor(self, commit):
        try:
            return commit["author"]["login"]
        except TypeError:
            return False
    
    
    
class COMMITS_ONLY(COMMITS):
    
    
    def get_stat(self, items, state="closed", period = ('2008-01-01', str(dt.now())), branch_name="master"):
        logins =[]
        print("---ПРОСМОТР РЕЗУЛЬТАТОВ")
        for commit in items:
            if not self.get_nameAuthor(commit):
                continue
            logins.append(self.get_nameAuthor(commit))
        
        return logins
    

class COMMITS_N_BRANCHES(COMMITS):
    
    
    
    def get_stat(self, items, period = ('2008-01-01', str(dt.now())), branch_name="master"):
        logins =[]
        print("---ПРОСМОТР ВЕТОК")
        for commit in items:
            if not self.commit_inBranch(
                    pr.clear_url(commit["commit"]["url"]), branch_name):
                continue
            if not self.get_nameAuthor(commit):
                continue
            logins.append(self.get_nameAuthor(commit))
                
        return logins
    
    
    def is_inBranch(self, branch_name, branches):
        for branch in branches:
            if branch_name == branch["name"]:
                return True
        return False
    
    
    def check_branch_name(self, url_sha, br, branch_name):
        r = tmr.get_objs(br, url_sha)
        print("коммит", r.json())

        return self.is_inBranch(branch_name, r.json())
  
      
    def commit_inBranch(self, url_sha, branch_name):
        br = Request()
        br.set_type("branches-where-head")

        return self.check_branch_name(url_sha, br, branch_name)
    
    
    
class BRANCHES(Request):
    
    tyype = "branches-where-head"
    
    def request(self, url, page = 1, per_page = 100, state = "closed",
                order = "desc", since = '2008-01-01', until = str(dt.now())):
        
        return r1.get(url + "/" + self.tyype, headers = 
                      {"Accept": "application/vnd.github.groot-preview+json"})
  

def def_type(item):
    if item == "contributors":
        return "commits"
    return item


import argparse

import re

def isUrl(url):
    scheme = url.split("/")
    if 'github.com' not in scheme:
        raise parser.error("Это не репозиторий github.com")
    if 'https:' in scheme and len(scheme) <5:
        raise parser.error("Это не репозиторий")
    if 'https:' not in scheme and len(scheme) <3:
        raise parser.error("Это не репозиторий")
        
    for el in scheme[:3]:
        match = re.fullmatch('\w+[.]\w+', el)
        if match:
            return url
    
    raise parser.error("url-адрес репозитория имеет некорректный формат")
    
    
def isType(a_type):
    a_type = a_type.lower()
    types = ("contributors", "issues", "pulls")
    if a_type not in types:
        parser.error("Недопустимое значение параметра type. Допустимыми являются %s, %s, %s" 
                         % types)
    return a_type
    
    

def isState(state):
    if state not in ("closed", "open"):
        parser.error("Недопустимое значение состояния")
    return state


def isDate(period):
    matches = ('-\w{3}---\d\d\d\d-\d\d-\d\d', '\d\d\d\d-\d\d-\d\d---\w{3}', 
               '-\w{3}---\w{3}', '\d\d\d\d-\d\d-\d\d---\d\d\d\d-\d\d-\d\d')
    d_formats = ("'YYYY-MM-DD---YYYY-MM-DD'", "'-INF---YYYY-MM-DD'", "'YYYY-MM-DD---INF'")
    count_matches=0
    for temp in matches:
        match = re.fullmatch(temp, period)
        if match:
            count_matches+=1
            break
    if count_matches>0:
        parser.error("Неверный формат периода. Верный формат период один из следующих: %s, %s, %s"
                     % d_formats)
        
    period = period.replace("'", "")
    period = period.split('---')
    if len(period)<2:
        parser.error("Неверный формат периода. Верный формат период один из следующих: %s, %s, %s"
                     % d_formats)
    if period[0] > period[1] or period[0]=='INF':
        parser.error("Дата начала анализа не может быть меньше даты конца анализа")
    if period[0] == '-INF':
        period[0] = "2008-01-01"
    if period[1] == "INF":
        period[1] = str(dt.date(dt.now()) + timedelta(days=1))
    for date in period:
        try:
            dt.strptime(date, "%Y-%m-%d")
        except ValueError:
            message = "Неверный формат даты '{}'".format(date)
            raise argparse.ArgumentTypeError(message)
    return tuple(period)


period_h = '''\
интервал времени на котором проводится анализ. 
Указаваются даты начала и окончания анализа* в формате ISO: 'YYYY-MM-DD---YYYY-MM-DD'

*Если одно из крайних значений интервала не требуется определять, то 
вместо указания соотвествующей даты используется INF: 
    '-INF---YYYY-MM-DD' - если не ограничено начало анализа
    'YYYY-MM-DD---INF' - если не ограничен конец анализа. 
Если же интервал анализа не ограничен ни сверху ни снизу, то пропустите параметр --period'''



parser = argparse.ArgumentParser(description = 'repo analyser', 
                                 formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("--url", type = isUrl, help = "url-адрес репозитория", required=True)
parser.add_argument("--type", type = isType, help = "тип искомого request: %s, %s, %s" % 
                    ("pulls", "issues", "contributors"), default ="pulls", required=True)

parser.add_argument("--state", type = isState, help = "состояние искомых pulls или issues: open, closed. По умолчанию - closed", default="closed",)

parser.add_argument("--period", type = isDate, help =  period_h, 
                    default ="2008-01-01---" + str(dt.date(dt.now())))




args = parser.parse_args()

url = args.url

tyype = def_type(args.type)

state = args.state

period = args.period



username = "*****"
password = input("ВВЕДИТЕ ВАШ СГЕНЕРИРОВАННЫЙ ТОКЕН: ")

r1 = requests.Session()

r1.auth = HTTPBasicAuth(username, password)

auth = r1.get('https://api.github.com/user',)

if auth.status_code==401:
    raise ConnectionError("От пользователя поступил неправильный запрос или некорректная работа сервера")
    
req = Request()
tmr = Timer(req)



req.set_type(tyype)


last_page = pr.last_page_num(pr.get_pages_links(url, since=period[0], until=period[1]))
tmr.set_nreqs(last_page+3)


def count_items(a_req, url_repo, last_page, state = "closed", order = "desc", 
                period =  ('2006-01-01', str(dt.now())), branch_name="master"):
    page = 1
    records = req.recorder(state=state)
    while page < last_page + 1:
        r = tmr.get_objs(url_repo, page=page, state=state, order=order, 
                                      since=period[0], until=period[1])

        print("на странице № ", page,)
        stat = a_req.stat(r.json(), state = state, period=period, branch_name=branch_name)
        records = a_req.add_stat(records, stat)
        page += 1
        

    req.printing(period, records, branch_name=branch_name)
    

if __name__ == "__main__":
    count_items(req, url, last_page, state=state, period =  period,)
