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

    def __init__(self, node_number, leader_node):
        self.node_number = node_number
        self.nodes_online_map = None
        self.nodes_last_ping_map = None

        # Algorithm-specific variables
        self.leader_node = leader_node

        self.lock = threading.Lock()
        self.message_queue = []

        self.is_running = True

        self.last_sent_ping_time = None

    def set_all_nodes(self, all_nodes):
        for node in all_nodes:
            if self == node:
                continue

            self.nodes_online_map[node] = True
            self.nodes_last_ping_map[node] = None

    def send_pings(self):
        current_time_seconds = int(time.time())

        # If we haven't sent any pings yet or it has been 5 seconds since last ping sent out.
        if not self.last_sent_ping_time or current_time_seconds > self.last_sent_ping_time+5:
            ping_message: Message = Message(MessageType.PING, None)

            for node, online_status in self.nodes_online_map:
                if online_status:
                    node.receive(self, ping_message)
                    self.nodes_last_ping_map[node] = current_time_seconds

            self.last_sent_ping_time = current_time_seconds

    def check_for_pongs(self):
        current_time_seconds = int(time.time())

        # Check the ping map to see if any pings have not been answered within 2 seconds.
        for node, last_ping_time in self.nodes_last_ping_map:
            if last_ping_time and self.nodes_online_map[node] and last_ping_time + 2 < current_time_seconds:
                # Failed to receive pong on time.
                self.nodes_online_map[node] = False
                if node == self.leader_node:
                    # Leader node failed, trigger new leader election
                    self.trigger_election()

    def trigger_election(self):
        logging.info("Node %i  has started new leader election", self.node_number)
        # TODO: Implement this

    def run(self):

        while self.is_running:
            # Random delay to simulate read-world network traffic.
            random_timeout()

            self.send_pings()

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
        logging.info("Node %i (status:%s)  is processing '%s' from node %i", self.node_number, self.status, incoming_message, from_node.node_number)

        msg_type: MessageType = incoming_message.msg_type
        msg_body = incoming_message.msg_body

        if MessageType.PING == msg_type:
            pong_message: Message = Message(MessageType.PONG, None)
            from_node.receive(self, pong_message)
        if MessageType.PONG == msg_type:
            self.nodes_last_ping_map[from_node] = None
            # self.nodes_online_map[from_node] = True # Not necessary for this simulation, failed nodes do not recover.
        elif MessageType.FAIL_NODE == msg_type:
            # 'Fail' the node, stopping its message processing loop.
            self.is_running = False
        else:
            raise RuntimeError("Unknown message type: " + msg_type)

    def __str__(self):
        return "Node " + str(self.node_number)
