BINDIR= ./bin

${BINDIR}:
	mkdir -p ${BINDIR}


INDIGO_DEBUG_BUILD = -g
INDIGO_LIB_DIR = /usr/local/lib

CFLAGS = $(INDIGO_DEBUG_BUILD) -O3 -std=gnu11 -DINDIGO_LINUX
LDFLAGS = -L$(INDIGO_LIB_DIR) -lindigo

PYINDIGO_CLIENT_OBJECT = ${BINDIR}/pyindigo_client.o
PYINDIGO_CLIENT_LIB = ${BINDIR}/libpyindigo_client.so

${PYINDIGO_CLIENT_OBJECT}: pyindigo_client.c | ${BINDIR}
	gcc -c -fPIC $< -o $@ $(CFLAGS)

${PYINDIGO_CLIENT_LIB}: ${PYINDIGO_CLIENT_OBJECT} | ${BINDIR}
	gcc -shared $< -o $@ $(CFLAGS) ${LDFLAGS}


.PHONY: install clean reinstall

install: ${PYINDIGO_CLIENT_LIB}
	@sudo cp ${PYINDIGO_CLIENT_LIB} ${INDIGO_LIB_DIR}

ISTALLED_PYINDIGO_CLIENT_LIB = ${INDIGO_LIB_DIR}/$(notdir ${PYINDIGO_CLIENT_LIB})

clean:
	@sudo rm -rf ${BINDIR} ${ISTALLED_PYINDIGO_CLIENT_LIB}

reinstall: clean | install
