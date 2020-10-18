// Python module wrapping INDIGO functionality

// developed by Igor Vaiman, SINP MSU

#define PY_SSIZE_T_CLEAN
#include "python3.8/Python.h"

#include <pthread.h>

#include <indigo/indigo_bus.h>
#include <indigo/indigo_client.h>

#include "pyindigo_client.h"

struct indigo_driver_entry *driver;  // typedef is not recognized by linter for some reason

PyObject* pyindigo_IndigoException;


static PyObject*
version(PyObject* self)
{
    return Py_BuildValue("s", "0.1.0");
}


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
setup_indigo_client(PyObject* self, PyObject* args)
{
    int verbosity = 0;
    if (!PyArg_ParseTuple(args, "|i", &verbosity))
        return NULL;
    set_indigo_log_level_from_verbosity(verbosity);
    indigo_start();
    indigo_attach_client(&pyindigo_client);
    Py_RETURN_NONE;
}


static PyObject*
cleanup_indigo_client(PyObject* self)
{
	indigo_detach_client(&pyindigo_client);
	indigo_stop();
    Py_RETURN_NONE;
}


static PyObject *device_defined_python_callback = NULL;

void device_defined_callback(char* device_name) {
    printf("%s (%s)\n", "before ensuring GIL...", __FUNCTION__);
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    printf("%s (%s)\n", "GIL ensured!", __FUNCTION__);
    PyObject *result;
    result = PyObject_CallFunction(device_defined_python_callback, "s", device_name);
    Py_XDECREF(result);
    PyGILState_Release(gstate);
    printf("%s (%s)\n", "GIL released!", __FUNCTION__);
}

static PyObject *device_connected_python_callback = NULL;

void device_connected_callback(char* device_name) {
    printf("%s (%s)\n", "before ensuring GIL...", __FUNCTION__);
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    printf("%s (%s)\n", "GIL ensured!", __FUNCTION__);
    PyObject *result;
    result = PyObject_CallFunction(device_connected_python_callback, "s", device_name);
    Py_XDECREF(result);
    PyGILState_Release(gstate);
    printf("%s (%s)\n", "GIL released!", __FUNCTION__);
}

static PyObject *device_disconnected_python_callback = NULL;

void device_disconnected_callback(char* device_name) {
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    PyObject *result;
    result = PyObject_CallFunction(device_disconnected_python_callback, "s", device_name);
    Py_XDECREF(result);
    PyGILState_Release(gstate);
}

static PyObject*
attach_indigo_driver(PyObject* self, PyObject* args) {
    char* driver_lib_name;
    if (!PyArg_ParseTuple(
        args, "sOOO", &driver_lib_name,
        &device_defined_python_callback,
        &device_connected_python_callback,
        &device_disconnected_python_callback
    ))
        return NULL;
    
    if (
        !PyCallable_Check(device_defined_python_callback) ||
        !PyCallable_Check(device_connected_python_callback) ||
        !PyCallable_Check(device_disconnected_python_callback)
    ) {
        PyErr_SetString(PyExc_TypeError, "All callbacks must be a Python callables!");
        return NULL;
    }
    Py_INCREF(device_defined_python_callback);
    Py_INCREF(device_connected_python_callback);
    Py_INCREF(device_disconnected_python_callback);

    if (indigo_load_driver(driver_lib_name, true, &driver) != INDIGO_OK)
        return PyErr_Format(PyExc_ValueError, "Unable to load requested driver \"%s\"", driver_lib_name);

    Py_RETURN_NONE;
}


static PyObject*
detach_indigo_driver(PyObject* self)
{
    indigo_remove_driver(driver);
    Py_RETURN_NONE;
}


static PyObject*
disconnect_indigo_device(PyObject* self, PyObject* args) {
    char* device_name;
    if (!PyArg_ParseTuple(args, "s", &device_name)) return NULL;
	indigo_device_disconnect(&pyindigo_client, device_name);
    Py_RETURN_NONE;
}


static PyObject *shot_processing_callback = NULL;

void process_ccd_shot_with_python_callback(const void *buffer, size_t size)
{
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    PyObject *result;
    result = PyObject_CallFunction(shot_processing_callback, "y#", buffer, (Py_ssize_t)size);
    Py_XDECREF(result);  // XDECREF ignores NULL — i.e. error in Python callback
    PyGILState_Release(gstate);
}

static PyObject*
set_shot_processing_callback(PyObject* self, PyObject* args)
{
    PyObject *new_callback = NULL;
    if (!PyArg_ParseTuple(args, "O", &new_callback))
        return NULL;
    
    if (!PyCallable_Check(new_callback)) {
        PyErr_SetString(PyExc_TypeError, "Callback must be a Python callable!");
        return NULL;
    }
    Py_XINCREF(new_callback);
    Py_XDECREF(shot_processing_callback);
    shot_processing_callback = new_callback;
    Py_RETURN_NONE;
}


static PyObject*
take_shot_with_ccd(PyObject* self, PyObject* args)
{
    float exposure;
    char* device_name;
    if (!PyArg_ParseTuple(args, "fs", &exposure, &device_name))
        return NULL;
    if (!shot_processing_callback) {
        return PyErr_Format(
            PyExc_ValueError,
            "No callback is stored, you must call set_shot_processing_callback at least once!"
        );
    }
    const char * items[] = { CCD_EXPOSURE_ITEM_NAME };
    double values[1] = { exposure };
    indigo_change_number_property(&pyindigo_client, device_name, CCD_EXPOSURE_PROPERTY_NAME, 1, items, values);
    Py_RETURN_NONE;
}


static PyObject*
set_gain(PyObject* self, PyObject* args)
{
    float gain;
    char* device_name;
    if (!PyArg_ParseTuple(args, "fs", &gain, &device_name))
        return NULL;
    const char * items[] = { CCD_GAIN_ITEM_NAME };
    double values[1] = { gain };
    indigo_change_number_property(&pyindigo_client, device_name, CCD_GAIN_PROPERTY_NAME, 1, items, values);
    Py_RETURN_NONE;
}


// Python module definitions


static PyMethodDef methods[] = {
    {"version", (PyCFunction)version, METH_NOARGS, "pyindigo core version"},
    // client-level functions (used once per module)
    {"setup_indigo_client", (PyCFunction)setup_indigo_client, METH_VARARGS, "must be used at first"},
    {"cleanup_indigo_client", (PyCFunction)cleanup_indigo_client, METH_NOARGS, "must be used at last"},
    // driver-level fuctions (may be used to communicate to several drivers in the future)
    {"attach_indigo_driver", (PyCFunction)attach_indigo_driver, METH_VARARGS, "ASYNC driver initialization function"},
    {"detach_indigo_driver", (PyCFunction)detach_indigo_driver, METH_NOARGS, "must be called after all devices are disconnected"},
    // device-level functions — one driver can have several devices
    // there's no "connect_indigo_device'"function, all devices are connected automatically as they are available
    {"disconnect_indigo_device", (PyCFunction)disconnect_indigo_device, METH_VARARGS, "ASYNC device disconnect function"},
    {"set_shot_processing_callback", (PyCFunction)set_shot_processing_callback, METH_VARARGS, "store new callback"},
    {"take_shot_with_exposure", (PyCFunction)take_shot_with_ccd, METH_VARARGS, "ASYNC set exposure and callback to process the result"},
    {"set_gain", (PyCFunction)set_gain, METH_VARARGS, "set CCD device gain"},
    {NULL, NULL, 0, NULL}  /* Sentinel */
};

static struct PyModuleDef _pyindigo = {
    PyModuleDef_HEAD_INIT,
    "_pyindigo",
    "Python interface to INDIGO operations. Used by wrapper Python code and should not be imported directly!",
    -1,
    methods
};

PyMODINIT_FUNC PyInit__pyindigo(void)
{
    pyindigo_IndigoException = PyErr_NewException("pyindigo.IndigoException", NULL, NULL);
    return PyModule_Create(&_pyindigo);
}
