from threading import Thread
from threading import Lock
import ubus




class journal:
    task_list = []
    params = None
    pollThread = None
    mutex = Lock()

    def WriteLog(self, modulename, type, facility, message):
        self.__loadparams()
        
        logmsg = '' #TODO build log message from args
        l = { 'params' : journal.params,
                'message' : logmsg }

        mutex.acquire()
        journal.task_list.append(l)
        mutex.release()

        if not journal.pollThread:
            journal.pollThread = Thread(target=self.__poll, args=())
            journal.pollThread.start()


    def __loadparams():
        pass

    def __poll():
        while journal.task_list:
            mutex.acquire()
            l = journal.task_list.pop()
            mutex.release()

            #TODO log message
