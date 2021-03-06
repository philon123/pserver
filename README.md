# What is this?

PServer is a simple web server that accepts only POST requests with JSON content and answers all requests in json. The motivation for this code is that other server libraries are really large, but I often only need this tiny subset of features.

Answers are also JSON, in the format {"status": S, "result": R} where S is either "ok" or "error" and R can be any value, including objects and arrays.

The library itself is included with `import pserver`. You must also include a module `api` that will hold submodules containing your api callbacks. The resulting directory structure is reflected in how you call your functions.

After starting the example api with "sudo python3 example.py" test the server as such:

#### Basic example: <br>
request: `curl -X POST http://127.0.0.1/mymodule/sayHello`<br>
```javascript 
{
    "status": "ok",
    "result": "Hello!"
}
```

#### Parameters: <br>
request: `curl -X POST http://127.0.0.1/mymodule/sayMyName --data '{"name":"Phil"}'`<br>
```javascript 
{
    "status": "ok",
    "result": "Phil"
}
```

#### Nested modules: <br>
request: `curl -X POST http://127.0.0.1/mymodule/submodule/sayHello`<br>
```javascript 
{
    "status": "ok",
    "result": "Hello from submodule!"
}
```

#### Context usage: <br>
request: `curl -X POST http://127.0.0.1/mymodule/insertToDb --data '{"name":"Phil"}'`<br>
```javascript 
{
    "result": "Saved Phil to the database!",
    "status": "ok"
}
```

# Changelog / feature list

v1.6.0
* Add http SimpleAuth by adding to the config `"simpleAuth": "user:pass"`

v1.5.0
* Allow configuration of port and baseDir

v1.4.2
* Make sure files outside of the html dir aren't reachable

v1.4.0
* Serve GET requests and return any file requested from inside the html directory. Example included

v1.3.0
* Requests are handled by subclasses of BasePServerRequestHandler
* preExec and postExec methods for preprocessing and cleanup
* Allow setting a global context which is passed to all handlers
* Allow specifying the port to use (default 80)

v1.2.0
* Migrated to Python 3.5
* make PServer a library, not a framework

v1.1.0
* Remove support for GET-vars and automatic preprocessing of files.
* Named parameters are enforced. Parameters that are lists or dicts are not further checked though.

v1.0.0
* It works
