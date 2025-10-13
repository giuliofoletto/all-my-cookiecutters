import json
import logging

import zmq

logger = logging.getLogger(__name__)

PAIR_ADDR = "inproc://control_communicator"


def create_communicator(context, port, name, peers):
    return Communicator(context, port, name, peers)


class Communicator:
    def __init__(self, context, port, name, peers):
        self.setup(context, port, name, peers)
        self.receive_loop()
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

        self.pair = context.socket(zmq.PAIR)
        self.pair.bind(PAIR_ADDR)
        self.poller = zmq.Poller()
        self.poller.register(self.router, zmq.POLLIN)
        self.poller.register(self.pair, zmq.POLLIN)
        self.should_continue = True

        logger.info(f"Communicator {name} initialized")

    def receive_loop(self):
        while self.should_continue:
            events = self.poller.poll()
            for event in events:
                if event[0] == self.pair:
                    try:
                        msg = self.pair.recv_json()
                    except json.JSONDecodeError:
                        logger.warning("Received invalid JSON message")
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
                    try:
                        msg = self.router.recv_json()
                    except json.JSONDecodeError:
                        logger.warning("Received invalid JSON message")
                        continue
                    else:  # Only if try succeeds
                        self.process_message(msg)

    def send(self, recipient, command, parameters=None):
        msg = {"recipient": recipient, "command": command}
        if parameters is not None:
            msg["parameters"] = parameters
        self.dealer.send_json(msg)

    def send_control(self, command, parameters=None):
        msg = {"command": command}
        if parameters is not None:
            msg["parameters"] = parameters
        self.pair.send_json(msg)

    def process_message(self, msg):
        if msg.get("recipient", None) != self.name:
            logger.debug(f"Message not for me: {msg}")
            return
        command = msg.get("command", None)
        parameters = msg.get("parameters", {})
        if command == "close":
            logger.info("Termination command received from peer")
            self.send_control("close")

    def finish(self):
        self.router.close()
        self.dealer.close()
        self.pair.close()
        self.poller.unregister(self.router)
        self.poller.unregister(self.pair)
        logger.info(f"Communicator {self.name} terminated")
