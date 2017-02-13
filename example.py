import time

import pserver #import the main server module
import api #import your api

#start the server asynchronously
pserver.start()

#set some global context for the RequestHandlers to use. The context can be changed at any time
pserver.setContext(dict(
	GLOBAL_VARIABLE = 42,
	db = "myDB"
))

while True:
	try:
		time.sleep(1)
	except KeyboardInterrupt:
		#stop the server
		pserver.stop()
		time.sleep(1)
		exit()
