from enum import Enum, auto


class MessageType(Enum):
    ELECTION = auto()
    ALIVE = auto()
    VICTORY = auto()

    # Instruct a node to start the leader election algorithm.
    WAKEUP = auto()


class Message:

    def __init__(self, msg_type: MessageType, msg_body):
        self.msg_type = msg_type
        self.msg_body = msg_body

    def __str__(self):
        return "Message: {msg_type: " + str(self.msg_type) + ", msg_body: " + str(self.msg_body) + "}"
