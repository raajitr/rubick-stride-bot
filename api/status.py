import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from datetime import datetime
import os
import calendar
from api import mongo, MongoException

QUOTE = """
> If you are going through hell, keep going.
"""

class StatusUpdate(object):
    def __init__(self):
        self.today = datetime.now()
        # connecting to our collection
        self.standups = mongo.db.standups
        self.latest_standup = self.latest_standup()

    def latest_standup(self):
        for l in self.standups.find().sort('datetime', -1).limit(1):
            latest_standup = l

        return latest_standup

    def new_day(self):
        doc = {
            "datetime": self.today,
            "tasks": []
        }

        start = self.today.replace(hour=0, minute=0, second=0)
        end = self.today.replace(hour=23, minute=59, second=59)
        latest_standup = self.standups.find_one({'datetime':{'$lt': end, '$gte': start}})
        if latest_standup:
            raise MongoException('Same date')

        self.standups.insert(doc)

        return QUOTE, 'text/markdown'

    def update(self, messages):
        start_index = 0
        for index, m in enumerate(messages):
            if m.get('text'):
                start_index = index
                break

        messages = messages[start_index:]
        print "NEW FORMATTED MESSAGE: {}".format(messages)

        task = {
                "createdDate": self.today,
                "title": "{}".format(messages[0]['text']),
                "subpoints": []
                }

        line = ""
        for message in messages[1:]:
            if message['type'] == 'hardBreak':
                if line:
                    task["subpoints"].append(line)
                line = ""

            if 'text' not in message:
                continue

            if 'marks' in message:
                if message['marks'][0]['type'] == 'link':
                    line += "[task]({})".format(message['marks'][0]['attrs']['href'])
                elif message['marks'][0]['type'] == 'strong':
                    line += "**{}**".format(message["text"].encode("utf8"))
                elif message['marks'][0]['type'] == 'em':
                    line += "_{}_".format(message["text"].encode("utf8"))
                else:
                    line += "{}".format(message["text"].encode("utf8"))
            else:
                line += "{}".format(message["text"].encode("utf8"))

        task["subpoints"].append(line)

        self.standups.update({'datetime':self.latest_standup['datetime']},
                             {'$push':{"tasks":task}})

        return self.dict_to_md(task)

    def delete_last_added(self):
        self.standups.update({'datetime':self.latest_standup['datetime']},
                             {'$pop':{"tasks": 1}})

        return 'Removed last added task', 'text/plain'

    def delete_for_index(self, index):
        print len(self.latest_standup['tasks'])
        print index
        target_standup = self.latest_standup['tasks'][int(index)-1]
        print target_standup['title']
        self.standups.update({'datetime':self.latest_standup['datetime']},
                             {'$pull':{"tasks": {"title": target_standup['title']}}})

        return 'Removed Task #{}'.format(index), 'text/plain'

    def send_update(self):
        return_md = "Status Update for {} - {}\n".format(calendar.day_name[self.latest_standup["datetime"].weekday()], self.latest_standup["datetime"].strftime("%d/%m/%Y"))
        if not self.latest_standup["tasks"]:
            return "Nothing Logged in for today.", "text/plain"
        return self.dict_to_md(self.latest_standup["tasks"], return_md)

    def dict_to_md(self, tasks, return_md=""):
        if not isinstance(tasks, list):
            tasks = [tasks]

        for t in tasks:
            return_md += "- {}\n".format(t["title"].encode("utf8"))
            for s in t['subpoints']:
                return_md += "{}- {}\n".format(" "*2, s.encode("utf8"))

        return return_md, 'text/markdown'
