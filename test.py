import socket
import time

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("127.0.0.1", 65432))
print("Conn to query port successful")
portInfo = sock.recv(1024)
portAvailable = portInfo.split(b',')[1]
print("Port available is", portAvailable)
sock.sendall(b"200")
sock.close()
#Open a new socket, which is directed towards the table ports
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("127.0.0.1", int(portAvailable)))
while True:
	time.sleep(1)
	sock.sendall(b"Test constant recv")
