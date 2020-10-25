// INDIGO client to be wrapped in a Python module

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


static indigo_result pyindigo_client_attach(indigo_client *client)
{
	indigo_log("attached to INDIGO bus...");
	indigo_enumerate_properties(client, &INDIGO_ALL_PROPERTIES);
	return INDIGO_OK;
}

static indigo_result pyindigo_client_define_property(indigo_client *client, indigo_device *device, indigo_property *property, const char *message) {
	call_dispatching_callback("define", property, message);
	return INDIGO_OK;
}


static indigo_result pyindigo_client_update_property(indigo_client *client, indigo_device *device, indigo_property *property, const char *message) {
	call_dispatching_callback("update", property, message);
	return INDIGO_OK;
}

static indigo_result pyindigo_client_delete_property(indigo_client *client, indigo_device *device, indigo_property *property, const char *message) {
	call_dispatching_callback("delete", property, message);
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
