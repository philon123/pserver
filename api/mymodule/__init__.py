import pserver #we always need the pserver module to use the PServerRequestHandler class
from . import submodule #include a sub module for a nested api
from MyRequestHandler import MyRequestHandler

#basic example
class sayHello(pserver.PServerRequestHandler):
	def execute(self):
		return dict(
			status = 'ok',
			result = 'Hello!'
		)

#example to show parameter usage
class sayMyName(pserver.PServerRequestHandler):
	def execute(self, name):
		return dict(
			status = 'ok',
			result = name
		)


#example for RequestHandler that does some db stuff. It uses a cutom RequestHandler class defined in the api module
class insertToDb(MyRequestHandler):
	def execute(self, name):
		#TODO actual db stuff :)
		return dict(
			status = 'ok',
			result = 'Saved {name} to database {db}!'.format(
				name=name,
				db=self.context['db']
			)
		)
