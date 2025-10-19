import json
import logging

import zmq

logger = logging.getLogger(__name__)

POLLING_TIMEOUT_MS = 1  # in milliseconds


def create_communicator(context, port, name, peers):
    return Communicator(context, port, name, peers)


class Communicator:
    def __init__(self, context, port, name, peers):
        self.setup(context, port, name, peers)
        self.main_loop()
        self.finish()

    def setup(self, context, port, name, peers):
        self.name = name
        self.router = context.socket(zmq.ROUTER)
        self.router.setsockopt(zmq.IDENTITY, name.encode())
        self.router.bind(f"tcp://*:{port}")
        self.dealer = context.socket(zmq.DEALER)
        self.dealer.setsockopt(zmq.IDENTITY, name.encode())

        for peer in peers:
            peer_ip = peer["peer_ip"]
            peer_port = peer["peer_port"]
            connection_string = f"tcp://{peer_ip}:{peer_port}"
            self.dealer.connect(connection_string)

        self.control_socket = context.socket(zmq.PAIR)
        self.control_socket.bind("inproc://control_communicator")
        self.poller = zmq.Poller()
        self.poller.register(self.router, zmq.POLLIN)
        self.poller.register(self.control_socket, zmq.POLLIN)
        self.should_continue = True

        logger.info(f"Communicator {name} initialized")

    def main_loop(self):
        while self.should_continue:
            events = self.poller.poll(POLLING_TIMEOUT_MS)
            for event in events:
                if event[0] == self.control_socket:
                    try:
                        msg = self.control_socket.recv_json()
                    except json.JSONDecodeError:
                        logger.warning("Received invalid JSON message from controller")
                        continue
                    else:  # Only if try succeeds
                        logger.debug(
                            f"Communicator {self.name} received control message {msg}"
                        )
                        if msg.get("command", None) == "close":
                            logger.info(
                                f"Termination command received by communicator {self.name}"
                            )
                            self.should_continue = False
                            self.send_control("ack")
                elif event[0] == self.router:
                    sender = self.router.recv().decode()  # identity frame
                    try:
                        msg = self.router.recv_json()
                    except json.JSONDecodeError:
                        logger.warning(
                            f"Received invalid JSON message from peer {sender}"
                        )
                        continue
                    else:  # Only if try succeeds
                        self.process_peer_message(msg)

    def send_peer(self, recipient, command, parameters=None):
        msg = {"recipient": recipient, "command": command}
        if parameters is not None:
            msg["parameters"] = parameters
        self.dealer.send_json(msg)

    def send_control(self, command, parameters=None):
        msg = {"recipient": self.name, "command": command}
        if parameters is not None:
            msg["parameters"] = parameters
        self.control_socket.send_json(msg)

    def process_peer_message(self, sender, msg):
        recipient = msg.get("recipient", None)
        if recipient != self.name:
            logger.debug(
                f"Communicator {self.name} received a message from {sender} to {recipient}, ignoring"
            )
        else:
            command = msg.get("command", None)
            parameters = msg.get("parameters", {})
            if command == "close":
                logger.info(f"Termination command received from peer {sender}")
                self.send_control("close")

    def finish(self):
        self.router.close()
        self.dealer.close()
        self.control_socket.close()
        self.poller.unregister(self.router)
        self.poller.unregister(self.control_socket)
        logger.info(f"Communicator {self.name} terminated")
