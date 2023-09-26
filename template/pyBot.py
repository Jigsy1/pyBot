# pyBot.py (template)


# include(s):

from config import *
from define import *
from replies import *
# `-> Our own.
import os
import re
import socket
import sqlite3


# Bot command(s):

def bot_command_do(data):
    # DO [#chan] <text>

    nick = get_nick(data[0])
    if is_array(data, 4) == False:
        send_message(nick, ERR_NEEDMOREARGS)
        return
    if is_channel(data[4]) == False:
        if is_channel(data[2]) == False:
            send_message(nick, ERR_NEEDATARGET)
            return
        channel = data[2]
        string = " ".join(data[4:])
    if is_array(data, 5) == False and "channel" not in locals():
        send_message(nick, ERR_NEEDMOREARGS)
        return
    if "channel" not in locals():
        channel = data[4]
        string = " ".join(data[5:])
    send_raw("PRIVMSG {} :\001ACTION {}\001{}".format(channel, string, NEWLINE))

def bot_command_say(data):
    # SAY [#chan] <text>

    nick = get_nick(data[0])
    if is_array(data, 4) == False:
        send_message(nick, ERR_NEEDMOREARGS)
        return
    if is_channel(data[4]) == False:
        if is_channel(data[2]) == False:
            send_message(nick, ERR_NEEDATARGET)
            return
        channel = data[2]
        string = " ".join(data[4:])
    if is_array(data, 5) == False and "channel" not in locals():
        send_message(nick, ERR_NEEDMOREARGS)
        return
    if "channel" not in locals():
        channel = data[4]
        string = " ".join(data[5:])
    send_raw("PRIVMSG {} :{}{}".format(channel, string, NEWLINE))


# IRC command(s):

def parse_irc_command(command, data):
    IRC_COMMANDS[command](data)

def parse_raw_376(data):
    # :<server> 376 <nick> :End of /MOTD command.

    if "BOT_CHAN" in globals() and is_channel(BOT_CHAN) == True:
        send_raw("JOIN {}{}".format(BOT_CHAN, NEWLINE))
        # `-> Half-assed hack of joining our defined channel.

def parse_irc_ping(data):
    # PING [:]<arg>

    send_raw("PONG {}{}".format(data.split(" ")[1], NEWLINE))

def parse_irc_privmsg(data):
    # :<nick!user@host> PRIVMSG <target> :[message]

    line = data.split(" ")
    nick = get_nick(line[0])
    command = line[3][1:]
    if command == "" or command == " ":
        return
    if line[2] != BOT_NICK:
        if command[0] != BOT_TRIGGER:
            return
        command = command[1:]
    with sqlite3.connect(BOT_DB) as dbConnection:
        dbCursor = dbConnection.cursor()
        dbSearch = "SELECT * FROM COMMANDS WHERE COMMAND = ? COLLATE NOCASE"
        dbCursor.execute(dbSearch, (command,))
        dbResult = dbCursor.fetchone()
        # ID | COMMAND | FUNCTION
        if dbResult == None:
            if line[2] == BOT_NICK:
                send_message(nick, ERR_NOSUCHCOMMAND.format(command))
                return
            dbConnection.close
            return
        dbConnection.close
    thisCommand = dbResult[2]
    globals()[thisCommand](line)

# Function(s):

def get_nick(fulladdress):
    # :<nick!user@host>

    return fulladdress.split("!")[0][1:]

def is_array(array, index):
    try:
        array[index]
    except IndexError:
        return False
    return True

def is_channel(channel):
    if channel[0] == "#":
        return True
    return False

def send_raw(data):
    pyBot.send(data.encode("UTF-8"))
    print(" ".join(re.split(REGEX_NEWLINE, data)))

def send_message(nick, string):
    send_raw("{} {} :{}{}".format(BOT_REPLYMETHOD, nick, string, NEWLINE))


# define(s):

BOT_DB = "{}{}".format(os.path.dirname(__file__),"/pyBot.db")

IRC_COMMANDS = {
    "376": parse_raw_376,
    "PING": parse_irc_ping,
    "PRIVMSG": parse_irc_privmsg
}

pyBot = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
pyBot.connect((BOT_SERVER, int(BOT_PORT)))

# Core:

def main():
    if "BOT_PASS" in globals():
        send_raw("PASS :{}{}".format(BOT_PASS, NEWLINE))
    send_raw("NICK {}{}".format(BOT_NICK, NEWLINE))
    send_raw("USER {} 0 0 :{}{}".format(BOT_NICK, BOT_REALNAME.format(BOT_NICK), NEWLINE))
    while True:
        data = pyBot.recv(BOT_BUFFER).decode("UTF-8")
        if not data:
            break
        print(data)
        dataSplit = re.split(REGEX_NEWLINE, data)
        if len(dataSplit) == 1 and dataSplit[0] == "":
            return
        for line in dataSplit:
            newLine = line.split(" ")
            if len(newLine) > 1:
                if newLine[1] in IRC_COMMANDS:
                    parse_irc_command(newLine[1], line)
            if newLine[0] in IRC_COMMANDS:
                parse_irc_command(newLine[0], line)
    pyBot.close()
    print("pyBot closed.\n")

if __name__ == "__main__":
    main()


# EOF
