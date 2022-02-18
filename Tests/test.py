#!/usr/bin/python3
import os
import ubus
import time

# config info
configpath = '/etc/config/'
configname = 'journalconf'
config_params_test = {'Settings': ['log_ip', 'log_port', 'log_proto', 'log_remote', 'log_size', 'log_type']}
config_params_test['Settings'].sort()

# for test python methods
from journal import journal

def test_config_existance():
    ret = False
    try:
        if os.path.isfile(f"{configpath}{configname}"):
            ret = True
    except:
        assert ret
    assert ret

def test_config_params():
    ret = False
    config_params = {}
    print("\n")
    try:
        ubus.connect()
    except:
        pass

    try:
        confvalues = ubus.call("uci", "get", {"config": configname})
        for confdict in list(confvalues[0]['values'].values()):
            if confdict['.type'] == 'info':
                config_params = {}
                if confdict['.name'] in config_params_test:
                    config_params[confdict['.name']] = []
                    for option in confdict:
                        if not option.startswith('.'):
                            if option in config_params_test[confdict['.name']]:
                                config_params[confdict['.name']].append(option)
                            else:
                                print("---WARNING---: Unknown option \"" + option + "\" in section \"" + confdict['.name'] + "\" in config file")
                    config_params[confdict['.name']].sort()
                else:
                    print("---WARNING---: Unknown section \"" + confdict['.name'] + "\" in config file")
                    continue
            assert config_params_test == config_params
    except:
        assert ret

    try:
        ubus.disconnect()
    except:
        pass

def test_python_writelog_method():
    ret = False
    try:
        journal.WriteLog("Notifications", "Normal", "notice", "Config changed!")
        out = os.popen('logread -e Notifications').read()
        if not out == "":
            ret = True
        assert ret

        # for log to file
        ret = False
        os.system(f"uci set {configname}.Settings.log_file=/test_log.txt")
        os.system(f"uci set {configname}.Settings.log_type=file")
        os.system(f"uci commit {configname}")
        time.sleep(1)
        try:
            ubus.connect()
        except:
            pass
        log_file = ubus.call("uci", "get", {"config": configname, "section": "Settings", "option": "log_file"})
        if log_file:
            log_file = log_file[0]['value']
        log_type = ubus.call("uci", "get", {"config": configname, "section": "Settings", "option": "log_type"})[0]['value']
        try:
            ubus.disconnect()
        except:
            pass
        if log_type == 'file' and log_file:
            print("\nclear logfile if exists...")
            if os.path.exists(log_file):
                os.system(f"cat /dev/null > {log_file}")
            print("run first WriteLog, waiting...")
            journal.WriteLog("Notifications", "Normal", "notice", "Config changed!")
            time.sleep(5)
            print("run second WriteLog, waiting...")
            journal.WriteLog("Notifications", "Normal", "notice", "Config changed!")
            time.sleep(5)
            with open(log_file, "r") as f:
                logline = f.read()
                if "Notifications" in logline:
                    ret = True
        assert ret

        os.system(f"uci set {configname}.Settings.log_file=''")
        os.system(f"uci set {configname}.Settings.log_type=circular")
        os.system(f"uci commit {configname}")
        time.sleep(1)
        journal.WriteLog("Notifications", "Normal", "notice", "Config changed!")
        if os.path.exists(log_file):
            os.remove(log_file)

    except:
        assert ret

