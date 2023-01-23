# pyBot.py

# include(s):

import socket


# IRC command(s):

def parse_irc_command(command, data):
    IRC_COMMANDS[command](data)

def parse_irc_376(data):
    # `-> <server> 376 <nick> :End of /MOTD command.

    sendRaw("JOIN {}{}".format(BOT_CHAN, NEW_LINES))

def parse_irc_ping(data):
    # `-> PING [:]<arg>

    data = data.split(" ")
    sendRaw("PONG {}{}".format(data[1], NEW_LINES))


# Function(s):

def sendRaw(input):
    pyBot.send(input.encode("UTF-8"))
    print(input.strip(NEW_LINES))


# define(s):

BOT_CHAN = "#localhost"
BOT_NICK = "pyBot"
BOT_PORT = 6667
BOT_REALNAME = "%s" % (BOT_NICK)
BOT_SERVER = "localhost"
IRC_COMMANDS = {
    '376': parse_irc_376,
    'PING': parse_irc_ping
}
NEW_LINES = "\r\n"

pyBot = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
pyBot.connect((BOT_SERVER, BOT_PORT))


# Core:

def main():
    sendRaw("NICK {}{}".format(BOT_NICK, NEW_LINES))
    sendRaw("USER {} 0 0 :{}{}".format(BOT_NICK, BOT_REALNAME, NEW_LINES))

    while 1:
            data = pyBot.recv(4096).decode("UTF-8")
            if not data:
                break
            print(data)
            # `-> No line stripping in this as I noticed on one server that they have an \r in the MOTD line(s).
            newData = data.split(NEW_LINES)
            if len(data.strip(NEW_LINES)) == 0:
                return
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
