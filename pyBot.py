# pyBot.py
#
# TODO: Try and split everything (replies, etc.) into separate files.

# include(s):

import socket


# Bot command(s):

def parse_bot_command(command, data):
    BOT_COMMANDS[command](data)

def parse_bot_debug(data):
    nick = data[0].split("!")[0][1:]
    sendRaw("{} {} :Hi {}, this is a debug line.{}".format(BOT_REPLYMETHOD, nick, nick, NEW_LINES))


# IRC command(s):

def parse_irc_command(command, data):
    IRC_COMMANDS[command](data)

def parse_irc_376(data):
    # `-> <server> 376 <nick> :End of /MOTD command.

    sendRaw("JOIN {}{}".format(BOT_CHAN, NEW_LINES))

def parse_irc_ping(data):
    # `-> PING [:]<arg>

    sendRaw("PONG {}{}".format(data.split(" ")[1], NEW_LINES))

def parse_irc_privmsg(data):
    # `-> <nick!user@host> PRIVMSG <target> :[message]

    line = data.split(" ")
    command = line[3][1:].lower()
    if line[2] != BOT_NICK:
        if command[0] != BOT_TRIGGER:
            return
        command = command[1:]
    if command not in BOT_COMMANDS:
        if line[2] == BOT_NICK:
            sendRaw("{} {} :{}{}".format(BOT_REPLYMETHOD, line[0].split("!")[0][1:], ERR_NOSUCHCOMMAND.format(command), NEW_LINES))
        return
    parse_bot_command(command, line)


# Function(s):

def sendRaw(input):
    pyBot.send(input.encode("UTF-8"))
    print(input.strip(NEW_LINES))


# define(s):

BOT_CHAN = "#localhost"
BOT_COMMANDS = {
    "debug": parse_bot_debug
}
BOT_NICK = "pyBot"
BOT_PORT = 6667
BOT_REALNAME = "{0}"
BOT_REPLYMETHOD = "NOTICE"
BOT_SERVER = "localhost"
BOT_TRIGGER = "!"

ERR_NOSUCHCOMMAND = "The command {0} does not exist."

IRC_COMMANDS = {
    "376": parse_irc_376,
    "PING": parse_irc_ping,
    "PRIVMSG": parse_irc_privmsg
}
NEW_LINES = "\r\n"

pyBot = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
pyBot.connect((BOT_SERVER, BOT_PORT))


# Core:

def main():
    sendRaw("NICK {}{}".format(BOT_NICK, NEW_LINES))
    sendRaw("USER {} 0 0 :{}{}".format(BOT_NICK, BOT_REALNAME.format(BOT_NICK), NEW_LINES))

    while 1:
            data = pyBot.recv(4096).decode("UTF-8")
            if not data:
                break
            print(data)
            # `-> No line stripping in this as I noticed on one server that they have an \r in the MOTD line(s).
            if len(data.strip(NEW_LINES)) == 0:
                return
            newData = data.split(NEW_LINES)
            for line in newData:
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
