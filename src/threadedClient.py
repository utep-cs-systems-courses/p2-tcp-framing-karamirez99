#! /usr/bin/env python3
# Echo client program
import socket, sys, re, time
import os
from framedSocket import FramedSocket
from myIO import writeLine, readLine
sys.path.append("../lib")       # for params
import params

switchesVarDefaults = (
    (('-s', '--server'), 'server', "127.0.0.1:50001"),
    (('-d', '--delay'), 'delay', "0"),
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    (('-i', '--input'), "input", "testIn.txt"),
    (('-o', '--output'), "output", "testOut.txt"),
    )
progname = "Client"
paramMap = params.parseParams(switchesVarDefaults)

server, usage  = paramMap["server"], paramMap["usage"]

if usage:
    params.usage()

try:
    serverHost, serverPort = re.split(":", server)
    serverPort = int(serverPort)
except:
    print("Can't parse server:port from '%s'" % server)
    sys.exit(1)

#connect to socket
s = None
for res in socket.getaddrinfo(serverHost, serverPort, socket.AF_UNSPEC, socket.SOCK_STREAM):
    af, socktype, proto, canonname, sa = res
    try:
        print("creating sock: af=%d, type=%d, proto=%d" % (af, socktype, proto))
        s = socket.socket(af, socktype, proto)
    except socket.error as msg:
        print(" error: %s" % msg)
        s = None
        continue
    try:
        print(" attempting to connect to %s" % repr(sa))
        s.connect(sa)
    except socket.error as msg:
        print(" error: %s" % msg)
        s.close()
        s = None
        continue
    break

if s is None:
    print('could not open socket')
    sys.exit(1)

#delay if requested
delay = float(paramMap['delay'])
if delay != 0:
    print(f"sleeping for {delay}s")
    time.sleep(delay)
    print("done sleeping")


s.settimeout(5)
#Attempt to send file given by input to output
fs = FramedSocket(s)
while 1:
    fs.sendMsg(paramMap["output"])
    data = fs.recvMsg()

    if len(data) == 0:
        break

    if not "OK" in data.decode():
        print("Couldnt do that. Heres the response")
        print(data.decode())
        break

    print(data.decode())

    try:
        fdIn = os.open(paramMap["input"], os.O_RDONLY)
        os.close(0)
        os.dup(fdIn)
        os.close(fdIn)

        while(True):
            line = readLine(True)
            if len(line) == 0:
                break
            fs.sendMsg(line)

        while(data.decode() != "DONE" or data.decode() != "BAD"):
            data = fs.recvMsg()

    except FileNotFoundError:
        print("{} could not be found".format(paramMap["input"]))
    except socket.timeout:
        pass

    break

print("Closing")
s.close()
