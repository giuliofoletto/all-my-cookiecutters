from .app import create_app
from {{cookiecutter.project_slug}}.cli import arguments

import zmq

from threading import Thread

if __name__ == "__main__":
    # Arguments and input
    args = arguments()
    
    # DO SOMETHING WITH THE ARGUMENTS

    # Setup ZeroMQ
    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    socket.bind("inproc://control_app")
    app_thread = Thread(
        target=create_app,
        kwargs={"name": args.name, "port": args.port, "peer_ip": args.peer_ip, "peer_port": args.peer_port, "context": context},
    )
    app_thread.start()

    should_continue = True
    print("Enter 's' to stop the application")
    while should_continue:
        try:
            c = input()
        except (KeyboardInterrupt, EOFError):
            c = "s"
        if c.lower() == "s":
            socket.send_json({"command": "close"})
            socket.recv_json()  # Wait for ack
            should_continue = False
        else:
            print("Unknown command " + c + " ignored")

    socket.close()
    app_thread.join()
