# -*- coding: utf-8 -*-
"""
Created on Mon Mar 24 10:34:36 2025

@author: acarriou
"""


import bs4
import requests
import urllib.parse
import argparse
from sys import exit

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


from concurrent.futures import ThreadPoolExecutor
import threading

# Nombre de threads (et donc de navigateurs simultanés)
NUM_THREADS = 8
TIMEOUT = 1

NUMBEROFPAYLOADS = 0

def setup_selenium():
    """Configure Selenium avec Chrome Headless."""
    options = Options()
    options.add_argument("--headless")  # Mode sans interface graphique
    options.add_argument("--disable-gpu")
    options.add_argument("--log-level=3")  # Réduire les logs inutiles
    
    service = Service("/usr/bin/chromedriver")
    return webdriver.Chrome(service=service, options=options)


# Pool de WebDrivers (un par thread)
thread_local = threading.local()

def get_driver():
    """Retourne un WebDriver attaché au thread actuel."""
    if not hasattr(thread_local, "driver"):
        options = webdriver.ChromeOptions()
         # Mode sans interface graphique
        options.add_argument("--headless=new")  

        thread_local.driver = webdriver.Chrome(options=options)
    return thread_local.driver


def check_xss(url):
    """Vérifie si une alerte XSS apparaît sur une URL donnée."""
    global NUMBEROFPAYLOADS
    driver = get_driver()
    #print(f"[I] Testing {url}")
    try:
        NUMBEROFPAYLOADS += 1
        driver.get(url)


        try:


            alert = driver.switch_to.alert
            alert_text = alert.text
            alert.accept()

            if alert_text in ["1", "8"]: # Because the payloads trigger alert(1) or prompt(8)
                print(f"[+] XSS detected on : {url} !")
                return url
            
        except:
            
            print(f"[-] No XSS detected on : {url}")

    except Exception as e:
            pass
    

    return None  # If no XSS


def detect_xss(urls):
    """Lance la détection XSS sur une liste d'URLs en parallèle avec un pool de WebDrivers."""
    xss_vulnerable_urls = []

    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        results = list(executor.map(check_xss, urls))

    # Fermer les WebDrivers après exécution
    if hasattr(thread_local, "driver"):
        thread_local.driver.quit()

    # Filtrer les résultats pour garder les URLs vulnérables
    xss_vulnerable_urls = [url for url in results if url is not None]
    
    # Generate report
    if xss_vulnerable_urls:
        print("\n[!] XSS Found on:")
        for url in xss_vulnerable_urls:
            print(f"   -> {url}")
        print(NUMBEROFPAYLOADS)
        return True
    else:
        print("\n[-] No XSS found.")
        return False


def load_payloads(file_path):
    """Loads the list of payloads from a file."""
    try:
        with open(file_path, "r", encoding="utf8") as f:
            return [line.strip() for line in f]
    except FileNotFoundError:
        print(f"[E] The file {file_path} does not exist.")
        exit(1)

def generate_injected_urls(url, payloads, separator):
    """Injects payloads into the URL parameters using the chosen separator. Returning a list with the injected urls"""
    print(f'[I] Using separator : {separator}')
    parsed_url = urllib.parse.urlparse(url)
    
    # Split the URL based on the separator
    full_url = url.split(separator, 1)
    base_url = full_url[0]
    param_str = full_url[1] if len(full_url) > 1 else ""

    # Extract existing parameters
    params = urllib.parse.parse_qs(param_str)
    
    urls_injected = []
    
    if not params:
        print(f"[W] No parameter found after '{separator}' in the URL.")
        return

    for param in params:
        print(f'[I] Generating payload for  param : {param}')
        for payload in payloads:
            new_params = params.copy()
            new_params[param] = [payload]
            new_query = urllib.parse.urlencode(new_params, doseq=True)
            
            # Reconstruct the URL with the correct separator
            new_url = f"{base_url}{separator}{new_query}"
            urls_injected.append(new_url)
    return urls_injected

def scan(url):
    """Displays the URL to be scanned (modify to send an actual HTTP request if needed)."""
    pass
    # print(f"[!] Scanning: {url}")
    # response = requests.get(url)  # Disabled to avoid accidental requests
    # print(response.text)

def ask_if_missing(value, prompt):
    """Asks for a value if not provided."""
    return value or input(prompt).strip()

if __name__ == "__main__":
    # Arguments
    parser = argparse.ArgumentParser(description="XSS Parameter Fuzzer")
    parser.add_argument("-u", "--url", help="Target URL with at least one parameter")
    parser.add_argument("-w", "--wordlist", default='payloads/xss-payload-list.txt', help="File containing the list of XSS payloads")
    parser.add_argument("-s", "--separator", default="?", help="Separator between the URL and parameters (e.g.: ?, #, ;, &)")

    args = parser.parse_args()

    # If no argument is provided, ask for values interactively
    required_args = {"url": args.url}
    
    missing = [name for name, value in required_args.items() if not value]
    
    if missing:
        print(f"[W] Missing required args: {', '.join(missing)}")
        interactive = input("[?] Required argument(s) is/are missing, would you like to enter interactive mode? [Y/n]: ")
        if interactive.lower() == 'n':
            exit()

    url = ask_if_missing(args.url, "Enter the target URL: ")
    payload_file = ask_if_missing(args.wordlist, "Enter the payload file: ")
    separator = ask_if_missing(args.separator, "Enter the separator (default is ?): ") or "?"

    # Generating urls
    payload_list = load_payloads(payload_file)
    urls = generate_injected_urls(url, payload_list, separator)
    #print(urls)
    
    # Scanning
    scan(urls)
    detect_xss(urls)