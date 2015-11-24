#!/usr/bin/python

import socket
import struct
import array

class UdpSocket(object):
	def __init__(self, recv_addr, receiving = False):
		self.addr = recv_addr
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		if (receiving): self.sock.bind(self.addr)
	def __del__(self):
		self.sock.close()
	
	def send(self, data):
		cksum = ~reduce(lambda x,y: x+y, data) & 0xFF
		packet = bytearray(data) + bytearray([cksum])
		sent = self.sock.sendto(packet, self.addr)
		while sent < len(packet):
			assert sent > 0, "Network unavailable"
			packet = packet[sent-1:]
			sent = self.sock.sendto(packet, self.addr)
	
	def recv(self, length):
		# Could do validation on same address, but that's probably overkill here
		remaining = length + 1
		packet = []
		while remaining > 0:
			buf, address = self.sock.recvfrom(remaining)
			assert len(buf) > 0, "Network unavailable"
			remaining -= len(buf)
			packet.extend(buf)
		
		packet = array.array('B', ''.join(packet))
		data = packet[:-1]
		cksum = packet[-1]
		if (cksum + reduce(lambda x,y: x+y, data) & 0xFF) != 0xFF:
			return None # Corrupted data
		return data	

RECV_ADDR = ('192.168.179.128', 9000)
#RECV_ADDR = ('localhost', 9000)
STRUCT_FMT = '<dd?'
EXPECTED_LENGTH = struct.calcsize(STRUCT_FMT)

if __name__ == "__main__":
	from sys import argv
	from time import sleep
	
	if (len(argv) > 1) and (argv[1].lower() == 'recv'):
		s = UdpSocket(RECV_ADDR, True)
		while True:
			data = s.recv(EXPECTED_LENGTH)
			if data == None: print "Corructed packet!"
			else:
				x, y, onscreen = struct.unpack(STRUCT_FMT, data)
				print ("Onscreen @", x, y) if onscreen else "Offscreen"
			sleep(0.1)
	else:
		from random import random
		s = UdpSocket(RECV_ADDR)
		while True:
			x = random() * 2.0 - 1.0
			y = random() * 2.0 - 1.0
			onscreen = random() < 0.5
			s.send(bytearray(struct.pack(STRUCT_FMT, x, y, onscreen)))
