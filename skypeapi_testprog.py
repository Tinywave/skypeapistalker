# based on https://gist.github.com/cwacek/3640980

import pprint
import sys

import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service

#import gobject
from threading import Thread

#class SkypeNotify(dbus.service.Object):
#    """DBus object which exports a Notify method. This will be called by Skype for all
#    notifications with the notification string as a parameter. The Notify method of this
#    class calls in turn the callable passed to the constructor.
#    """

#    def __init__(self, bus):
#        dbus.service.Object.__init__(self, bus, '/com/Skype/Client')
#        print('Skype notify init done')

#    @dbus.service.method(dbus_interface='com.Skype.API.Client')
#    def Notify(self, com):
#        print('it works, that s what I got from Skype:')
#        print(com)


class My_Skype(Thread):
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
            answer = self.send_dbus_message('NAME XyoozSkypeAPITest')
            if answer != 'OK':
                raise dbus.exceptions.DBusException()
        except dbus.exceptions.DBusException:
            sys.exit('Could not bind to Skype client')

        print("OK:", answer)

        answer = self.send_dbus_message('PROTOCOL 8')
        print("PROTOCOL 8:", answer)

        if answer != 'PROTOCOL 8':
            sys.exit('This test program only supports Skype API protocol version 8')

        #print('TestInit3')
        #self.skype_in = SkypeNotify(remote_bus)
        #gobject.threads_init()

        Thread.__init__(self)

    # Client -> Skype
    def send_dbus_message(self, message):
        response = self.skype_api_object.Invoke(message)
        return response



if __name__ == "__main__":
    t = My_Skype()
    t.start();
    while True:
        pprint.pprint(t.send_dbus_message(input("cmd> ")))

