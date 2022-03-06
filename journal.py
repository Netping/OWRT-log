from threading import Thread
from threading import Lock
import ubus
import os
import hashlib



class journal:
    ubus_flag = False

    def WriteLog(modulename, typelog, facility, message):
        msg = {
                'text' : message,
                'tag' : modulename + '(' + typelog + ')',
                'facility' : facility,
                'ubus_rpc_session' : '1'
            }

        try:
            ubus.connect()
            journal.ubus_flag = True
        except:
            journal.ubus_flag = False

        #log message
        #os.system('logger -p "' + msg['facility'] +'" -t "' + msg['tag'] + '" "' + msg['text'] + '"')
        ubus.call("owrt_log", "add_task", msg)

        if journal.ubus_flag:
            ubus.disconnect()
            journal.ubus_flag = False
