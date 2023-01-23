# pyBot.py

# include(s):

import socket


# define(s):

BOT_CHAN = "#localhost"
BOT_NICK = "pyBot"
BOT_PORT = 6667
BOT_REALNAME = "%s" % (BOT_NICK)
BOT_SERVER = "localhost"
NEW_LINES = "\r\n"

pyBot = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
pyBot.connect((BOT_SERVER, BOT_PORT))


# Function(s):

def sendRaw(input):
    pyBot.send(input.encode("UTF-8"))
    print(input.strip(NEW_LINES))


# Core:

def main():
    sendRaw("NICK {}{}".format(BOT_NICK, NEW_LINES))
    sendRaw("USER {} 0 0 :{}{}".format(BOT_NICK, BOT_REALNAME, NEW_LINES))

    while 1:
            data = pyBot.recv(4096).decode("UTF-8")
            print(data)
            # `-> No line stripping in this as I noticed on one server that they have an \r in the MOTD line(s).
            data = data.split(NEW_LINES)
            for line in data:
                newLine = line.split(" ")
                if len(newLine) > 1:
                    if newLine[1] == "376":
                        sendRaw("JOIN {}{}".format(BOT_CHAN, NEW_LINES))
                if newLine[0] == "PING":
                    sendRaw("PONG {}{}".format(newLine[1], NEW_LINES))

if __name__ == "__main__":
    main()


# EOF
