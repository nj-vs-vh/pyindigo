// Python module with bindings to INDIGO function calls

// developed by Igor Vaiman, SINP MSU

#define PY_SSIZE_T_CLEAN
#include "python3.8/Python.h"

#include <pthread.h>

#include <indigo/indigo_bus.h>
#include <indigo/indigo_client.h>

#include "pyindigo_client.h"


// temporary working with only one driver!
// TODO: dynamic array of driver pointers with Python objects storing indices (IDs)
//       letting Python user load and delete drivers as they please
struct indigo_driver_entry *driver;


// pyindigo.core version, might differ from pyindigo wrapper version
static PyObject*
version(PyObject* self)
{
    return Py_BuildValue("s", "0.1.0");
}


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


// dispatching callback is a single Python callable representing all possible INDIGO actions
// all dispatching should be done on Python side


static PyObject *dispatching_callback = NULL;

void call_dispatching_callback(const char* action_type, indigo_property* property, const char *message) {
    assert(dispatching_callback != NULL);
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    PyObject *result = NULL;
    // here Pyindigo property building should occur
    result = PyObject_CallFunction(dispatching_callback, "sss", action_type, property->device, property->name);
    Py_XDECREF(result);
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
    {"version", (PyCFunction)version, METH_NOARGS, "pyindigo.core version"},
    // client-level functions (used once per module)
    {"setup_client", (PyCFunction)setup_client, METH_NOARGS, "start INDIGO bus thread and attach client"},
    {"cleanup_client", (PyCFunction)cleanup_client, METH_NOARGS, "detach client and stop INDIGO bus thread"},
    {"set_log_level", (PyCFunction)set_log_level, METH_VARARGS, "accepts verbosity as int number (0-3)"},
    // driver-level fuctions (may be used to communicate to several drivers in the future)
    {"attach_driver", (PyCFunction)attach_driver, METH_VARARGS, "request driver attachment from INDIGO bus"},
    {"detach_driver", (PyCFunction)detach_driver, METH_NOARGS, "request driver detachment from INDIGO bus"},
    {"set_dispatching_callback", (PyCFunction)set_dispatching_callback, METH_VARARGS, "set master-callback"},
    // device-level functions — one driver can have several devices
    // there's no "connect_indigo_device'"function, all devices are connected automatically as they are available
    {"disconnect_device", (PyCFunction)disconnect_device, METH_VARARGS, "request device disconnection from INDIGO bus"},
    {NULL, NULL, 0, NULL}  /* Sentinel */
};

static struct PyModuleDef pyindigo_core = {
    PyModuleDef_HEAD_INIT,
    "core",
    "Direct bindings to INDIGO calls",
    -1,
    methods
};

PyMODINIT_FUNC PyInit_core(void)
{
    return PyModule_Create(&pyindigo_core);
}
