#!/usr/bin/python3

import requests
import re


def isLoginSuccess(url, username, password):

    with requests.Session() as session:
        keyword = "id=\"token\""
        resPage = session.get(url)

        with open("./token_resPage.html", "w") as file:
            file.write(resPage.text)
        with open("./token_resPage.html", "r") as file:
            for line in file.readlines():
                if (keyword in line):
                    value = line.split(" ")[-2]
                    regex = re.search(r"\"([A-Za-z0-9_]+)\"", value) # Regex to extract token value between double quotes
                    assert regex != None
                    token = regex.group(1)
                    print("CSRF Token: " + token)
                    break

        payload = {
            'url': '', 
            'timezone': '1',
            'skin': 'unilim',
            'token': token,
            'user': username,
            'password': password
        }
        resLogIn = session.post(url, data=payload)
        cookies = resLogIn.request._cookies.get_dict()
        if not cookies:
            print("Login failed. Request rejected.")
            return False

        print("Cookies: " + cookies["lemonldap"])
        print("Login success. Request granted.")
        return True


