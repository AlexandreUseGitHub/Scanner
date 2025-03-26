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

def load_payloads(file_path):
    """Loads the list of payloads from a file."""
    try:
        with open(file_path, "r", encoding="utf8") as f:
            return [line.strip() for line in f]
    except FileNotFoundError:
        print(f"[E] The file {file_path} does not exist.")
        exit(1)

def generate_payload_in_params(url, payloads, separator):
    """Injects payloads into the URL parameters using the chosen separator."""
    parsed_url = urllib.parse.urlparse(url)
    
    # Split the URL based on the separator
    full_url = url.split(separator, 1)
    base_url = full_url[0]
    param_str = full_url[1] if len(full_url) > 1 else ""

    # Extract existing parameters
    params = urllib.parse.parse_qs(param_str)

    if not params:
        print(f"[W] No parameter found after '{separator}' in the URL.")
        return

    for param in params:
        print(f'[+] Testing {param} in separator "{separator}"')
        for payload in payloads:
            new_params = params.copy()
            new_params[param] = [payload]
            new_query = urllib.parse.urlencode(new_params, doseq=True)
            
            # Reconstruct the URL with the correct separator
            new_url = f"{base_url}{separator}{new_query}"
            scan(new_url)

def scan(url):
    """Displays the URL to be scanned (modify to send an actual HTTP request if needed)."""
    print(f"[!] Scanning: {url}")
    # response = requests.get(url)  # Disabled to avoid accidental requests
    # print(response.text)

def ask_if_missing(value, prompt):
    """Asks for a value if not provided."""
    return value or input(prompt).strip()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="XSS Parameter Fuzzer")
    parser.add_argument("-u", "--url", help="Target URL with at least one parameter")
    parser.add_argument("-w", "--wordlist", default='xss-payload-list.txt', help="File containing the list of XSS payloads")
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

    payload_list = load_payloads(payload_file)
    generate_payload_in_params(url, payload_list, separator)
