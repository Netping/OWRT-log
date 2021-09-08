#/usr/bin/python3

from journal import journal


def main():
    journal.WriteLog("Test", "DEBUG", "notice", "Hello world!")

if __name__ == "__main__":
    main()
