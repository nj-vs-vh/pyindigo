# indigo compilation stuff

INDIGO_DEBUG_BUILD = -g
INDIGO_ROOT = ../../indigo
INDIGO_LIB_DIR = $(INDIGO_ROOT)/build/lib

CFLAGS = $(INDIGO_DEBUG_BUILD) -O3 -I$(INDIGO_ROOT)/indigo_libs -std=gnu11 -DINDIGO_LINUX
LDFLAGS = -L$(INDIGO_LIB_DIR) -lindigo

INDIGO_SONAME = libindigo.so  # used later


# prepare directory for compiled files (added as an order only prerequisite)

BINDIR= ./bin

${BINDIR}:
	mkdir -p ${BINDIR}


# ccd client shared library building

PYINDIGO_CLIENT_OBJECT = ${BINDIR}/pyindigo_client.o
PYINDIGO_CLIENT_LIB = ${BINDIR}/libpyindigo_client.so

${PYINDIGO_CLIENT_OBJECT}: pyindigo_client.c | ${BINDIR}
	gcc -c -fPIC $< -o $@ $(CFLAGS)

${PYINDIGO_CLIENT_LIB}: ${PYINDIGO_CLIENT_OBJECT} | ${BINDIR}
	gcc -shared $< -o $@ $(CFLAGS) ${LDFLAGS}


# commands

.PHONY: install clean

install: ${PYINDIGO_CLIENT_LIB}
	cp ${PYINDIGO_CLIENT_LIB} ${INDIGO_LIB_DIR}
	echo $(realpath ${INDIGO_LIB_DIR})

ISTALLED_PYINDIGO_CLIENT_LIB = ${INDIGO_LIB_DIR}/$(notdir ${PYINDIGO_CLIENT_LIB})

clean:
	rm -rf ${BINDIR} ${ISTALLED_PYINDIGO_CLIENT_LIB}

reinstall: clean | install
