import sys
import time
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import threading
import traceback
import inspect

PSERVER_VERSION = "1.2.2"

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
		try:
			#decode request json
			req = {}
			if self.headers.get_all(name='content-length') != None:
				length = int(self.headers.get_all(name='content-length')[0])
				reqJson = str(self.rfile.read(length), 'utf-8')
				req = json.loads(reqJson)

			#find and execute method
			apiMethod = self.getApiMethod(self.path)
			result = self.executeApiMethod(apiMethod, req)
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

		if result['status'] == 'error':
			print(json.dumps(result, indent=4))
		print('{f} took {time}s to answer'.format(f = self.path, time = round(time.time()-starttime, 2)))

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

	def executeApiMethod(self, apiMethod, req):
		#check parameters
		#TODO only the existance of the params is checked here. we need to be able to define the complete data structure
		if list(req.keys()) != inspect.getargspec(apiMethod).args:
			raise PserverException('Problem with parameters: Expected {expected}, got {got}'
				.format(
					expected = inspect.getargspec(apiMethod).args,
					got = req.keys()
				)
			)

		result = apiMethod(**req)
		self.verifyResultFormat(result)
		return result

#Handle requests in a separate thread
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	pass

server = None
context = {}
def start():
	global server
	server = ThreadedHTTPServer(('', 8080), RequestHandler)
	t = threading.Thread(target=server.serve_forever)
	t.daemon = True
	t.start()
	print("Started PServer")

def stop():
	print("Stopping PServer...")
	server.shutdown()
	print("Stopped PServer")
