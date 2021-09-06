#/usr/bin/python3

from journal import *


def main():
    j = journal()
    j.WriteLog("Test", "DEBUG", "notice", "Hello world!")

if __name__ == "__main__":
    main()
