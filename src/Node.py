import time
import logging
import random
from enum import Enum, auto

from src.Message import Message, MessageType


def random_timeout():
    timeout = 1 + random.uniform(-0.1, 0.1)
    time.sleep(timeout)


class NodeState(Enum):
    candidate = auto()
    dummy = auto()
    leader = auto()
    passive = auto()
    waiting = auto()


class Node:

    def __init__(self, node_number):
        self.node_number = node_number
        self.neighbour_node = None

        # Algorithm-specific variables
        self.status = NodeState.passive
        self.candidate_successor = None
        self.candidate_predecessor = None

        # Leader after election, will be set by the algorithm
        self.leader = None

    def set_neighbour(self, neighbour_node):
        self.neighbour_node = neighbour_node

    def wakeup(self):
        # Delay the wakeup a bit to allow other threads to do their thing as well (to simulate network traffic)
        random_timeout()
        logging.info("Node %i has woken up", self.node_number)

        self.status = NodeState.candidate

        # Construct an ALG message and send it to the node's neighbour
        alg_message: Message = Message(MessageType.ALG, self)
        self.neighbour_node.receive(self, alg_message)

    def receive(self, from_node, incoming_message):
        # Delay the receive a bit to allow other threads to do their thing as well (to simulate network traffic)
        random_timeout()
        logging.info("Node %i  received '%s' from node %i", self.node_number, incoming_message, from_node.node_number)

        msg_body = incoming_message.msg_body
        msg_type: MessageType = incoming_message.msg_type

        if msg_type == MessageType.ALG:
            if NodeState.passive == self.status:
                self.status = NodeState.dummy

                alg_message: Message = incoming_message
                self.neighbour_node.receive(self, alg_message)

            elif NodeState.candidate == self.status:
                self.candidate_predecessor = msg_body

                if self.node_number > msg_body.node_number:
                    if not self.candidate_successor:
                        self.status = NodeState.waiting

                        avs_message: Message = Message(MessageType.AVS, self)
                        msg_body.receive(self, avs_message)
                    else:
                        avs_response_message: Message = Message(MessageType.AVS_RESP, self.candidate_predecessor)
                        self.candidate_successor.receive(self, avs_response_message)

                        self.status = NodeState.dummy

                elif self.node_number == msg_body.node_number:
                    logging.info("Node %i has been made leader", self.node_number)
                    self.status = NodeState.leader

        elif msg_type == MessageType.AVS:
            exit()
        elif msg_type == MessageType.AVSRSP:
            exit()
        else:
            raise RuntimeError("Unknown message type: " + msg_type)

    def __str__(self):
        return "Node " + str(self.node_number) + " with neighbour: " + (
            str(self.neighbour_node.node_number) if self.neighbour_node else None)
