import socket, sys, re, os
import threading
from time import sleep
from framedSocket import FramedSocket
sys.path.append("../lib")       # for params
import params

switchesVarDefaults = (
    (('-l', '--listenPort') ,'listenPort', 50001),
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )

progname = "server"
paramMap = params.parseParams(switchesVarDefaults)

listenPort = paramMap['listenPort']
listenAddr = ''       # Symbolic name meaning all available interfaces

if paramMap['usage']:
    params.usage()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((listenAddr, listenPort))
s.listen(1)              # allow only one outstanding request

#############################################

files = set()
mutex = threading.Lock()

def handleRequest(fs):
    msg = fs.recvMsg()
    fileName = msg.decode()
    print(msg)

    mutex.acquire()
    if fileName in files:
        fs.sendMsg("BAD")
        fs.socket.shutdown(socket.SHUT_WR)
        mutex.release()
        return

    fs.sendMsg("OK")
    files.add(fileName)
    mutex.release()

    sleep(5)
    
    try:
        fd = os.open(msg, os.O_CREAT | os.O_WRONLY)
        while True:
            msg = fs.recvMsg()
            if len(msg) == 0:
                break
            os.write(fd, msg)
        os.close(fd)
    except socket.timeout:
        pass
    except:
        fs.sendMsg("BAD")
        os.close(fd)
        
    files.remove(fileName)
    print("Finished writing:" + fileName)
    fs.sendMsg("DONE")
    fs.socket.close()

while True:
    conn, addr = s.accept() # wait until incoming connection request (and accept it)
    print('Connected by', addr)
    conn.settimeout(5)

    fs = FramedSocket(conn)
    threading._start_new_thread(handleRequest, (fs,))

