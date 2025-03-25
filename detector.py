# -*- coding: utf-8 -*-
"""
Created on Mon Mar 24 10:34:36 2025

@author: acarriou
"""


import requests
import bs4

URL="https://vulnerable.com/search.php?search=test&date=somedate"
PAYLOAD_FILE = "xss-payload-list.txt"

payload_list = []

f = open(PAYLOAD_FILE, "r",encoding='utf8')
for payload in f:
    payload_list.append(payload)


def generate_payload_in_params(url,payloads):
    params=URL.split('?')[1].split('&')
    for param in params:
        print(f'[+] Testing GET param : {param.split("=")[0]}')
        for payload in payloads:
            new_param = "".join(param.split('=')[0])+'='+payload
            url = URL.replace(param,new_param)
            scan(url)
    
def scan(url):
    pass


generate_payload_in_params(URL,payload_list)