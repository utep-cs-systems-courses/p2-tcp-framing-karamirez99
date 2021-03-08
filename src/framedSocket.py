import socket

class FramedSocket:
    def __init__(self, socket):
        self.socket = socket
        self.buffer = ""

    #Messages given will be separated with '\r\n'
    def sendMsg(self, msg):
        if  msg == "":
            return

        msg += "\r\n"
        byteMsg = msg.encode()
        
        while len(byteMsg) > 0:
            bytesSent = self.socket.send(byteMsg)
            byteMsg = byteMsg[bytesSent:]


    #Returns a full message as separated with '\r\n'
    def recvMsg(self):
        currMessage = ""

        while(True):

            if len(self.buffer) == 0:
                self.buffer = self.socket.recv(1024).decode()
                if len(self.buffer) == 0:
                    return currMessage

            if '\r\n' in self.buffer:
                currMessage += self.buffer[0:self.buffer.index('\r\n')]
                self.buffer = self.buffer[self.buffer.index('\r\n') + 2:]
                return currMessage
            else:
                currMessage += self.buffer
                self.buffer = ""
        
