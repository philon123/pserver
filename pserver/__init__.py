import sys
import os
import time
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import threading
import traceback
import inspect

VERSION = "1.4.5"

class PserverException(Exception):
	pass

def to_json(python_object): # serialize bytes objects
	if isinstance(python_object, bytes): return python_object.decode('utf-8')
	raise TypeError(repr(python_object) + ' is not JSON serializable')

class RequestHandler(BaseHTTPRequestHandler):
	# disable logging of every incoming request. only log errors
	def log_request(self, code='-', size='-'):
		pass

	def do_HEAD(self):
		self.send_response(200)
		self.send_header("Content-type", "application/json")
		self.end_headers()

	def do_GET(self):
		# check file exists and is allowed to access
		try:
			targetPath = self.checkAccess(self.path)
		except Exception as e:
			self.send_response(404)
			self.send_header("Content-type", 'text/html')
			self.end_headers()
			self.wfile.write('File not found'.encode('utf-8'))
			return

		# guess correct content type and send file
		f,extension = os.path.splitext(targetPath)
		contentType = 'text/css' if extension == '.css' else 'text/html'

		# send response
		self.send_response(200)
		self.send_header("Content-type", contentType)
		self.end_headers()
		with open(targetPath, 'rb') as f:
			self.wfile.write(f.read())

	def checkAccess(self, targetPath):
		# format targetPath to be an absolute path
		if targetPath == '/': targetPath = '/index.html'
		baseDir = os.path.dirname(os.path.abspath(sys.argv[0])) + '/html'
		targetPath = os.path.abspath(baseDir + targetPath)

		# make sure file exist and is allowed
		isFileExisting = os.path.isfile(targetPath)
		isFileAllowed = os.path.abspath(targetPath).startswith(baseDir)
		if not isFileAllowed:
			print("Trying to read out of scope file: " + targetPath) # log this as it may be an attacker
			raise PserverException('File does not exist')
		if not isFileExisting:
			raise PserverException('File does not exist')

		# return valid, allowed file path
		return targetPath

	def do_POST(self):
		starttime = time.time()
		try:
			# decode request json
			req = dict()
			if self.headers.get_all(name='content-length') != None:
				length = int(self.headers.get_all(name='content-length')[0])
				reqJson = str(self.rfile.read(length), 'utf-8')
				req = json.loads(reqJson) if len(reqJson)>0 else dict()

			# find and execute method
			requestHandler = self.getRequestHandler(self.path)
			result = self.executeApiMethod(requestHandler, req)
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

		# if result['status'] == 'error': print(json.dumps(result, indent=4))
		print('{f} took {time}s to answer'.format(f = self.path, time = round(time.time()-starttime, 2)))

		self.send_response(200)
		self.send_header("Content-type", "application/json")
		self.end_headers()
		self.wfile.write(bytes(json.dumps(result, indent=4, default=to_json), 'utf-8'))

	def getRequestHandler(self, path):
		if path == '':
			print("Aborted handling request because no command was given. ")
			raise PserverException('You need to specify a command')
		if path.startswith('/'): path = path[1:]

		pathParts = path.split('/')
		rhModuleName = 'api.' + '.'.join(pathParts[:-1])
		rhName = pathParts[-1]

		try:
			apiModule = sys.modules[rhModuleName]
			return getattr(apiModule, rhName)
		except (KeyError, AttributeError) as e:
			print("Unknown or invalid command: " + path)
			raise PserverException('Unknown or invalid command')
		print("Handling request: " + rhName + " in module " + rhModuleName)

	def executeApiMethod(self, requestHandler, req):
		rh = requestHandler(context, req)
		result = rh.execute_internal()
		return result

# Handle requests in a separate thread
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	pass

class PServerRequestHandler:
	def __init__(self, context, args):
		self.context = context
		self.args = args
		self.checkArgs()
	def checkArgs(self):
		# TODO only the existance of the params is checked here. we need to be able to define the complete data structure
		expectedArgs = inspect.getargspec(self.execute).args
		expectedArgs.remove('self')
		expectedArgs.sort()
		gotArgs = sorted(list(self.args.keys()))
		if gotArgs != expectedArgs:
			raise PserverException('Problem with parameters: Expected {expected}, got {got}'
				.format(expected = expectedArgs, got = gotArgs)
			)
	def execute_internal(self):
		self.preExec()
		result = self.execute(**self.args)
		self.verifyResultFormat(result)
		self.postExec()
		return result
	def preExec(self):
		pass
	def execute(self):
		raise PserverException('Request Handler "' + type(self).__name__ + '" not implemented')
	def postExec(self):
		pass
	def verifyResultFormat(self, result):
		if not (isinstance(result, dict) and 'status' in result and 'result' in result):
			raise PserverException('Bad result format: ' + str(result))

PORT = 80
server = None
context = {}
def start():
	global server
	server = ThreadedHTTPServer(('', PORT), RequestHandler)
	t = threading.Thread(target=server.serve_forever)
	t.daemon = True
	t.start()
	print("Started PServer")

def stop():
	print("Stopping PServer...")
	server.shutdown()
	print("Stopped PServer")

def setContext(c):
	global context
	context = c
