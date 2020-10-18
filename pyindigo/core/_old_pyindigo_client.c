// indigo client intended to be wrapped in a Python module

// TODO: more general dispatching off callbacks to allow general-purpose interface
// this will likely require storing C-string -> C-function mapping

// developed by Igor Vaiman, SINP MSU

// Original copyright:
//
// You can use this software under the terms of 'INDIGO Astronomy
// open-source license' (see LICENSE.md).
//
// THIS SOFTWARE IS PROVIDED BY THE AUTHORS 'AS IS' AND ANY EXPRESS
// OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
// WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
// ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
// DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
// DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
// GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
// INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
// WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
// NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
// SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <indigo/indigo_bus.h>
#include <indigo/indigo_client.h>

#include "pyindigo_core.h"


static indigo_result pyindigo_client_attach(indigo_client *client) {
	indigo_log("attached to INDIGO bus...");
	indigo_enumerate_properties(client, &INDIGO_ALL_PROPERTIES);
	return INDIGO_OK;
}

static indigo_result pyindigo_client_define_property(indigo_client *client, indigo_device *device, indigo_property *property, const char *message) {
	// if we are ale to connect to the device, try to do so
	if (!strcmp(property->name, CONNECTION_PROPERTY_NAME)) {
		if (indigo_get_switch(property, CONNECTION_DISCONNECTED_ITEM_NAME)) {
			device_defined_callback(property->device);
			indigo_device_connect(client, property->device);
			return INDIGO_OK;
		}
	}
	// no external config is used, all properties are expected to be set explicitly from Python
	if (!strcmp(property->name, CONFIG_PROPERTY_NAME)) {
		static const char * items[] = { CONFIG_LOAD_ITEM_NAME, CONFIG_SAVE_ITEM_NAME, CONFIG_REMOVE_ITEM_NAME };
		static bool values[] = { false, true, false };
		indigo_change_switch_property(client, property->device, CONFIG_PROPERTY_NAME, 3, items, values);
	}
	// always use blobs as we are operationg locally
	if (!strcmp(property->name, CCD_IMAGE_PROPERTY_NAME)) {
		if (device->version >= INDIGO_VERSION_2_0)
			indigo_enable_blob(client, property, INDIGO_ENABLE_BLOB_URL);
		else
			indigo_enable_blob(client, property, INDIGO_ENABLE_BLOB_ALSO);
	}
	// always use fits if the device allows so
	if (!strcmp(property->name, CCD_IMAGE_FORMAT_PROPERTY_NAME)) {
		static const char * items[] = { CCD_IMAGE_FORMAT_FITS_ITEM_NAME };
		static bool values[] = { true };
		indigo_change_switch_property(client, property->device, CCD_IMAGE_FORMAT_PROPERTY_NAME, 1, items, values);
	}
	return INDIGO_OK;
}


static indigo_result pyindigo_client_update_property(indigo_client *client, indigo_device *device, indigo_property *property, const char *message) {
	if (!strcmp(property->name, CONNECTION_PROPERTY_NAME) && property->state == INDIGO_OK_STATE) {
		if (indigo_get_switch(property, CONNECTION_CONNECTED_ITEM_NAME)) {
			indigo_log("connected...");
			device_connected_callback(property->device);
		} else {
			indigo_log("disconnected...");
			device_disconnected_callback(property->device);
		}
		return INDIGO_OK;
	}
	if (!strcmp(property->name, CCD_IMAGE_PROPERTY_NAME) && property->state == INDIGO_OK_STATE) {
		if (property->items[0].blob.value) {
			process_ccd_shot_with_python_callback(property->items[0].blob.value, property->items[0].blob.size);
		}
		return INDIGO_OK;
	}
}

static indigo_result pyindigo_client_detach(indigo_client *client) {
	indigo_log("detached from INDIGO bus...");
	return INDIGO_OK;
}

indigo_client pyindigo_client = {
	"CCD client", false, NULL, INDIGO_OK, INDIGO_VERSION_CURRENT, NULL,
	pyindigo_client_attach,
	pyindigo_client_define_property,
	pyindigo_client_update_property,
	NULL,
	NULL,
	pyindigo_client_detach
};
