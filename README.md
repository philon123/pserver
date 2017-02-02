#What is this?

PServer is a simple web server that accepts only POST requests with JSON content and answers all requests in json. The motivation for this code is that other server libraries are really large, but I often only need this tiny subset of features.

Answers are also JSON, in the format {"status": S, "result": R} where S is either "ok" or "error" and R can be any value, including objects and arrays.

API functions are organized into nested folders inside the "api" directory. Organize your code just like the "test" folder is organized.

After starting the server with "python pserver.py" test the server as such:

curl -X POST http://127.0.0.1:8080/test/sayHello
result:
{
    "status": "ok",
    "result": "Hello!"
}

curl -X POST http://127.0.0.1:8080/test/sayMyName --data '{"name":"Phil"}'
result:
{
    "status": "ok",
    "result": "Phil"
}

curl -X POST http://127.0.0.1:8080/test/subtest/sayHello
result:
{
    "status": "ok",
    "result": "Hello again!"
}

#Changelog / feature list

v1.1.0
* Remove support for GET-vars and automatic preprocessing of files.
* Named parameters are enforced. Parameters that are lists or dicts are not further checked though.

v1.0.0
* It works
