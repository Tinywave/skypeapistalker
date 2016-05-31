import skypeapi
import message_dict
import sys
import time
import random

if __name__ == '__main__':
    sleep = False
    sleep_duration = 0
    message_set = []
    for item in sys.argv:
        item = item.split('=',1)
        if len(item) > 1:
            if item[0] == '--sleep':
                sleep = True
                sleep_duration = random.randint(0, 60*60)
            elif item[0] == '--sleep-max':
                sleep = True
                sleep_duration = random.randint(0, int(item[1]))
            elif item[0] == '--message-set':
                if item[1] == 'tests':
                    message_set = message_dict.Messages().tests
                elif item[1] == 'greetings':
                    message_set = message_dict.Messages().greetings
        else:
            pass
    if sleep:
        time.sleep(sleep_duration)
    skypeconn = skypeapi.Skype()
    skypeconn.start()
    for message in message_set:
        skypeconn.send_chatmessage(receiver=message['receiver'], message=message['message'])

