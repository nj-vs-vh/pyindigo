# indigo compilation stuff

INDIGO_DEBUG_BUILD = -g
INDIGO_ROOT = ../indigo
INDIGO_LIB_DIR = $(INDIGO_ROOT)/build/lib

CFLAGS = $(INDIGO_DEBUG_BUILD) -O3 -I$(INDIGO_ROOT)/indigo_libs -std=gnu11 -DINDIGO_LINUX
LDFLAGS = -L$(INDIGO_LIB_DIR) -lindigo

INDIGO_SONAME = libindigo.so  # used later


# prepare directory for compiled files (added as an order only prerequisite)

BINDIR= ./bin

${BINDIR}:
	mkdir -p ${BINDIR}


# ccd client shared library building

CCD_CLIENT_OBJECT = ${BINDIR}/pyindigo_ccd_client.o
CCD_CLIENT_LIB = ${BINDIR}/libpyindigo_ccd_client.so


${CCD_CLIENT_OBJECT}: pyindigo_ccd_client.c | ${BINDIR}
	gcc -c -fPIC $< -o $@ $(CFLAGS)


${CCD_CLIENT_LIB}: ${CCD_CLIENT_OBJECT} | ${BINDIR}
	gcc -shared $< -o $@


# python extension building and installation to virtual environment

INDIGO_VENV_NAME = indgenv
INDIGO_VENV_PATH = ../${INDIGO_VENV_NAME}

${INDIGO_VENV_PATH}:
	cd ..
	python3 -m venv ${INDIGO_VENV_NAME}
	bash -c ". ${INDIGO_VENV_NAME}/bin/activate;"
	pip3 install -r requirements.txt
	cd pyindigo


PYTHON_INSTALLATION_LOG = setup_py_installation_log.txt

activate_python_virtual_environment:
	bash -c ". ../${INDIGO_VENV_NAME}/bin/activate;"

python_extension: ${INDIGO_VENV_PATH} activate_python_virtual_environment
	python3 setup.py install --record ${PYTHON_INSTALLATION_LOG}


# commands

.PHONY: install clean

install: ${CCD_CLIENT_LIB} python_extension
	cp ${CCD_CLIENT_LIB} ${INDIGO_LIB_DIR}
	echo "Make sure LD_LIBRARY_PATH env variable includes:"
	echo $(realpath ${INDIGO_LIB_DIR})

ISTALLED_CCD_CLIENT_LIB = ${INDIGO_LIB_DIR}/$(notdir ${CCD_CLIENT_LIB})

clean:
	chmod +x setup_py_uninstall && \
	./setup_py_uninstall ${PYTHON_INSTALLATION_LOG} && \
	rm -rf ${BINDIR} build ${PYTHON_INSTALLATION_LOG} ${ISTALLED_CCD_CLIENT_LIB}
