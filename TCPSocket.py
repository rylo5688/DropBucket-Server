from socket import *
from collections import defaultdict

class TCPSockets:
	MAX_BUFSIZ = 1024
	SERVER_PORT = 12000
	def __init__(self):
		self.__connections = defaultdict(list) # Map of userid to list of device socket connections

		self.serverSocket = socket(AF_INET,SOCK_STREAM)
		self.serverSocket.bind(('', self.SERVER_PORT))
		self.serverSocket.listen(1)

	def establishConnection(self):
		while True:
			connSocket, addr = self.serverSocket.accept()
			connInfo = connSocket.recv(self.MAX_BUFSIZ).decode()
			infoList = connInfo.split(",")

			# Expect format `userId,deviceId`
			if len(infoList) == 2:
				# Correct format so add this to the list of connections
				self.__connections[infoList[0]].append((infoList[1], connSocket, addr))

	def sendSyncRequests(self, userId, recentDeviceId, bucketInfo):
		def filterFun(deviceInfo):
			(dId, connSocket, addr) = deviceInfo
			try:
				if dId != recentDeviceId:
					# TODO: Send the file system status object
					connSocket.send("hello world")
				return True
			except:
				print("Socket closed....")
				return False

		self.__connections[userid] = filter(filterFun, self.__connections[userId])


