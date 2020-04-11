import time
import logging
import random
from enum import Enum, auto

from src.Message import Message, MessageType


def random_timeout():
    timeout = 1 + random.uniform(-0.1, 0.1)
    time.sleep(timeout)


class NodeState(Enum):
    passive = auto()
    candidate = auto()
    dummy = auto()
    leader = auto()


class Node:

    def __init__(self, node_number):
        self.node_number = node_number
        self.neighbour_node = None

        # Algorithm-specific variables
        self.status = NodeState.passive
        self.candidate_successor = None
        self.candidate_predecessor = None

    def set_neighbour(self, neighbour_node):
        self.neighbour_node = neighbour_node

    def wakeup(self):
        # Delay the wakeup a bit to allow other threads to do their thing as well (to simulate network traffic)
        random_timeout()
        logging.info("Node %i has woken up", self.node_number)

        self.status = NodeState.candidate
        # Construct an ALG message and send it to the node's neighbour
        algMessage: Message = Message(MessageType.ALG, {})
        self.neighbour_node.receive(self, algMessage)

    def receive(self, from_node, message):
        # Delay the receive a bit to allow other threads to do their thing as well (to simulate network traffic)
        random_timeout()
        logging.info("Node %i  received '%s' from node %i", self.node_number, message, from_node.node_number)

        msgBody = message.msg_body
        msgType: MessageType = message.msg_type

        if msgType == MessageType.ALG:
            exit()
        elif msgType == MessageType.AVS:
            exit()
        elif msgType == MessageType.AVSRSP:
            exit()
        else:
            raise RuntimeError("Unknown message type: " + msgType)

    def __str__(self):
        return "Node " + str(self.node_number) + " with neighbour: " + (
            str(self.neighbour_node.node_number) if self.neighbour_node else None)
