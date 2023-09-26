from define import *

import re

FILE_CONF = "pyBot.conf"

with open(FILE_CONF, mode="r", encoding="UTF-8") as conf:
    for line in conf:
        item = line.split("=", 1)
        if len(item) < 2:
            continue
        data = re.split(REGEX_NEWLINE, item[1])
        if item[0] == "BOT_CHAN":
            BOT_CHAN = data[0]
            continue
        if item[0] == "BOT_NICK":
            BOT_NICK = data[0]
            continue
        if item[0] == "BOT_PASS":
            BOT_PASS = data[0]
            continue
        if item[0] == "BOT_PORT":
            BOT_PORT = data[0]
            continue
        if item[0] == "BOT_REALNAME":
            BOT_REALNAME = data[0]
            continue
        if item[0] == "BOT_REPLYMETHOD":
            BOT_REPLYMETHOD = data[0]
            continue
        if item[0] == "BOT_SERVER":
            BOT_SERVER = data[0]
            continue
        if item[0] == "BOT_TRIGGER":
            BOT_TRIGGER = data[0]
            continue

# EOF
