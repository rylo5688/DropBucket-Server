import threading
from socket import *
from collections import defaultdict

class TCPSockets:
	MAX_BUFSIZ = 1024
	SERVER_PORT = 12000
	def __init__(self):
		self.__connections = defaultdict(list) # Map of userid to list of device socket connections
		self.__connLock = threading.Lock()

		self.serverSocket = socket(AF_INET,SOCK_STREAM)
		self.serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
		self.serverSocket.bind(('', self.SERVER_PORT))
		self.serverSocket.listen(1)

		listening = threading.Thread(target=self.establishConnection)
		listening.start()

	def establishConnection(self):
		while True:
			connSocket, addr = self.serverSocket.accept()
			print("GOT CONNECTION", flush=True)
			connInfo = connSocket.recv(self.MAX_BUFSIZ).decode()
			infoList = connInfo.split(",")

			# Expect format `userId,deviceId`
			if len(infoList) == 2:
				# Correct format so add this to the list of connections
				print(infoList, flush=True)
				self.__connLock.acquire(True, -1)
				self.__connections[infoList[0]].append((infoList[1], connSocket, addr))
				print(self.__connections, flush=True)
				self.__connLock.release()

	# TODO: This should be a thread function
	def sendSyncRequests(self, userId, recentDeviceId, bucketInfo):
		# Lock the Connections until we go through updating this list
		self.__connLock.acquire(True, -1)

		# Send sync requests to user devices
		connRemove = []
		for i, (dId, connSocket, addr) in enumerate(self.__connections[userId]):
			print("TEST: {},{},{}".format(dId, connSocket, addr, flush=True))
			try:
				if dId != recentDeviceId:
					# TODO: Send the file system status object
					print("hello world (UPDATE FROM: {}, SYNC REQUEST TO: {})".format(recentDeviceId, dId), flush=True)
					connSocket.send("hello world (UPDATE FROM: {}, SYNC REQUEST TO: {})".format(recentDeviceId, dId).encode())
			except:
				print("Socket closed.")
				connRemove.append(i)

		# Removing all socket connections that are closed
		for i in sorted(connRemove, reverse=True):
			del self.__connections[userId][i]

		self.__connLock.release()


# Testing
sockets = TCPSockets()
sentence = input('Input lowercase sentence:')
sockets.sendSyncRequests("user1", "1", "{}")



