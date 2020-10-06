DEBUG_BUILD = -g
INDIGO_ROOT = /home/njvh/Documents/Science/sphere/camera-server/indigo
BUILD_ROOT = $(INDIGO_ROOT)/build
BUILD_LIB = $(BUILD_ROOT)/lib


CFLAGS = $(DEBUG_BUILD) -O3 -I$(INDIGO_ROOT)/indigo_libs -I$(INDIGO_ROOT)/indigo_libs -std=gnu11 -DINDIGO_LINUX
LDFLAGS = -L$(BUILD_LIB) -lindigo


all: | build_object_file create_shared_library


TEMP_O_FILE = ./bin/pyindigo_ccd_client.o

# mkdir bin && cd bin && mkdir shared && cd ..

# delete -c ???
build_object_file: pyindigo_ccd_client.c
	gcc -c -fPIC $^ -o ${TEMP_O_FILE} $(CFLAGS) $(LDFLAGS)

create_shared_library:
	gcc -shared ${TEMP_O_FILE} -o ./bin/shared/libpyindigo_ccd_client.so
