import time
import logging
import random
import threading

from src.Message import Message, MessageType


def random_timeout():
    timeout = random.uniform(0, 0.01)
    time.sleep(timeout)


class Node:
    leader_elected = None
    expected_leader = -1

    def __init__(self, node_number):
        self.node_number = node_number
        self.all_nodes = None

        self.lock = threading.Lock()
        self.message_queue = []

        self.is_running = True

    def set_all_nodes(self, all_nodes):
        self.all_nodes = all_nodes

    def on_node_elected_as_leader(self):
        logging.info("Node %i has selected itself as leader", self.node_number)
        Node.leader_elected = self
        victory_message = Message(MessageType.VICTORY, None)
        for node in self.all_nodes:
            if self == node:
                continue

            node.receive(self, victory_message)

        self.is_running = False

    def trigger_election(self):
        logging.info("Node %i has started new leader election", self.node_number)
        # If the current node has the highest node number, it's the leader. Inform the other nodes of this.
        if self.all_nodes[-1] == self:
            self.on_node_elected_as_leader()
        else:
            # Send an election message to all nodes with a higher node number than current node's number.
            election_message = Message(MessageType.ELECTION, None)
            # node_number is array index+1 (so don't do node_number-1 as that will lead to nodes messaging themselves).
            for i in range(self.node_number, len(self.all_nodes)):
                self.all_nodes[i].receive(self, election_message)

    def run(self):

        while self.is_running:
            # Random delay to simulate read-world network traffic.
            random_timeout()

            from_node = None
            message = None

            with self.lock:
                # Take one message out of the queue
                if self.message_queue:
                    from_node, message = self.message_queue.pop(0)

            if message:
                self.process_message(from_node, message)

    def receive(self, from_node, incoming_message):
        logging.info("Node %i  received '%s' from node %s", self.node_number, incoming_message, from_node)
        with self.lock:
            self.message_queue.append((from_node, incoming_message))

    def process_message(self, from_node, incoming_message):
        logging.info("Node %i is processing '%s' from node %i", self.node_number, incoming_message, from_node.node_number if from_node else -1)

        msg_type: MessageType = incoming_message.msg_type
        msg_body = incoming_message.msg_body

        if MessageType.WAKEUP == msg_type:
            self.trigger_election()
        #elif MessageType.ELECTION == msg_type:
        #    # TODO: Implement this
        #    raise(NotImplementedError())
        #elif MessageType.ALIVE == msg_type:
        #    # TODO: Implement this
        #    raise (NotImplementedError())
        elif MessageType.VICTORY == msg_type:
            # Set winner as leader and stop the leader election process.
            Node.leader_elected = from_node
            self.is_running = False

    def __str__(self):
        return "Node " + str(self.node_number)
