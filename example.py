import pserver
import time
import sys
import api

pserver.start()

while True:
	try:
		time.sleep(1)
	except KeyboardInterrupt:
		pserver.stop()
		time.sleep(1)
		exit()
