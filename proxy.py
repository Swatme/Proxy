"""
A simple scraper proxy rotator

TODO: Docs later

@author: Mingjian Lu
@email: mingjian.lu@berkeley.edu
"""

import requests
from random import randint

class proxy_manager(object):
    # This class is for proxy management

    def __init__(self, proxy_file = './proxy_list.txt', switch_limit = 1000):
        with open(proxy_file) as f:
            self.proxy_list = f.readlines()
        self.proxy_list = map(lambda s: s.strip(), self.proxy_list)
        self.counter = switch_limit
        self.switch_limit = switch_limit
        self.proxy = None

    # Thanks http://codereview.stackexchange.com/questions/107087/multithreaded-web-scraper-with-proxy-and-user-agent-switching
    def check_proxy_and_clean_list(self, proxy_list_index):
        try:
            proxies = {'http': ("http://" + self.proxy_list[proxy_list_index])}
            response = requests.get('http://canihazip.com/s', proxies = proxies)
            returned_ip = response.text
            if returned_ip != self.proxy_list[proxy_list_index].split(":")[0]:
                self.proxy_list.pop(proxy_list_index)
                if len(self.proxy_list) == 0:
                    raise Exception("No more proxies available to be used")
                return False
            else:
                return True
        except:
            self.proxy_list.pop(proxy_list_index)
            if len(self.proxy_list) == 0:
                raise Exception("No more proxies available to be used")
            return False

    def random_proxy_index(self):
        return randint(0,len(self.proxy_list))

    def get_valid_proxy(self):
        if self.counter >= self.switch_limit:
            self.counter = 0
            while True:
                new_proxy_index = self.random_proxy_index()
                print("Trying " + str(self.proxy_list[new_proxy_index]))
                if self.check_proxy_and_clean_list(new_proxy_index):
                    self.proxy = {'http': 'http://' + self.proxy_list[new_proxy_index]}
                    return
                else:
                    print("Failed in validation!")
                    continue
        else:
            self.counter += 1
            return

    def proxy_get(self, url):
        self.get_valid_proxy()
        while True:
            try:
                response = requests.get(url, proxies = self.proxy)
            except:
                print("Failed because get banned by website!")
                self.counter = self.switch_limit
                self.get_valid_proxy()
                continue
            else:
                return response
