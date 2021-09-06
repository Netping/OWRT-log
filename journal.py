from threading import Thread
from threading import Lock
import ubus
import os
import hashlib




class journal:
    task_list = []
    params = None
    paramsHash = ''
    pollThread = None
    mutex = Lock()

    def WriteLog(self, modulename, type, facility, message):
        self.__loadparams()
        
        logmsg = message #TODO build log message from args
        l = { 'params' : journal.params,
                'message' : {
                    'text' : logmsg,
                    'tag' : modulename,
                    'facility' : facility 
                }
            }

        journal.mutex.acquire()
        journal.task_list.append(l)
        journal.mutex.release()

        if not journal.pollThread:
            journal.pollThread = Thread(target=self.__poll, args=())
            journal.pollThread.start()

    def __md5(self, fname):
        hash_md5 = hashlib.md5()
        with open(fname, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)

        return hash_md5.hexdigest()

    def __loadparams(self):
        newHash = self.__md5("/etc/config/system")
        print(newHash)
        print(journal.paramsHash)

        if newHash != journal.paramsHash:
            try:
                ubus.connect()

                confvalues = ubus.call("uci", "get", {"config": "system"})
                print(confvalues)
                
                #TODO

                ubus.disconnect()
                journal.paramsHash = newHash
            except:
                print("Can't load params")

    def __poll(self):
        while journal.task_list:
            journal.mutex.acquire()
            l = journal.task_list.pop()
            par = l['params']
            msg = l['message']
            journal.mutex.release()

            #log message
            os.system('logger -p "' + msg['facility'] +'" -t "' + msg['tag'] + '" "' + msg['text'] + '"')

        journal.pollThread = None
