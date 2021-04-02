import socket

class FramedSocket:
    def __init__(self, socket):
        self.socket = socket
        self.buffer = ""
        self.numBytes = 0

    #Messages given will be separated with content length
    def sendMsg(self, msg):
        if  msg == "":
            return

        msg = "Length:" + str(len(msg)) + ":" + msg
        byteMsg = msg.encode()
        
        while len(byteMsg) > 0:
            bytesSent = self.socket.send(byteMsg)
            byteMsg = byteMsg[bytesSent:]


    #Returns a full message as indicated by content length
    def recvMsg(self):
        currMessage = b""

        while True:

            if len(self.buffer) == 0:
                self.buffer = self.socket.recv(1024)
                    
            if len(self.buffer) == 0:
                return currMessage

            if self.numBytes != 0 and len(self.buffer) >= self.numBytes:
                currMessage += self.buffer[:self.numBytes]
                self.buffer = self.buffer[self.numBytes:]
                self.numBytes = 0
                return currMessage

            elif self.numBytes != 0:
                currMessage += self.buffer
                self.numBytes -= len(self.buffer)
                self.buffer = b""

            else:
                currMessage += self.buffer
                getLength = currMessage.decode()

                if "Length:" in getLength:
                    getLengthSize = getLength[getLength.index("Length:") + 7:]
                    if ":" in getLengthSize:
                        numBytes = getLengthSize[:getLengthSize.index(":")]
                        self.numBytes = int(numBytes)
                        self.buffer = currMessage[len(getLength[:getLength.index(":", 7) + 1].encode()):]
                        currMessage = b""
                    else:
                        self.buffer = b""
                else:
                    self.buffer = b""
        
