import time
import pserver  # import the main server module
import api  # import your api, this makes linters unhappy though # noqa


if __name__ == '__main__':
    # create pserver instance
    ps = pserver.PServer(config=dict(simpleAuth="root:root"))

    # set some global context for the RequestHandlers to use. The context can be changed at any time
    ps.setContext(dict(
        db = "myDB"
    ))

    # start the server asynchronously
    ps.start()

    # listen for a keboard interrupt, then exit
    while True:
        try:
            time.sleep(0.1)
        except KeyboardInterrupt:
            ps.stop()
            exit()
