# pyBot.py


# include(s):

import re
import socket


# Bot command(s):

def parse_bot_command(command, data):
    BOT_COMMANDS[command](data)

def parse_bot_do(data):
    # DO [#chan] <text>

    nick = getNick(data[0])
    if is_array(data, 4) == False:
        sendString(nick, ERR_NEEDMOREARGS)
        return
    if is_channel(data[4]) == False:
        if is_channel(data[2]) == False:
            sendString(nick, ERR_NEEDATARGET)
            return
        thisChannel = data[2]
        thisString = " ".join(data[4:])
    if is_array(data, 5) == False and "thisChannel" not in locals():
        sendString(nick, ERR_NEEDMOREARGS)
        return
    if "thisChannel" not in locals():
        thisChannel = data[4]
        thisString = " ".join(data[5:])
    sendRaw("PRIVMSG {} :\001ACTION {}\001{}".format(thisChannel, thisString, NEWLINE))

def parse_bot_say(data):
    # SAY [#chan] <text>

    nick = getNick(data[0])
    if is_array(data, 4) == False:
        sendString(nick, ERR_NEEDMOREARGS)
        return
    if is_channel(data[4]) == False:
        if is_channel(data[2]) == False:
            sendString(nick, ERR_NEEDATARGET)
            return
        thisChannel = data[2]
        thisString = " ".join(data[4:])
    if is_array(data, 5) == False and "thisChannel" not in locals():
        sendString(nick, ERR_NEEDMOREARGS)
        return
    if "thisChannel" not in locals():
        thisChannel = data[4]
        thisString = " ".join(data[5:])
    sendRaw("PRIVMSG {} :{}{}".format(thisChannel, thisString, NEWLINE))


# IRC command(s):

def parse_irc_command(command, data):
    IRC_COMMANDS[command](data)

def parse_raw_376(data):
    # :<server> 376 <nick> :End of /MOTD command.

    sendRaw("JOIN {}{}".format(BOT_CHAN, NEWLINE))

def parse_irc_ping(data):
    # PING [:]<arg>

    sendRaw("PONG {}{}".format(data.split(" ")[1], NEWLINE))

def parse_irc_privmsg(data):
    # :<nick!user@host> PRIVMSG <target> :[message]

    line = data.split(" ")
    nick = getNick(line[0])
    if is_array(line, 3) == True:
        # `-> I found out on one IRCd (*cough* mIRCd :P) that if nothing is sent after the <target> (which is actually a bug), the bot will crash.
        command = line[3][1:].lower()
    if line[2] != BOT_NICK:
        if command[0] != BOT_TRIGGER:
            return
        command = command[1:]
    if command not in BOT_COMMANDS:
        if line[2] == BOT_NICK:
            sendString(nick, ERR_NOSUCHCOMMAND.format(command))
        return
    parse_bot_command(command, line)

# Function(s):

def getNick(fulladdress):
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

def sendRaw(data):
    pyBot.send(data.encode("UTF-8"))
    print(" ".join(re.split(NEWLINE_REGEX, data)))

def sendString(nick, string):
    sendRaw("{} {} :{}{}".format(BOT_REPLYMETHOD, nick, string, NEWLINE))


# define(s):

BOT_CHAN = "#localhost"
BOT_COMMANDS = {
    "do": parse_bot_do,
    "say": parse_bot_say
}
BOT_NICK = "pyBot"
BOT_PORT = 6667
BOT_REALNAME = "{0}"
BOT_REPLYMETHOD = "NOTICE"
BOT_SERVER = "localhost"
BOT_TRIGGER = "!"

ERR_NEEDATARGET = "Please specify a channel to use this command."
ERR_NEEDMOREARGS = "Insufficient parameters."
ERR_NOSUCHCOMMAND = "The command [{0}] does not exist."

IRC_COMMANDS = {
    "376": parse_raw_376,
    "PING": parse_irc_ping,
    "PRIVMSG": parse_irc_privmsg
}
NEWLINE = "\r\n"
# `-> Send in this order.

NEWLINE_REGEX = r"[\n\r]+"
# `-> For splitting.

pyBot = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
pyBot.connect((BOT_SERVER, BOT_PORT))


# Core:

def main():
    sendRaw("NICK {}{}".format(BOT_NICK, NEWLINE))
    sendRaw("USER {} 0 0 :{}{}".format(BOT_NICK, BOT_REALNAME.format(BOT_NICK), NEWLINE))

    while 1:
            data = pyBot.recv(4096).decode("UTF-8")
            if not data:
                break
            print(data)
            # `-> No line stripping in this as I noticed on one server that they have an \r in the MOTD line(s).
            splitData = re.split(NEWLINE_REGEX, data)
            if len(splitData) == 1 and splitData[0] == "":
                return
            for line in splitData:
                newLine = line.split(" ")
                if len(newLine) > 1:
                    if newLine[1] in IRC_COMMANDS:
                        parse_irc_command(newLine[1], line)
                if newLine[0] in IRC_COMMANDS:
                    parse_irc_command(newLine[0], line)
    pyBot.close()
    print("Socket closed.\n")

if __name__ == "__main__":
    main()


# EOF
