import sys
import os
import time
import json
import BaseHTTPServer
import urlparse
import base64
import md5
from SocketServer import ThreadingMixIn
import threading
import traceback
import inspect
import requests
import api

PSERVER_VERSION = "1.1.0"

class PserverException(Exception):
	pass

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
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

		print 'GET request ignored.'

		self.wfile.write('POST only')

	def do_POST(self):
		starttime = time.time()
		postfiles = []
		try:
			#decode request json
			req = {}
			if self.headers.getheader('content-length') != None:
				length = int(self.headers.getheader('content-length'))
				req = json.loads(self.rfile.read(length))

			#find method
			apiMethod = self.getApiMethod(self.path)
			if req.keys() != inspect.getargspec(apiMethod).args:
				raise PserverException('Missing expected parameters: Expected {expected}, got {got}'
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
			print json.dumps(result, indent=4)
		print "done. processing time " + str(round(time.time()-starttime, 2)) + "s"

		#return result
		self.send_response(200)
		self.send_header("Content-type", "application/json")
		self.end_headers()
		self.wfile.write(json.dumps(result, indent=4))

	def getApiMethod(self, path):
		if path == '':
			print "Aborted handling request because no command was given. "
			raise PserverException('You need to specify a command')
		if path.startswith('/'): path = path[1:]

		pathParts = path.split('/')
		apiModuleName = 'api.' + '.'.join(pathParts[:-1])
		apiMethodName = pathParts[-1]

		try:
			apiModule = sys.modules[apiModuleName]
			return getattr(apiModule, apiMethodName)
		except (KeyError, AttributeError) as e:
			print "Unknown or invalid command supplied: " + path
			raise PserverException('Unknown or invalid command')
		print "Handling command: " + apiMethodName + " in module " + apiModuleName

	def verifyResultFormat(self, result):
		if not (isinstance(result, dict) and 'status' in result and 'result' in result):
			raise PserverException('Bad result format: ' + str(result))

#Handle requests in a separate thread
class ThreadedHTTPServer(ThreadingMixIn, BaseHTTPServer.HTTPServer):
	pass

def download_file(url):
	local_filename = '/tmp/' + url.split('/')[-1]
	r = requests.get(url, stream=True)
	with open(local_filename, 'wb') as f:
		for chunk in r.iter_content(chunk_size=1024):
			if chunk: # filter out keep-alive new chunks
				f.write(chunk)
	if r.status_code != 200:
		raise Exception('Could not download file ' + url)
	return local_filename

#TODO
def callApiFunction(apiModule, cmdName, postvars, postfiles):
	#check if fuction and spec exist


	#check parameters
	args = []

	#execute function
	result = getattr(sys.modules[apiModule], cmdName)(*args)


	#check results


if __name__ == '__main__':
	server = ThreadedHTTPServer(('', 8080), RequestHandler)
	print "Started server. "
	server.serve_forever()
