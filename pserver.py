import sys
import os
import time
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import threading
import traceback
import inspect
import requests
import api

PSERVER_VERSION = "1.1.1"

class PserverException(Exception):
	pass

class RequestHandler(BaseHTTPRequestHandler):
	#disable logging of every incoming request. only log errors
	def log_request(self, code='-', size='-'):
		pass

	def do_HEAD(self):
		self.send_response(200)
		self.send_header("Content-type", "application/json")
		self.end_headers()

	def do_GET(self):
		self.send_response(404)
		self.send_header("Content-type", "text/html")
		self.end_headers()

		print('GET request ignored.')

		self.wfile.write(bytes('POST only', 'utf-8'))

	def do_POST(self):
		starttime = time.time()
		postfiles = []
		try:
			#decode request json
			req = {}
			if self.headers.get_all(name='content-length') != None:
				length = int(self.headers.get_all(name='content-length')[0])
				reqJson = str(self.rfile.read(length), 'utf-8')
				req = json.loads(reqJson)

			#find method
			apiMethod = self.getApiMethod(self.path)
			print(inspect.signature(apiMethod))
			if list(req.keys()) != inspect.getargspec(apiMethod).args:
				raise PserverException('Problem with parameters: Expected {expected}, got {got}'
					.format(
						expected = inspect.getargspec(apiMethod).args,
						got = req.keys()
					)
				)

			#execute method
			result = apiMethod(**req)

			#process response
			self.verifyResultFormat(result)
		except ValueError as e:
			raise PserverException("Request is not valid Json: " + reqJson)
		except PserverException as e:
			result = {
				'status':'error',
				'result': str(e)
			}
		except Exception as e:
			result = {
				'status':'error',
				'result':'Processing exception: ' + traceback.format_exc()
			}
		finally:
			for f in postfiles:
				os.remove(f['path'])

		if result['status'] == 'error':
			print(json.dumps(result, indent=4))
		print("done. processing time " + str(round(time.time()-starttime, 2)) + "s")

		#return result
		self.send_response(200)
		self.send_header("Content-type", "application/json")
		self.end_headers()
		self.wfile.write(bytes(json.dumps(result, indent=4), 'utf-8'))

	def getApiMethod(self, path):
		if path == '':
			print("Aborted handling request because no command was given. ")
			raise PserverException('You need to specify a command')
		if path.startswith('/'): path = path[1:]

		pathParts = path.split('/')
		apiModuleName = 'api.' + '.'.join(pathParts[:-1])
		apiMethodName = pathParts[-1]

		try:
			apiModule = sys.modules[apiModuleName]
			return getattr(apiModule, apiMethodName)
		except (KeyError, AttributeError) as e:
			print("Unknown or invalid command supplied: " + path)
			raise PserverException('Unknown or invalid command')
		print("Handling command: " + apiMethodName + " in module " + apiModuleName)

	def verifyResultFormat(self, result):
		if not (isinstance(result, dict) and 'status' in result and 'result' in result):
			raise PserverException('Bad result format: ' + str(result))

#Handle requests in a separate thread
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	pass

server = ThreadedHTTPServer(('', 8080), RequestHandler)
def start():
	print("Started PServer. ")
	t = threading.Thread(target=server.serve_forever)
	t.daemon = True
	t.start()

def stop():
	server.shutdown()

if __name__ == '__main__':
	start()
	while True:
		time.sleep(1)
