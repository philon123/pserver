function doSomething() {
	console.log("doing something...");
	window.setTimeout(doSomething, 1000);
}
doSomething();
