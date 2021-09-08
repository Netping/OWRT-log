SECTION="NetPing modules"
CATEGORY="Base"
TITLE="EPIC4 OWRT_Log"

PKG_NAME="OWRT_Log"
PKG_VERSION="Epic4.V1.S1"
PKG_RELEASE=4

MODULE_FILES=journal.py
MODULE_FILES_DIR=/usr/lib/python3.7/

ETC_FILES=hash
ETC_FILES_DIR=/etc/netping_log/


.PHONY: all install

all: install
	
install:
	for f in $(MODULE_FILES); do cp $${f} $(MODULE_FILES_DIR); done
	mkdir $(ETC_FILES_DIR)
	for f in $(ETC_FILES); do cp etc/$${f} $(ETC_FILES_DIR); done
clean:
	for f in $(MODULE_FILES); do rm -f $(MODULE_FILES_DIR)$${f}; done
	rm -rf $(ETC_FILES_DIR)
