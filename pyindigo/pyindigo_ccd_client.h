// developed on 07/09/20 by Igor Vaiman, SINP MSU, as part of TAIGA experiment

#include <indigo/indigo_client.h>

extern char *ccd_device_name;

extern indigo_client ccd_client;

void set_ccd_image_processing_callback(void (*callback)(const void *start, size_t size));
