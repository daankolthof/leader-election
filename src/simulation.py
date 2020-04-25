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
        nodes[i].set_all_nodes(nodes)

    Node.expected_leader = nodes[-1]

    # Randomly have nodes detect leader failure
    number_of_nodes_to_wake = random.randint(1, number_of_nodes_in_simulation)

    logging.info("Waking up %i node(s)", number_of_nodes_to_wake)

    nodes_shuffled = nodes.copy()
    random.shuffle(nodes_shuffled)

    nodes_to_wake = []
    for i in range(0, number_of_nodes_to_wake):
        nodes_to_wake.append(nodes_shuffled[i])

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
        wakeup_message = Message(MessageType.WAKEUP)
        node_to_wake.receive(None, wakeup_message)

    # Join threads after they're done
    for thread in threads:
        thread.join()

    return nodes


number_of_test_runs = 100

for i in range(number_of_test_runs):
    Node.leader_elected = None
    Node.expected_leader = None

    number_of_nodes_in_simulation = random.randint(1, 10)

    nodes = run_simulation(number_of_nodes_in_simulation)

    elected_leader = nodes[0].leader
    if elected_leader != Node.expected_leader:
        logging.error("Testing failure: Expected Node %i to be leader, got Node %i", Node.expected_leader.node_number, elected_leader.node_number)
        exit(-1)

    for node in nodes[1:]:
        if node.leader != elected_leader:
            logging.error("Testing failure: Not all nodes have the same leader elected.")
            exit(-1)

logging.info("Testing succeeded with %i random test runs.", number_of_test_runs)
