#!/usr/bin/env python
#encoding: utf-8

#利用现成的接口获取子域名
#1、https://crt.sh/?q=%.aliyun.com&output=json
#2、http://api.hackertarget.com/hostsearch/?q=aliyun.com
#3、https://findsubdomains.com/subdomains-of/aliyun.com
#4、dns zone transfer

import logging, argparse
from random import choice
import os, re, json,sys
import dns.resolver, Queue, threading
import requests
from bs4 import BeautifulSoup

reload(sys)
sys.setdefaultencoding('utf8')
#console output log
logging.basicConfig(level = logging.INFO, format='%(asctime)s - %(levelname)s [%(filename)s:%(lineno)d]: %(message)s')

User_Agent = [
"Mozilla/5.0 (Windows; U; Windows NT 6.0; cs; rv:1.9.0.13) Gecko/2009073022 Firefox/3.0.13",
"Mozilla/5.0 (Windows; U; Windows NT 6.0; cs; rv:1.9.0.19) Gecko/2010031422 Firefox/3.0.19",
"Opera 9.4 (Windows NT 5.3; U; en)",
"Opera 9.4 (Windows NT 6.1; U; en)",
"Opera/9.64 (X11; Linux i686; U; pl) Presto/2.1.1",
]
#Set http request header
headers = {
    'User-Agent' : choice(User_Agent),
    'Referer' : '',
    'Cookie' : '',
}

#requests api_url
def get_url_content(url, timeout='', cookie='', allow_redirects=False, data=''):
    try:
        if cookie:
            headers['Cookie'] = cookie
        if timeout:
            timeout = timeout
        else:
            timeout = 10
        #proxies = { "http": "http://127.0.0.1:10800", "https": "http://127.0.0.1:10800", }
        proxies = {}
        post_data = {}
        if data:
            for d in data.split('&'):
                if d.find('=') != -1:
                    post_data[d.split('=')[0]] = d.split('=')[1]
            content = requests.post(url, headers = headers, data = post_data)
        else:
            content = requests.get(url, headers = headers, timeout = timeout, proxies = proxies)
        return content
    except requests.exceptions.ConnectionError as e:
       logging.error(str(e))

######################################
class AXFR(object):
    def __init__(self, domain):
        super(AXFR, self).__init__()
        self.domain = domain
        self.address = "https://crt.sh/"
        self.result = []

    def _get(self):
        try:
            url = "{0}?q=%.{1}&output=json".format(self.address, self.domain)
            api_content = get_url_content(url)

            if not api_content or api_content.status_code != 200:
                logging.error("AXFR get domain fail")
                return []

            json_domain = json.loads('[{}]'.format(api_content.text.replace('}{', '},{')))

            for (key,value) in enumerate(json_domain):
                self.result.append(value['name_value'])

            return list(set(self.result))


        except Exception as e:
            logging.error(str(e))
            return list(self.result)

######################################
class Hackertarget(object):

    def __init__(self,domain):
        self.domain = domain
        self.address = 'http://api.hackertarget.com/hostsearch/?q='
        self.result = []

    def _get(self):
        try:
            url = '{0}{1}'.format(self.address,self.domain)
            api_content = get_url_content(url)

            if not api_content or api_content.status_code != 200:
                logging.error("hackertaget get domain fail")
                return []

            regex = re.compile(r'([a-zA-Z0-9]+.{0})'.format(self.domain))
            for value in regex.findall(api_content.text):
                self.result.append(value)

            return list(set(self.result))

        except Exception as e:
            print(str(e))
            return self.result

######################################
class Findsubdomains(object):

    def __init__(self, domain):
        super(Findsubdomains, self).__init__()
        self.domain = domain
        self.address = "https://findsubdomains.com/subdomains-of"
        self.result = []


    def _get(self):
        try:
            url = "{0}/{1}".format(self.address, self.domain)
            api_content = get_url_content(url)

            if not api_content or api_content.status_code != 200:
                logging.error("findsubdomains get domain fail")
                return []

            regex = re.compile(r'([a-zA-Z0-9]+.{0})'.format(self.domain))
            for value in regex.findall(api_content.text):
                self.result.append(value)


            return list(set(self.result))

        except Exception as e:
            logging.error(str(e))
            return self.result

######################################
class Dns_zone(object):
    def __init__(self, domain):
        super(Dns_zone, self).__init__()
        self.domain = domain
        self.result = []

    def _get(self):
        console = os.popen('nslookup -type=ns {0}'.format(self.domain)).read()
        regex = re.compile('nameserver = ([\w\.]+)')
        dns_servers = regex.findall(console)

        for dns_server in dns_servers:
            console = os.popen('dig @{0} axfr {1}'.format(dns_server, self.domain)).read()
            
            regex1 = re.compile('([\w\.]+\.{0})'. format(self.domain))

            for value in regex1.findall(console):
                self.result.append(value)

            self.result = list(set(self.result))

        if len(self.result) > 0:
            logging.info('Found Dns-Zone-Transfer')
        else:
            logging.error('Not Found Dns-Zone-Transfer')

        return self.result

######################################

class Domain_check(object):

    def __init__(self, domain):
        self.domain = domain
        self.resolver = dns.resolver.Resolver()
        self.threading = 10
        self.result = []
        self.sub_domain = Queue.Queue()

    def _load_queue(self):
        for s in self.domain:
            if s:
                self.sub_domain.put(s)

    def _query(self, sub):
        try:
            target = '{0}'.format(sub)
            answer = self.resolver.query('{0}'.format(target),'A')
            for i in answer.response.answer:
                for j in i.items:
                    if j:
                        return target
        except Exception as e:
            logging.error(str(e))

    def _scan(self):
        while not self.sub_domain.empty():
            sub = self.sub_domain.get()
            subdomain = self._query(sub)
            if subdomain:
                self.result.append(subdomain)
            self.sub_domain.task_done()

    def _run(self):
        self._load_queue()
        for i in range(self.threading):
            t = threading.Thread(target=self._scan())
            t.start()
            #t.join()
            
        #work with queue.task_done()
        #block master untill queue is empty
        self.sub_domain.join()

        return list(set(self.result))
######################################

class Web_check(object):

    def __init__(self, domain):
        self.domain = domain
        self.resolver = dns.resolver.Resolver()
        self.threading = 10
        self.result = []
        self.sub_domain = Queue.Queue()

    def _load_queue(self):
        for s in self.domain:
            if s:
                self.sub_domain.put(s)

    def _query(self, sub):
        try:
            target = 'http://{0}'.format(sub) if not sub.startswith('http') else sub
            res = get_url_content(target, allow_redirects=True)
            if res:
                #coding
                #requests 从响应头中获取编码，如果content-type没有charset，则text对应到ISO-8859-1
                #get_encodings_from_content用正则匹配html获取编码
                if res.encoding == 'ISO-8859-1':
                    if len(requests.utils.get_encodings_from_content(res.content))>0:
                        res.encoding = requests.utils.get_encodings_from_content(res.content)[0]
                    else:
                        res.encoding = res.apparent_encoding

                soup = BeautifulSoup(res.text,'html.parser')
                title = 'none'
                if soup.title:
                    title = soup.title.string.strip()
                logging.info(title + ' ' + target)
                return target+'#s#'+title
        except Exception as e:
            logging.error(str(e))

    def _scan(self):
        while not self.sub_domain.empty():
            sub = self.sub_domain.get()
            subdomain = self._query(sub)
            if subdomain:
                self.result.append(subdomain)
            self.sub_domain.task_done()

    def _run(self):        
        self._load_queue()
        for i in range(self.threading):
            t = threading.Thread(target=self._scan())
            t.start()
            #t.join()#block master
        
        #work with queue.task_done()
        #block master untill queue is empty
        self.sub_domain.join()

        return list(set(self.result))

######################################

class Sub_domain(object):

    def __init__(self, domain, save_path):
        self.domain = domain
        self.mkdir_path = save_path

    def _out_file(self, file_path, filename, result):
        result_file = os.path.join(file_path, filename)
        with open(result_file, 'w') as f:
            f.write("\n".join(result))

    def _run(self):
        if not os.path.exists(self.mkdir_path):
            os.makedirs(self.mkdir_path)
        
        subdomain = []
        #AXFR
        logging.info("starting AXFR...")
        result = AXFR(self.domain)._get()
        logging.info("Finish AXFR, Total: {}".format(len(result)))
        subdomain += result

        #Dns_zone
        logging.info("starting Dns_zone...")
        result = Dns_zone(self.domain)._get()
        logging.info("Finish Dns_zone, Total: {}".format(len(result)))
        subdomain += result

        #findsubmains
        logging.info("starting findsubdomains...")
        result = Findsubdomains(self.domain)._get()
        logging.info("Finish findsubdomains, Total: {}".format(len(result)))
        subdomain += result

        #hackertarget
        logging.info("starting hacktarget...")
        result = Hackertarget(self.domain)._get()
        logging.info("Finish hackertarget, Total: {}".format(len(result)))
        subdomain += result

        #all
        result = [x.lstrip('*.') for x in subdomain]
        result = list(set(result))
        self._out_file(self.mkdir_path, 'all.txt', result)
        logging.info("Saving to result/all.txt, Total: {}".format(len(result)))
        
        #check-alive
        logging.info("starting check-alive...")
        result = Domain_check(result)._run()
        self._out_file(self.mkdir_path, 'alive.txt', result)
        logging.info("Saving to result/alive.txt, Total: {}".format(len(result)))
        

        #check-web
        logging.info("starting check-web...")
        result = Web_check(result)._run()
        self._out_file(self.mkdir_path, 'web.txt', result)
        logging.info("Saving to result/web.txt, Total: {}".format(len(result)))
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='子域名检测工具\n#利用现成的接口获取子域名\n#1、https://crt.sh/?q=%.aliyun.com&output=json\n#2、http://api.hackertarget.com/hostsearch/?q=aliyun.com\n#3、https://findsubdomains.com/subdomains-of/aliyun.com\n#4、dns zone transfer')
    parser.add_argument("-d", dest="domain",type=str, help="eg: alipay.com")

    args = parser.parse_args()
    domain = args.domain
    if not domain:
        parser.print_help()
        exit(1)

    file_abspath = os.path.dirname(os.path.abspath(__file__))
    mkdir_path = os.path.join(file_abspath, 'result/{0}'.format(domain))
    try:
        Sub_domain(args.domain, mkdir_path)._run()
    except Exception as e:
        logging.error(str(e))
        exit(1)
