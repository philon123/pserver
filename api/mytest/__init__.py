from . import subsection

def sayHello():
	return dict(
		status = 'ok',
		result = 'Hello!'
	)

def sayMyName(name):
	return dict(
		status = 'ok',
		result = name
	)
