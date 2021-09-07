#/usr/bin/python3

from journal import journal


def main():
    journal.WriteLog("Test", "DEBUG", "notice", "Hello world!")
    #for i in range(1, 10):
    #    journal.WriteLog("Test", "DEBUG", "notice", "Loop! " + str(i))

if __name__ == "__main__":
    main()
