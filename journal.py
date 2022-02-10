from threading import Thread
from threading import Lock
import ubus
import os
import hashlib



class journal:
    task_list = []
    params = None
    pollThread = None
    mutex = Lock()
    configmutex = Lock()

    def WriteLog(modulename, typelog, facility, message):
        #self.__loadparams()
        journal.__loadparams()
        
        logmsg = message
        l = { 'params' : journal.params,
                'message' : {
                    'text' : logmsg,
                    'tag' : modulename + '(' + typelog + ')',
                    'facility' : facility 
                }
            }

        journal.mutex.acquire()
        journal.task_list.insert(0, l)
        journal.mutex.release()

        if not journal.pollThread:
            journal.pollThread = Thread(target=journal.__poll, args=())
            journal.pollThread.start()

    def __md5(fname):
        hash_md5 = hashlib.md5()
        with open(fname, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)

        return hash_md5.hexdigest()

    def __readhash(hashfile):
        value = ''
        with open("/etc/netping/log/" + hashfile, "r") as f:
            value = f.readline()

        return value

    def __loadparams():
        journal.configmutex.acquire()

        newHash = journal.__md5("/etc/config/journalconf")
        oldHash = journal.__readhash("journal_hash")

        if newHash != oldHash:
            try:
                ubus.connect()

                value = {}
                confvalues = ubus.call("uci", "get", {"config": "journalconf"})
                for confdict in list(confvalues[0]['values'].values()):
                    if confdict['.type'] == 'info':
                        try:
                            if confdict['log_ip']:
                                value['log_ip'] = confdict['log_ip']
                        except:
                            value['log_ip'] = ''

                        try:
                            if confdict['log_port']:
                                value['log_port'] = confdict['log_port']
                        except:
                            value['log_port'] = ''

                        try:
                            if confdict['log_proto']:
                                value['log_proto'] = confdict['log_proto']
                        except:
                            value['log_proto'] = ''
                            
                        try:
                            if confdict['log_file']:
                                value['log_file'] = confdict['log_file']    
                        except:
                            value['log_file'] = ''

                        try:
                            if confdict['log_remote']:
                                value['log_remote'] = confdict['log_remote']
                        except:
                            value['log_remote'] = ''

                        try:
                            if confdict['log_size']:
                                value['log_size'] = confdict['log_size']
                        except:
                            value['log_size'] = ''

                        try:
                            if confdict['log_type']:
                                value['log_type'] = confdict['log_type']
                        except:
                            value['log_type'] = ''

                        journal.params = value

                ubus.disconnect()
                
                with open("/etc/netping/log/journal_hash", "w") as f:
                    f.write(newHash)

                #set to system conf vi os.system (ubus call doesn't work)
                for k, v in value.items():
                    os.system("uci set system.@system[0]." + k + "=" + v)

                os.system("uci commit system")
                os.system("/etc/init.d/log restart")

            except:
                print("Can't load params")

        newHash = journal.__md5("/etc/config/system")
        oldHash = journal.__readhash("system_hash")

        if newHash != oldHash:
            try:
                ubus.connect()

                confvalues = ubus.call("uci", "get", {"config": "system"})
                for confdict in list(confvalues[0]['values'].values()):
                    if confdict['.type'] == 'system':
                        value = {}

                        try:
                            if confdict['log_ip']:
                                value['log_ip'] = confdict['log_ip']
                        except:
                            value['log_ip'] = ''

                        try:
                            if confdict['log_port']:
                                value['log_port'] = confdict['log_port']
                        except:
                            value['log_port'] = ''

                        try:
                            if confdict['log_proto']:
                                value['log_proto'] = confdict['log_proto']
                        except:
                            value['log_proto'] = ''
                            
                        try:
                            if confdict['log_file']:
                                value['log_file'] = confdict['log_file']    
                        except:
                            value['log_file'] = ''

                        try:
                            if confdict['log_remote']:
                                value['log_remote'] = confdict['log_remote']
                        except:
                            value['log_remote'] = ''

                        try:
                            if confdict['log_size']:
                                value['log_size'] = confdict['log_size']
                        except:
                            value['log_size'] = ''

                        try:
                            if confdict['log_type']:
                                value['log_type'] = confdict['log_type']
                        except:
                            value['log_type'] = ''

                        #journal.params = value

                ubus.disconnect()

                #os.system("/etc/init.d/log restart")
                
                with open("/etc/netping/log/system_hash", "w") as f:
                    f.write(newHash)
            except:
                print("Can't load params")

        journal.configmutex.release()

    def __applyparams(p):
        try:
            ubus.connect()

            ubus.call("uci", "set", {"config" : "system", "type" : "system", "values" : p})
            ubus.call("uci", "commit", {"config" : "system"})

            ubus.disconnect()

            os.system("/etc/init.d/log restart")

        except:
            print("Can't connect to ubus")

    def __poll():
        while journal.task_list:
            journal.mutex.acquire()

            l = journal.task_list.pop()
            par = l['params']
            msg = l['message']
            journal.mutex.release()

            journal.configmutex.acquire()

            if par != journal.params:
                journal.__applyparams(par)

            #log message
            os.system('logger -p "' + msg['facility'] +'" -t "' + msg['tag'] + '" "' + msg['text'] + '"')

            if par != journal.params:
                journal.__applyparams(journal.params)

            journal.configmutex.release()

        journal.pollThread = None
