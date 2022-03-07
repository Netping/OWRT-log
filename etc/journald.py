import os
import ubus
import time
from threading import Thread
from threading import Lock




params = {}
task_list = []
pollThread = None
mutex = Lock()

def init():
    params['log_ip'] = ''
    params['log_port'] = '514'
    params['log_proto'] = 'udp'
    params['log_file'] = ''
    params['log_remote'] = '0'
    params['log_size'] = '64'
    params['log_type'] = 'circular'

    def get_params_callback(event, data):
        event.reply(params)

    def set_params_callback(event, data):
        ret = { 'status' : '0' }

        #set params and restart log service
        params['log_ip'] = data['log_ip']
        params['log_port'] = data['log_port']
        params['log_proto'] = data['log_proto']
        params['log_file'] = data['log_file']
        params['log_remote'] = data['log_remote']
        params['log_size'] = data['log_size']
        params['log_type'] = data['log_type']

        ubus.call("uci", "set", {"config" : "system", "type" : "system", "values" : params})
        ubus.call("uci", "commit", {"config" : "system"})

        event.reply(ret)

    def add_task_callback(event, data):
        ret = { 'status' : '0' }

        mutex.acquire()
        task_list.insert(0, data)
        mutex.release()

        event.reply(ret)

    ubus.add(
            'owrt_log', {
                'get_params': {
                    'method': get_params_callback,
                    'signature': {
                        'ubus_rpc_session' : ubus.BLOBMSG_TYPE_STRING
                    }
                },

                'set_params': {
                    'method': set_params_callback,
                    'signature': {
                        'log_ip' : ubus.BLOBMSG_TYPE_STRING,
                        'log_port' : ubus.BLOBMSG_TYPE_STRING,
                        'log_proto' : ubus.BLOBMSG_TYPE_STRING,
                        'log_file' : ubus.BLOBMSG_TYPE_STRING,
                        'log_remote' : ubus.BLOBMSG_TYPE_STRING,
                        'log_size' : ubus.BLOBMSG_TYPE_STRING,
                        'log_type' : ubus.BLOBMSG_TYPE_STRING,
                        'ubus_rpc_session' : ubus.BLOBMSG_TYPE_STRING
                    }
                },

                'add_task' : {
                    'method': add_task_callback,
                    'signature': {
                        'text' : ubus.BLOBMSG_TYPE_STRING,
                        'tag' : ubus.BLOBMSG_TYPE_STRING,
                        'facility' : ubus.BLOBMSG_TYPE_STRING,
                        'ubus_rpc_session' : ubus.BLOBMSG_TYPE_STRING
                    }
                }
            }
        )

def commit_callback(event, data):
    if data['config'] == 'system':
        #new paramters
        confvalues = ubus.call("uci", "get", {"config": "system"})
        for confdict in list(confvalues[0]['values'].values()):
            if confdict['.type'] == 'system':
                try:
                    if confdict['log_ip']:
                        params['log_ip'] = confdict['log_ip']
                except:
                    pass

                try:
                    if confdict['log_port']:
                        params['log_port'] = confdict['log_port']
                except:
                    pass

                try:
                    if confdict['log_proto']:
                        params['log_proto'] = confdict['log_proto']
                except:
                    pass
                                
                try:
                    if confdict['log_file']:
                        params['log_file'] = confdict['log_file']
                except:
                    pass

                try:
                    if confdict['log_remote']:
                        params['log_remote'] = confdict['log_remote']
                except:
                    pass

                try:
                    if confdict['log_size']:
                        params['log_size'] = confdict['log_size']
                except:
                    pass

                try:
                    if confdict['log_type']:
                        params['log_type'] = confdict['log_type']
                except:
                    pass

        #restart log and system services
        os.system(f"/etc/init.d/log restart")
        os.system(f"/etc/init.d/system restart")

        mutex.acquire()
        time.sleep(1) #block mutex in 1 second for applying config parameters (else some log records may be not writen)
        mutex.release()

def poll():
    while task_list:
        mutex.acquire()

        msg = task_list.pop()
        mutex.release()

        #log message
        os.system('logger -p "' + msg['facility'] +'" -t "' + msg['tag'] + '" "' + msg['text'] + '"')

if __name__ == '__main__':
    try:
        ubus.connect()

        init()

        ubus.listen(("commit", commit_callback))

        while True:
            poll()
            ubus.loop(1)

    except KeyboardInterrupt:
        ubus.disconnect()
