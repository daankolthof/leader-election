import time
import logging
import random
import threading
from enum import Enum, auto

from src.Message import Message, MessageType


def random_timeout():
    #timeout = 1 + random.uniform(-0.1, 0.1)
    timeout = random.uniform(0, 0.5)
    time.sleep(timeout)


class NodeState(Enum):
    candidate = auto()
    dummy = auto()
    leader = auto()
    passive = auto()
    waiting = auto()


class Node:
    leader_elected = False

    def __init__(self, node_number):
        self.node_number = node_number
        self.neighbour_node = None

        # Algorithm-specific variables
        self.status = NodeState.passive
        self.candidate_successor = None
        self.candidate_predecessor = None

        # Leader after election, will be set by the algorithm
        self.leader = None

        self.lock = threading.Lock()
        self.message_queue = []

    def set_neighbour(self, neighbour_node):
        self.neighbour_node = neighbour_node

    def run(self):
        while not Node.leader_elected:
            # Delay the wakeup a bit to allow other threads to do their thing as well (to simulate network traffic)
            random_timeout()

            from_node = None
            message = None

            with self.lock:
                # Take one message out of the queue
                if self.message_queue:
                    from_node, message = self.message_queue.pop(0)

            if message:
                if MessageType.WAKEUP == message.msg_type:
                    self.wakeup()
                else:
                    self.process_message(from_node, message)

    def wakeup(self):
        logging.info("Node %i has woken up", self.node_number)

        self.status = NodeState.candidate

        # Construct an ALG message and send it to the node's neighbour
        alg_message: Message = Message(MessageType.ALG, self)
        self.neighbour_node.receive(self, alg_message)

    def receive(self, from_node, incoming_message):
        logging.info("Node %i  received '%s' from node %s", self.node_number, incoming_message, from_node)
        with self.lock:
            self.message_queue.append((from_node, incoming_message))

    def process_message(self, from_node, incoming_message):
        logging.info("Node %i  is processing '%s' from node %i", self.node_number, incoming_message, from_node.node_number)

        msg_body = incoming_message.msg_body
        msg_type: MessageType = incoming_message.msg_type

        if msg_type == MessageType.ALG:
            if NodeState.passive == self.status:
                self.status = NodeState.dummy

                alg_message: Message = incoming_message
                self.neighbour_node.receive(self, alg_message)

            elif NodeState.candidate == self.status:
                self.candidate_predecessor = msg_body

                if self == msg_body:
                    logging.info("Node %i has been made leader", self.node_number)
                    self.status = NodeState.leader
                    Node.leader_elected = True

                else:
                    if not self.candidate_successor:
                        if self.node_number > msg_body.node_number:

                            self.status = NodeState.waiting

                            avs_message: Message = Message(MessageType.AVS, self)
                            msg_body.receive(self, avs_message)

                    else:
                        avs_response_message: Message = Message(MessageType.AVS_RESP, self.candidate_predecessor)
                        self.candidate_successor.receive(self, avs_response_message)

                        self.status = NodeState.dummy

        elif msg_type == MessageType.AVS:
            if NodeState.candidate == self.status:
                if not self.candidate_predecessor:
                    self.candidate_successor = msg_body

                else:
                    avs_response_message: Message = Message(MessageType.AVS_RESP, self.candidate_predecessor)
                    msg_body.receive(self, avs_response_message)

                    self.status = NodeState.dummy

            elif NodeState.waiting == self.status:
                self.candidate_successor = msg_body

        elif msg_type == MessageType.AVS_RESP:
            if NodeState.waiting == self.status:
                if self == msg_body:
                    logging.info("Node %i has been made leader", self.node_number)
                    self.status = NodeState.leader
                    Node.leader_elected = True

                else:
                    self.candidate_predecessor = msg_body

                    if not self.candidate_successor:
                        if msg_body.node_number < self.node_number:
                            self.status = NodeState.waiting

                            avs_message: Message = Message(MessageType.AVS, self)
                            msg_body.receive(self, avs_message)

                    else:
                        self.status = NodeState.dummy

                        avs_response_message: Message = Message(MessageType.AVS_RESP, msg_body)
                        self.candidate_successor.receive(self, avs_response_message)

        else:
            raise RuntimeError("Unknown message type: " + msg_type)

    def __str__(self):
        return "Node " + str(self.node_number)
