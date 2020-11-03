// INDIGO client to be wrapped in a Python modulem

// developed by Igor Vaiman, SINP MSU


#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <indigo/indigo_bus.h>
#include <indigo/indigo_client.h>

#include "pyindigo_core.h"


#define PYINDIGO_DEFINE_ACTION "define"
#define PYINDIGO_UPDATE_ACTION "update"
#define PYINDIGO_DELETE_ACTION "delete"


static indigo_result pyindigo_client_attach(indigo_client *client)
{
	indigo_log("attached to INDIGO bus...");
	indigo_enumerate_properties(client, &INDIGO_ALL_PROPERTIES);
	return INDIGO_OK;
}

static indigo_result pyindigo_client_define_property(indigo_client *client, indigo_device *device, indigo_property *property, const char *message) {
	call_dispatching_callback(PYINDIGO_DEFINE_ACTION, device, property, message);
	return INDIGO_OK;
}


static indigo_result pyindigo_client_update_property(indigo_client *client, indigo_device *device, indigo_property *property, const char *message) {
	call_dispatching_callback(PYINDIGO_UPDATE_ACTION, device, property, message);
	return INDIGO_OK;
}

static indigo_result pyindigo_client_delete_property(indigo_client *client, indigo_device *device, indigo_property *property, const char *message) {
	call_dispatching_callback(PYINDIGO_DELETE_ACTION, device, property, message);
	return INDIGO_OK;
}

static indigo_result pyindigo_client_send_message(indigo_client *client, indigo_device *device, const char *message) {
	return INDIGO_OK;
}

static indigo_result pyindigo_client_detach(indigo_client *client) {
	indigo_log("detached from INDIGO bus...");
	return INDIGO_OK;
}

indigo_client pyindigo_client = {
	"Pyindigo client", false, NULL, INDIGO_OK, INDIGO_VERSION_CURRENT, NULL,
	pyindigo_client_attach,
	pyindigo_client_define_property,
	pyindigo_client_update_property,
	pyindigo_client_delete_property,
	pyindigo_client_send_message,
	pyindigo_client_detach
};
