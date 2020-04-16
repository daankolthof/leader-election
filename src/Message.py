from enum import Enum, auto


class MessageType(Enum):
    ELECTION = auto()
    ALIVE = auto()
    VICTORY = auto()

    # Not part of the leader election algorithm, used by nodes to check each other.
    PING = auto()
    PONG = auto()

    # Not part of the leader election algorithm, used for to instruct a node to simulate failure.
    FAIL_NODE = auto()


class Message:

    def __init__(self, msg_type: MessageType, msg_body):
        self.msg_type = msg_type
        self.msg_body = msg_body

    def __str__(self):
        return "Message: {msg_type: " + str(self.msg_type) + ", msg_body: " + str(self.msg_body) + "}"
