// Python module with bindings to INDIGO function calls

// developed by Igor Vaiman, SINP MSU

#define PY_SSIZE_T_CLEAN
#include "Python.h"

#include <pthread.h>

#include <indigo/indigo_bus.h>
#include <indigo/indigo_client.h>
#include <indigo/indigo_version.h>

#include "pyindigo_client.h"


// temporaryly working with only one driver!
// TODO: dynamic list of driver pointers with Python objects storing indices (IDs)
//       letting Python user load and delete drivers as they please
struct indigo_driver_entry *driver;


// client-level functions


indigo_log_levels CURRENT_INDIGO_LOG_LEVEL;

void set_indigo_log_level_from_verbosity(int verbosity) {
    switch (verbosity) {
        case 1: CURRENT_INDIGO_LOG_LEVEL = INDIGO_LOG_INFO; break;
        case 2: CURRENT_INDIGO_LOG_LEVEL = INDIGO_LOG_DEBUG; break;
        case 3: CURRENT_INDIGO_LOG_LEVEL = INDIGO_LOG_TRACE; break;
        default: CURRENT_INDIGO_LOG_LEVEL = INDIGO_LOG_ERROR; break;
    }
    indigo_set_log_level(CURRENT_INDIGO_LOG_LEVEL);
}


static PyObject*
setup_client(PyObject* self)
{
    set_indigo_log_level_from_verbosity(0);
    indigo_start();
    indigo_attach_client(&pyindigo_client);
    Py_RETURN_NONE;
}


static PyObject*
cleanup_client(PyObject* self)
{
	indigo_detach_client(&pyindigo_client);
	indigo_stop();
    Py_RETURN_NONE;
}


static PyObject*
set_log_level(PyObject* self, PyObject* args)
{
    int verbosity = 0;
    if (!PyArg_ParseTuple(args, "i", &verbosity))
        return NULL;
    set_indigo_log_level_from_verbosity(verbosity);
    Py_RETURN_NONE;
}


// Indigo properties modelled with Python classes
// see src/properties/base_classes.py for base class definition

static PyObject *text_vector_class = NULL;
static PyObject *number_vector_class = NULL;
static PyObject *switch_vector_class = NULL;
static PyObject *light_vector_class = NULL;

static PyObject*
set_property_classes(PyObject* self, PyObject* args)
{
    if (
        !PyArg_ParseTuple(
            args, "OOOO",
            &text_vector_class, &number_vector_class, &switch_vector_class, &light_vector_class
        )
    )
        return NULL;
    Py_RETURN_NONE;
}


// dispatching callback is a single Python callable representing all possible INDIGO actions
// all dispatching should be done on Python side

static PyObject *dispatching_callback = NULL;

void call_dispatching_callback(const char* action_type, indigo_device *device, indigo_property* property, const char *message)
{
    assert(dispatching_callback != NULL);
    assert(property != NULL);

    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();

    PyObject* property_object = NULL;

    switch (property->type) {
        case INDIGO_TEXT_VECTOR:
            property_object = PyObject_CallFunction(text_vector_class, "ss", indigo_property_name(device->version, property), property->device);
            for (int i = 0; i < property->count; i++) {
                indigo_item *item = &property->items[i];
                PyObject_CallMethod(
                    property_object, "add_item", "ssss",
                    indigo_item_name(device->version, property, item), item->label, item->hints,
                    item->text.value
                );
            }
            break;
        case INDIGO_NUMBER_VECTOR:
            property_object = PyObject_CallFunction(number_vector_class, "ss", indigo_property_name(device->version, property), property->device);
            for (int i = 0; i < property->count; i++) {
                indigo_item *item = &property->items[i];
                PyObject_CallMethod(
                    property_object, "add_item", "ssssddddd",
                    indigo_item_name(device->version, property, item), item->label, item->hints,
                    item->number.format,
                    item->number.min,
                    item->number.max,
                    item->number.step,
                    item->number.value,
                    item->number.target
                );
            }
            break;
        case INDIGO_SWITCH_VECTOR:
            // TODO: save rule for switch vectors (i.e. one of many, many of many)
            property_object = PyObject_CallFunction(switch_vector_class, "ss", indigo_property_name(device->version, property), property->device);
            for (int i = 0; i < property->count; i++) {
                indigo_item *item = &property->items[i];
                PyObject_CallMethod(
                    property_object, "add_item", "sssi",
                    indigo_item_name(device->version, property, item), item->label, item->hints, item->sw.value
                );
            }
            break;
        case INDIGO_LIGHT_VECTOR:
            property_object = PyObject_CallFunction(light_vector_class, "ss", indigo_property_name(device->version, property), property->device);
            for (int i = 0; i < property->count; i++) {
                indigo_item *item = &property->items[i];
                PyObject_CallMethod(
                    property_object, "add_item", "sssi",
                    indigo_item_name(device->version, property, item), item->label, item->hints, item->light.value
                );
            }
            break;
        default : {}
	}

    if (property_object != NULL) {
        PyObject *result = NULL;
        result = PyObject_CallFunction(dispatching_callback, "sO", action_type, property_object);
        Py_XDECREF(result);
    }
    
    PyGILState_Release(gstate);
}

static PyObject*
set_dispatching_callback(PyObject* self, PyObject* args) {
    PyObject* new_callback;
    if (!PyArg_ParseTuple(args, "O", &new_callback))
        return NULL;
    
    if (!PyCallable_Check(new_callback)) {
        PyErr_SetString(PyExc_TypeError, "Dispatching callback must be a Python callable!");
        return NULL;
    }

    Py_INCREF(new_callback);
    Py_XDECREF(dispatching_callback);
    dispatching_callback = new_callback;

    Py_RETURN_NONE;
}


// driver-level functions


static PyObject*
attach_driver(PyObject* self, PyObject* args) {
    char* driver_lib_name;
    if (!PyArg_ParseTuple(args, "s", &driver_lib_name))
        return NULL;
    if (indigo_load_driver(driver_lib_name, true, &driver) != INDIGO_OK)
        return PyErr_Format(PyExc_ValueError, "Unable to load requested driver: \"%s\"", driver_lib_name);
    Py_RETURN_NONE;
}


static PyObject*
detach_driver(PyObject* self)
{
    indigo_remove_driver(driver);
    Py_RETURN_NONE;
}


// device-level functions


static PyObject*
disconnect_device(PyObject* self, PyObject* args) {
    char* device_name;
    if (!PyArg_ParseTuple(args, "s:device_name", &device_name)) return NULL;
	indigo_device_disconnect(&pyindigo_client, device_name);
    Py_RETURN_NONE;
}


// Python module definitions


static PyMethodDef methods[] = {
    // client-level functions (used once per module)
    {"setup_client", (PyCFunction)setup_client, METH_NOARGS, "start INDIGO bus thread and attach client"},
    {"cleanup_client", (PyCFunction)cleanup_client, METH_NOARGS, "detach client and stop INDIGO bus thread"},
    {"set_log_level", (PyCFunction)set_log_level, METH_VARARGS, "accepts verbosity as int number (0-3)"},
    {"set_property_classes", (PyCFunction)set_property_classes, METH_VARARGS, "set Python classes modelling Indigo properties"},
    // driver-level fuctions (may be used to communicate to several drivers in the future)
    {"attach_driver", (PyCFunction)attach_driver, METH_VARARGS, "request driver attachment from INDIGO bus"},
    {"detach_driver", (PyCFunction)detach_driver, METH_NOARGS, "request driver detachment from INDIGO bus"},
    {"set_dispatching_callback", (PyCFunction)set_dispatching_callback, METH_VARARGS, "set master-callback"},
    // device-level functions — one driver can have several devices
    // there's no "connect_indigo_device'"function, all devices are connected automatically as they are available
    {"disconnect_device", (PyCFunction)disconnect_device, METH_VARARGS, "request device disconnection from INDIGO bus"},
    {NULL, NULL, 0, NULL}  /* Sentinel */
};

static struct PyModuleDef pyindigo_core_ext = {
    PyModuleDef_HEAD_INIT,
    "core_ext",
    "C extension module with bindings to Indigo functions. Together with pyindigo.core form core Pyindigo functionality",
    -1,
    methods
};

PyMODINIT_FUNC PyInit_core_ext(void)
{
    return PyModule_Create(&pyindigo_core_ext);
}
