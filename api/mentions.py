import json
from status import StatusUpdate

class Mentions(object):
    def __init__(self, data):
        self.data = json.loads(data)
        self.status = StatusUpdate()
        self.text, self.type = self.process_message()

    def process_message(self):
        messages = self.data['message']['body']['content'][0]['content'][1:] # The first message is 'mention' itself.

        print "FILTERED_MESSAGE: {}".format(messages)
        first_msg = messages[0]['text'].strip()
        print "MESSAGE: {}".format(first_msg)

        if first_msg == '!update':
            if not self.validate():
                return 'This command is not for you :)', 'text/plain'

            print "SENDING TO UPDATE: {}".format(messages[1:])
            return self.status.update(messages[1:])
        elif first_msg == '!start':
            if not self.validate():
                return 'This command is not for you :)', 'text/plain'

            return self.status.new_day()
        elif first_msg.startswith('!remove'):
            if not self.validate():
                return 'This command is not for you :)', 'text/plain'

            if len(first_msg.split()) > 1:
                return self.status.delete_for_index(first_msg.split()[-1])
            return self.status.delete_last_added()

        elif first_msg.lower() == 'status':
            return self.status.send_update()


        return 'Hey There!', 'text/plain'

    def validate(self):
        userId = self.data['sender']['id']

        if userId == '5a26734395dac237f1299f01':
            print "User ID matched!"
            return True
        print "User Id didn't matched {}".format(userId)
        return False
