import pserver

class sayHello(pserver.PServerRequestHandler):
	def execute(self):
		return dict(
			status = 'ok',
			result = 'Hello!'
		)
