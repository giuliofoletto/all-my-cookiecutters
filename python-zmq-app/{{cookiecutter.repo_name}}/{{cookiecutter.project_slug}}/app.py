import logging
import zmq

from {{cookiecutter.project_slug}}.communicate import create_communicator

from threading import Thread

logger = logging.getLogger(__name__)


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

        self.pair_communicator = self.context.socket(zmq.PAIR)
        self.pair_communicator.connect("inproc://control_communicator")
        self.pair_main = self.context.socket(zmq.PAIR)
        self.pair_main.connect("inproc://control_app")
        self.poller = zmq.Poller()
        self.poller.register(self.pair_communicator, zmq.POLLIN)
        self.poller.register(self.pair_main, zmq.POLLIN)

        logger.info(f"App {self.name} initialized")

    def main_loop(self):
        while self.should_continue:
            events = self.poller.poll()
            for event in events:
                msg = event[0].recv_json()
                if msg.get("command", None) == "close":
                    logger.info(f"Termination command received by app {self.name}")
                    self.should_continue = False
                    self.pair_main.send_json({"command": "ack"})

    def finish(self):
        self.pair_communicator.send_json({"command": "close"})
        self.pair_communicator.recv_json()  # Wait for ack
        self.pair_communicator.close()
        self.pair_main.close()
        self.poller.unregister(self.pair_communicator)
        self.poller.unregister(self.pair_main)
        self.communicator_thread.join()
        logger.info(f"App {self.name} terminated")
