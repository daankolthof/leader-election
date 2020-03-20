from enum import Enum, auto


class Message:

    def __init__(self, msg_type, msg_body):
        self.msg_type = msg_type
        self.msg_body = msg_body

    def __str__(self):
        return "Message: {msg_type: " + str(self.msg_type) + ", msg_body: " + str(self.msg_body) + "}"


class MessageType(Enum):
    ALG = auto()
    AVS = auto()
    AVS_RESP = auto()
