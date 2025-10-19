import logging
import zmq

from {{cookiecutter.project_slug}}.communicate import create_communicator

from threading import Thread

logger = logging.getLogger(__name__)

POLLING_TIMEOUT_MS = 1  # in milliseconds


def create_app(context, port, name, peer_ip, peer_port):
    return App(context, port, name, peer_ip, peer_port)


class App:
    def __init__(self, context, port, name, peer_ip, peer_port):
        self.setup(context, port, name, peer_ip, peer_port)
        self.main_loop()
        self.finish()

    def setup(self, context, port, name, peer_ip, peer_port):
        self.name = name
        self.context = context
        self.port = port
        self.peer_ip = peer_ip
        self.peer_port = peer_port

        self.should_continue = True

        self.communicator_thread = Thread(
            target=create_communicator,
            args=(
                self.context,
                self.port,
                self.name,
                [
                    {
                        "peer_ip": self.peer_ip,
                        "peer_port": self.peer_port,
                    }
                ],
            ),
        )
        self.communicator_thread.start()

        self.control_communicator_socket = self.context.socket(zmq.PAIR)
        self.control_communicator_socket.connect("inproc://control_communicator")
        self.control_main_socket = self.context.socket(zmq.PAIR)
        self.control_main_socket.connect("inproc://control_app")
        self.poller = zmq.Poller()
        self.poller.register(self.control_communicator_socket, zmq.POLLIN)
        self.poller.register(self.control_main_socket, zmq.POLLIN)

        logger.info(f"App {self.name} initialized")

    def main_loop(self):
        while self.should_continue:
            events = self.poller.poll(POLLING_TIMEOUT_MS)
            for event in events:
                if event[0] == self.control_main_socket:
                    msg = event[0].recv_json()
                    if msg.get("command", None) == "close":
                        logger.info(f"Termination command received by app {self.name}")
                        self.should_continue = False

    def finish(self):
        self.send_control(self.control_communicator_socket, "close")
        self.wait_for_command(self.control_communicator_socket, "ack")
        self.control_communicator_socket.close()
        self.send_control(self.control_main_socket, "ack")
        self.control_main_socket.close()
        self.poller.unregister(self.control_communicator_socket)
        self.poller.unregister(self.control_main_socket)
        self.communicator_thread.join()
        logger.info(f"App {self.name} terminated")

    def send_peer(self, recipient, command, parameters):
        self.control_communicator_socket.send_json(
            {
                "recipient": self.name,
                "command": "forward",
                "parameters": {
                    "recipient": recipient,
                    "command": command,
                    "parameters": parameters,
                },
            }
        )

    def send_control(self, socket, command, parameters=None):
        msg = {"recipient": self.name, "command": command}
        if parameters is not None:
            msg["parameters"] = parameters
        socket.send_json(msg)

    def wait_for_command(self, socket, command):
        waiting_for_command = True
        while waiting_for_command:
            msg = socket.recv_json()
            if msg.get("command", None) == command:
                waiting_for_command = False
            else:
                logger.warning(f"Expected {command}, but received: {msg}")