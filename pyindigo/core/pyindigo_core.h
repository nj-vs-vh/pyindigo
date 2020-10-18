// developed by Igor Vaiman, SINP MSU

#include <stdio.h>

void process_ccd_shot_with_python_callback(const void *start, size_t size);

void device_defined_callback(char* device_name);

void device_connected_callback(char* device_name);

void device_disconnected_callback(char* device_name);
