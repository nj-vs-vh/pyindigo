// indigo client intended to be wrapped in a Python class
// based largely on client examples provided by INDIGO team:
// https://github.com/indigo-astronomy/indigo/tree/master/indigo_examples

// TODO: more general dispatching off callbacks to allow general-purpose interface
// this will likely require storing C-string -> C-function mapping

// developed by Igor Vaiman, SINP MSU, as part of TAIGA experiment

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

#include "_pyindigo.h"

char* ccd_device_name;
static bool device_connected = false;

static indigo_result ccd_client_attach(indigo_client *client) {
	indigo_log("attached to INDIGO bus...");
	indigo_enumerate_properties(client, &INDIGO_ALL_PROPERTIES);
	return INDIGO_OK;
}

static indigo_result ccd_client_define_property(indigo_client *client, indigo_device *device, indigo_property *property, const char *message) {
	if (strcmp(property->device, ccd_device_name))
		// anything but our dedicated ccd_device_name is ignored
		return INDIGO_OK;
	if (!strcmp(property->name, CONNECTION_PROPERTY_NAME)) {
		if (indigo_get_switch(property, CONNECTION_CONNECTED_ITEM_NAME)) {
			device_connected = true;
			indigo_log("already connected...");
		} else {
			indigo_device_connect(client, ccd_device_name);
			return INDIGO_OK;
		}
	}
	if (!strcmp(property->name, CCD_IMAGE_PROPERTY_NAME)) {
		if (device->version >= INDIGO_VERSION_2_0)
			indigo_enable_blob(client, property, INDIGO_ENABLE_BLOB_URL);
		else
			indigo_enable_blob(client, property, INDIGO_ENABLE_BLOB_ALSO);
	}
	if (!strcmp(property->name, CCD_IMAGE_FORMAT_PROPERTY_NAME)) {
		static const char * items[] = { CCD_IMAGE_FORMAT_FITS_ITEM_NAME };
		static bool values[] = { true };
		indigo_change_switch_property(client, ccd_device_name, CCD_IMAGE_FORMAT_PROPERTY_NAME, 1, items, values);
	}
	return INDIGO_OK;
}


static indigo_result ccd_client_update_property(indigo_client *client, indigo_device *device, indigo_property *property, const char *message) {
	if (strcmp(property->device, ccd_device_name))
		return INDIGO_OK;
	if (!strcmp(property->name, CONNECTION_PROPERTY_NAME) && property->state == INDIGO_OK_STATE) {
		if (indigo_get_switch(property, CONNECTION_CONNECTED_ITEM_NAME)) {
			if (!device_connected) {
				device_connected = true;
				indigo_log("connected...");
			}
		} else {
			if (device_connected) {
				indigo_log("disconnected...");
				device_connected = false;
			}
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

static indigo_result ccd_client_detach(indigo_client *client) {
	indigo_log("detached from INDIGO bus...");
	return INDIGO_OK;
}

indigo_client ccd_client = {
	"CCD client", false, NULL, INDIGO_OK, INDIGO_VERSION_CURRENT, NULL,
	ccd_client_attach,
	ccd_client_define_property,
	ccd_client_update_property,
	NULL,
	NULL,
	ccd_client_detach
};
