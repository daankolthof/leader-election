from src.Message import MessageType, Message
from src.Node import Node
import random
import threading
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

def run_simulation(simulation_node_count):
    # Initialize the nodes.
    nodes = []
    for i in range(0, number_of_nodes_in_simulation):
        nodes.append(Node(i+1))

    # After initialization, set node neighbours (next neighbour in the array).
    for i in range(len(nodes)):
        nodes[i].set_all_nodes(nodes.copy())

    Node.expected_leader = nodes[-1]

    # Randomly have nodes detect leader failure
    number_of_nodes_to_wake = random.randint(1, number_of_nodes_in_simulation)

    logging.info("Waking up %i node(s)", number_of_nodes_to_wake)

    #random.shuffle(nodes)

    #nodes_to_wake = []
    #for i in range(0, number_of_nodes_to_wake):
    #    nodes_to_wake.append(nodes[i])

    nodes_to_wake = [nodes[-1]]


    # Define the function that will run on the new threads
    def run_on_thread(node):
        logging.info("Thread starting for node %i", node.node_number)
        node.run()
        logging.info("Thread stopped for node %i", node.node_number)


    # Create all threads (with function listed above)
    threads = []
    for node in nodes:
        threads.append(threading.Thread(target=run_on_thread, args=(node,)))

    # Start threads
    for thread in threads:
        thread.start()

    # Wake up nodes
    for node_to_wake in nodes_to_wake:
        wakeup_message = Message(MessageType.WAKEUP, {})
        node_to_wake.receive(None, wakeup_message)

    # Join threads after they're done
    for thread in threads:
        thread.join()

number_of_nodes_in_simulation = 3

for i in range(0, 1):
    Node.leader_elected = None
    Node.expected_leader = None

    run_simulation(number_of_nodes_in_simulation)

    if Node.leader_elected != Node.expected_leader:
        print(Node.leader_elected)
        print(Node.expected_leader)
        logging.error("Testing failure: Expected Node %i to be leader, got Node %i", Node.expected_leader.node_number, Node.leader_elected.node_number)
