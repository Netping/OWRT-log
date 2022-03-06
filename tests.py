#!/usr/bin/python3
import os
import time
from journal import journal




def WriteLog(tag, facility, text):
    os.system('logger -p "' + facility +'" -t "' + tag + '" "' + text + '"')

if __name__ == "__main__":
    configname = 'journalconf'

    os.system(f"echo -n \"\" > /test_log.txt")

    #os.system(f"uci set journalconf.Settings.log_file=/test_log.txt")
    #os.system(f"uci set journalconf.Settings.log_type=file")
    #os.system(f"uci commit journalconf")

    time.sleep(3)

    for i in range(0, 10):
        journal.WriteLog("Notifications", "Normal", "notice", "Test message! " + str(i + 1))
        #WriteLog("Notifications", "notice", "Test message! " + str(i + 1))

    #time.sleep(5)

    #os.system(f"uci set system.@system[0].log_file=''")
    #os.system(f"uci set system.@system[0].log_type=circular")
    #os.system(f"uci commit system")
    #time.sleep(1)

    #for i in range(0, 10):
        #journal.WriteLog("Notifications", "Normal", "notice", "New 2 Test message! " + str(i + 1))
    #    WriteLog("Notifications", "notice", "New 2 Test message! " + str(i + 1))
