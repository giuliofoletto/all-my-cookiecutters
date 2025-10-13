import pytest

from threading import Thread
import time
import zmq

from {{cookiecutter.project_slug}}.app import create_app


def test_app_normal():
    context_alice = zmq.Context()
    context_bob = zmq.Context()
    socket_alice = context_alice.socket(zmq.PAIR)
    socket_alice.bind("inproc://control_app")
    socket_bob = context_bob.socket(zmq.PAIR)
    socket_bob.bind("inproc://control_app")

    alice_thread = Thread(
        target=create_app,
        args=(context_alice, 5555, "alice", "127.0.0.1", 5556)
    )
    bob_thread = Thread(
        target=create_app,
        args=(context_bob, 5556, "bob", "127.0.0.1", 5555)
    )
    alice_thread.start()
    bob_thread.start()
    time.sleep(0.5)
    socket_alice.send_json({"command": "close"})
    socket_alice.recv_json()  # Wait for ack
    socket_bob.send_json({"command": "close"})
    socket_bob.recv_json()  # Wait for ack
    socket_alice.close()
    socket_bob.close()
    alice_thread.join()
    bob_thread.join()
    context_alice.term()
    context_bob.term()
