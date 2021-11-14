#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Libraries
from pycurl import Curl, ENCODING, SSL_VERIFYPEER, SSL_VERIFYHOST, TIMEOUT, CUSTOMREQUEST, POSTFIELDS, URL, HTTPHEADER, RESPONSE_CODE
from threading import Thread, Lock, active_count
from random import choice, randint
from datetime import datetime
from requests import post
from colorama import init
from time import sleep
from json import loads

# Variables
CONFIG = loads(open("./data/config.json", "r").read())
SUCCESS = "[\x1b[32m+\x1b[39m]"
ERROR = "[\x1b[31m-\x1b[39m]"
INFO = "[\x1b[33m?\x1b[39m]"
lock = Lock()

class Base(object):
    def __init__(self):
        super(Base, self).__init__()
        self.attempts, self.rs, self.running = 0, 0, True

    def discordWebhook(self, username, attempts):
        try:
            post(CONFIG["discord"]["webhook"], headers={
                "Content-Type": "application/json",
                "Accept-Language": "en-US",
                "User-Agent": "Turbo/v1",
                "Accept": "*/*",
            }, json={
                "embeds": [{
                    "title": "Removal's WHI Turbo",
                    "url": "https://weheartit.com/{}/".format(username),
                    "description": "{}".format(choice(CONFIG["discord"]["descriptions"])),
                    "timestamp": datetime.utcnow().isoformat(),
                    "color": randint(1, 16777215),
                    "fields": [
                    {
                        "name": "Username",
                        "value": "{}".format(username),
                        "inline": True
                    },
                    {
                        "name": "Attempts",
                        "value": "{:,}".format(attempts),
                        "inline": True
                    }],
                    "thumbnail":
                    {
                        "url": "https://i.imgur.com/TM5qRUm.png"
                    },
                    "footer":
                    {
                    "text": "WHI",
                    "icon_url": "https://i.imgur.com/TM5qRUm.png"
                    }
                }]
            })
        except : return

class Turbo(Thread):
    def __init__(self, weheartit, target, session):
        super(Turbo, self).__init__()
        self.weheartit = weheartit
        self.session = session
        self.target = target

    def weheartitConnection(self):
        try:
            self.request = Curl()
            self.request.setopt(ENCODING, "gzip")
            self.request.setopt(SSL_VERIFYPEER, 0)
            self.request.setopt(SSL_VERIFYHOST, 0)
            self.request.setopt(TIMEOUT, 1)

            return self.request
        except : pass

    def weheartitRequest(self, url, data, headers):
        try:
            self.request.setopt(CUSTOMREQUEST, "PUT")
            self.request.setopt(POSTFIELDS, data)

            self.request.setopt(URL, url)
            self.request.setopt(HTTPHEADER, headers)
            self.request.perform_rs()

            return self.request.getinfo(RESPONSE_CODE)
        except :
            self.request.close()
            self.weheartitConnection()
            pass

    def run(self):
        sleep(0.1)
        self.weheartitConnection()

        while True:
            try:
                if self.weheartitRequest("https://api.weheartit.com/api/v2/user", data="{\"username\":\"%s\"}" % self.target, headers=["Connection: keep-alive", "Content-Type: application/json; charset=UTF-8", "Authorization: Bearer " + self.session]) == 200:
                    with lock:
                        self.weheartit.running = False

                        if self.weheartit.running == False:
                            print("{} Successfully claimed {} after {:,} attempts{}".format(SUCCESS, self.target, self.weheartit.attempts, " " * 10))

                            self.weheartit.discordWebhook(self.target, self.weheartit.attempts)
                else: self.weheartit.attempts += 1
            except : pass

class Rs(Thread):
    def __init__(self, weheartit):
        super(Rs, self).__init__()
        self.weheartit = weheartit

    def run(self):
        while True:
            before = self.weheartit.attempts
            sleep(1)
            self.weheartit.rs = self.weheartit.attempts - before

def getInput(prompt):
    print(prompt, end="")
    return input()

def main():
    init()

    try:
        print("{} Removal's WHI Turbo | Version 1.0\n".format(INFO))

        request = Base()
        threads = int(getInput("{} Threads: ".format(INFO)))
        target = str(getInput("{} Target: ".format(INFO)))
        session = str(getInput("{} Session: ".format(INFO)))

        getInput("\n{} Ready. Press ENTER to start!".format(INFO))
        print("\x1b[A{}\x1b[A".format(" " * 54))

        for _ in range(threads):
            turboThread = Turbo(request, target, session)
            turboThread.setDaemon(True)
            turboThread.start()

        rsThread = Rs(request)
        rsThread.setDaemon(True)
        rsThread.start()

        while request.running:
            try:
                print("{} Total Requests Sent: {:,} | {:,} R/S | Threads Active: {:,} {}".format(SUCCESS, request.attempts, request.rs, active_count(), " " * 10), end='\r', flush=True)
                sleep(.1)
            except KeyboardInterrupt:
                print("\n\n{} Turbo stopped, exiting after {:,} attempts {}".format(ERROR, request.attempts, "" * 40))
                request.running = False
                exit(0)

    except : pass

main()