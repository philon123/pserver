def sayHello(getvars, postvars, postfiles):
	return dict(
		status = 'ok',
		result = 'Hello!'
	)

def sayMyName(getvars, postvars, postfiles):
	name = postvars['name']

	return dict(
		status = 'ok',
		result = name
	)
