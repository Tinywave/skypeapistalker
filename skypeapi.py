# based on https://gist.github.com/cwacek/3640980

import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service

import datetime
import pprint
import re
import sqlite3
import sys
import time
from threading import Thread


class MySkype(Thread):
    def __init__(self):

        remote_bus = dbus.SessionBus(mainloop=dbus.mainloop.glib.DBusGMainLoop(set_as_default=True))

        system_service_list = remote_bus.get_object('org.freedesktop.DBus', '/org/freedesktop/DBus').ListNames()
        skype_api_found = 0

        for service in system_service_list:
            if service == 'com.Skype.API':
                skype_api_found = 1
                break

        if not skype_api_found:
            sys.exit('No running API-capable Skype found')

        self.skype_api_object = remote_bus.get_object('com.Skype.API', '/com/Skype')
        try:
            answer = self.send_dbus_message('NAME XyoozSkypeStalker')
            if answer != 'OK':
                raise dbus.exceptions.DBusException()
        except dbus.exceptions.DBusException:
            sys.exit('Could not bind to Skype client')

        answer = self.send_dbus_message('PROTOCOL 8')

        if answer != 'PROTOCOL 8':
            sys.exit('This test program only supports Skype API protocol version 8')

        Thread.__init__(self)

    def send_dbus_message(self, message):
        response = self.skype_api_object.Invoke(message)
        return response


if __name__ == "__main__":
    conn = sqlite3.connect('skypeapi.db')
    cur = conn.cursor()
    try:
        cur.execute('create table friendsdata (skypeid text, timestamp text, onlinestatus text, fullname text);')
    except sqlite3.OperationalError:
        pass
    pprint.pprint(cur.execute('select * from friendsdata;').fetchall())

    t = MySkype()
    t.start()
    while True:
        friends = t.send_dbus_message("search friends")[len('USERS '):].split(',')
        friends.append(t.send_dbus_message("get currentuserhandle")[len('CURRENTUSERHANDLE '):])
        time = datetime.datetime.utcnow().timestamp()
        for user in friends:
            user = user.strip()
            try:
                onlinestatus = re.match('^USER .*? ONLINESTATUS (?P<status>.*?)$',
                                        t.send_dbus_message("get user {0} onlinestatus".format(user))).group('status')
            except:
                onlinestatus = 'UNDEFINED'
            try:
                fullname = re.match('^USER .*? FULLNAME (?P<fullname>.*?)$',
                                    t.send_dbus_message("get user {0} fullname".format(user))).group('fullname')
            except:
                fullname = 'UNDEFINED'
            cur.execute("insert into friendsdata (skypeid, timestamp, onlinestatus, fullname) values (?, ?, ?, ?);",
                        (user,
                         time,
                         onlinestatus,
                         fullname))
            conn.commit()
        time.sleep(15)
