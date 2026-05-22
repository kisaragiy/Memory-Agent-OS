class MessageBus:
    def send(self, sender, receiver, message):
        receiver.receive(message)
