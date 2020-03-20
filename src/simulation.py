from src.Node import Node
import random
import threading
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

# Initialize the nodes.
nodes = []
for i in range(0, 4):
    nodes.append(Node(i))

# After initialization, set node neighbours (next neighbour in the array).
for i in range(0, len(nodes) - 1):
    nodes[i].set_neighbour(nodes[i + 1])
nodes[-1].set_neighbour(nodes[0])

# Print out neighbours
for node in nodes:
    print(str(node))

# Randomly wake up 1 or 2 nodes.
random.shuffle(nodes)
number_of_nodes_to_wake = random.randint(1, 2)

logging.info("Waking up %i node(s)", number_of_nodes_to_wake)


# Define the function that will run on the new threads
def thread_function(node):
    logging.info("Thread starting for node %i", node.node_number)
    node.wakeup()
    logging.info("Thread stopped for node %i", node.node_number)


# Create all threads (with function listed above)
threads = []
for i in range(0, number_of_nodes_to_wake):
    threads.append(threading.Thread(target=thread_function, args=(nodes[i],)))

# Start threads
for thread in threads:
    thread.start()

# Join threads after they're done
for thread in threads:
    thread.join()
