import threading
import json
from socket import *
from collections import defaultdict

class TCPSockets:

	class __TCPSockets:
		MAX_BUFSIZ = 1024
		SERVER_PORT = 12000
		def __init__(self):
			"""
			Initializes TCP socket connection and start a thread to accept incoming connections
			These new connections are added to a private connections attribute (shared memory)
			"""
			self.__connections = defaultdict(list) # Map of userid to list of device socket connections
			self.__connLock = threading.Lock()

			self.serverSocket = socket(AF_INET,SOCK_STREAM)
			self.serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
			self.serverSocket.bind(('', self.SERVER_PORT))
			self.serverSocket.listen(1)

			listening = threading.Thread(target=self.establishConnection)
			listening.start()

		def establishConnection(self):
			"""
			Thread function. This is an infinite loop to accept incoming socket connections.
			All new connections are added to a shared dictionary of user to socket connection
			mappings.

			TODO: Some bug here with the thread not dieing for the hot reloading... Is it possible to have zombie threads lmao
			"""
			while True:
				connSocket, addr = self.serverSocket.accept()
				connInfo = connSocket.recv(self.MAX_BUFSIZ).decode()
				infoList = connInfo.split(",")

				# Expect format `userId,deviceId`
				if len(infoList) == 2:
					# Correct format so add this to the list of connections
					self.__connLock.acquire(True, -1)
					self.__connections[infoList[0]].append((infoList[1], connSocket, addr))
					self.__connLock.release()

		# TODO: This should be a thread function
		def sendSyncRequests(self, userId, recentDeviceId, bucketInfo):
			"""
			Thread function. Sends a sync request to all connected devices for a user.
			However, the one device that sent the request to cause a need for a sync
			will not be a sent a sync message.

			Args:
				userId: string
				recentDeviceId: string
				bucketInfo: string, JSON string of the current file system state
			"""

			# Lock the Connections until we go through updating this list
			self.__connLock.acquire(True, -1)

			# Send sync requests to user devices
			connRemove = []
			for i, (dId, connSocket, addr) in enumerate(self.__connections[userId]):
				try:
					if dId != recentDeviceId:
						# TODO: Send the file system status object
						payload = json.dumps(bucketInfo, separators=(",",":"))
						connSocket.send(payload)
				except:
					# Socket has closed
					connRemove.append(i)

			# Removing all socket connections that are closed
			for i in sorted(connRemove, reverse=True):
				del self.__connections[userId][i]

			self.__connLock.release()

	__instance = __TCPSockets() # Eager instantiation

	def __new__(cls):
		"""
		Singleton pattern
		NOTE: This is the eager version
		"""
		if not cls.__instance:
			cls.__instance = TCPSockets.__TCPSockets()
		return TCPSockets.__instance

	def __getattr__(self, name):
		"""
		Allows to to act like we are just calling TCPSockets.function when we are actually calling
		TCPSockets.instance.function
		"""
		return getattr(self.instance, name)