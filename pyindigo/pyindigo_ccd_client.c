// indigo client intended to be wrapped in a Python class
// based largely on client examples provided by INDIGO team:
// https://github.com/indigo-astronomy/indigo/tree/master/indigo_examples

// developed on 07/09/20 by Igor Vaiman, SINP MSU, as part of TAIGA experiment

// Original copyright:

// Copyright (c) 2020 CloudMakers, s. r. o. & Rumen G.Bogdanovski
// All rights reserved.
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

static bool device_connected = false;

char *ccd_device_name;

static indigo_result ccd_client_attach(indigo_client *client) {
	indigo_log("attached to INDIGO bus...");
	indigo_enumerate_properties(client, &INDIGO_ALL_PROPERTIES);
	return INDIGO_OK;
}

static indigo_result ccd_client_define_property(indigo_client *client, indigo_device *device, indigo_property *property, const char *message) {
	if (strcmp(property->device, ccd_device_name))
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


void (*ccd_image_processing_callback)(const void *start, size_t size);


void set_ccd_image_processing_callback(void (*callback)(const void *start, size_t size))
{
	ccd_image_processing_callback = callback;
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
			// FILE *f = fopen("test_img.fits", "wb");
			// fwrite(property->items[0].blob.value, property->items[0].blob.size, 1, f);
			// fclose(f);
			ccd_image_processing_callback(property->items[0].blob.value, property->items[0].blob.size);
			indigo_log("image saved!");
		}
	}
	// if (!strcmp(property->name, CCD_EXPOSURE_PROPERTY_NAME)) {
	// 	if (property->state == INDIGO_BUSY_STATE) {
	// 		indigo_log("exposure %gs...", property->items[0].number.value);
	// 	} else if (property->state == INDIGO_OK_STATE) {
	// 		indigo_log("exposure done...");
	// 	}

	// 	return INDIGO_OK;
	// }
	return INDIGO_OK;
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
