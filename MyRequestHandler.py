import pserver

#example for custom RequestHandler, in this case for handling db transactions
class MyRequestHandler(pserver.PServerRequestHandler):
	def preExec(self): #executed directly before the main execution
		print("Starting db transaction")
	def postExec(self): #executed directly after the main execution
		print("Committing db transaction")
