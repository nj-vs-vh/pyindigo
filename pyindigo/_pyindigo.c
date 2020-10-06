// Python module wrapping basic indigo functions
// extensible on demand

// developed on 07/09/20 by Igor Vaiman, SINP MSU, as part of TAIGA experiment

#define PY_SSIZE_T_CLEAN
#include "python3.8/Python.h"

#include "pyindigo_ccd_client.h"

#include <indigo/indigo_bus.h>
// #include <indigo/indigo_client.h>


char *ccd_driver_so_filename;

struct indigo_driver_entry *driver;

PyObject* pyindigo_IndigoException;


static PyObject*
version(PyObject* self)
{
    return Py_BuildValue("s", "0.0.1");
}


static PyObject*
set_ccd_driver_and_device(PyObject* self, PyObject* args)
{
    if (!PyArg_ParseTuple(args, "ss", &ccd_device_name, &ccd_driver_so_filename))
        return NULL;
    Py_RETURN_NONE;
}

static PyObject*
setup_ccd_client(PyObject* self)
{
    // indigo_set_log_level(INDIGO_LOG_INFO);
    indigo_start();
    indigo_attach_client(&ccd_client);
    if (indigo_load_driver(ccd_driver_so_filename, true, &driver) == INDIGO_OK)
    {
        set_ccd_image_processing_callback(process_ccd_shot_with_python_callback);
        Py_RETURN_NONE;
    }
    else
    {
        return PyErr_Format(PyExc_ValueError, "Unable to load requested driver \"%s\"", ccd_driver_so_filename);
    }
}


static PyObject*
cleanup_ccd_client(PyObject* self)
{
	// indigo_device_disconnect(client, ccd_device_name);
	indigo_remove_driver(driver);
	indigo_detach_client(&ccd_client);
	indigo_stop();
    Py_RETURN_NONE;
}


static PyObject *shot_processing_callback = NULL;

void process_ccd_shot_with_python_callback(const void *start, size_t size)
{
    // char (*buffer)[size] = (char (*)[size]) start;
    PyObject *arglist;
    arglist = Py_BuildValue("(y#)", start, size);
    PyObject_CallObject(shot_processing_callback, arglist);
    Py_DECREF(arglist);
}


static PyObject*
take_shot_with_ccd(PyObject* self, PyObject* args)
{
    PyObject *new_callback = NULL;
    float exposure;
    if (!PyArg_ParseTuple(args, "f|O", &exposure, &new_callback))
        return NULL;
    
    if (new_callback) {
        if (!PyCallable_Check(new_callback)) {
            PyErr_SetString(PyExc_TypeError, "Callback must be callable!");
            return NULL;
        }

        Py_XINCREF(new_callback);
        Py_XDECREF(shot_processing_callback);
        shot_processing_callback = new_callback;
    }
    else {
        if (!shot_processing_callback) {
            return PyErr_Format(PyExc_ValueError, "No callback found!");
        }
    }

    const char * items[] = { CCD_EXPOSURE_ITEM_NAME };
    double values[1] = { exposure };
    indigo_change_number_property(&ccd_client, ccd_device_name, CCD_EXPOSURE_PROPERTY_NAME, 1, items, values);
    Py_RETURN_NONE;
}


// Python stuff


static PyMethodDef methods[] = {
    {"version", (PyCFunction)version, METH_NOARGS, "pyindigo core version"},
    {"set_ccd_driver_and_device", (PyCFunction)set_ccd_driver_and_device, METH_VARARGS, "set driver filename and device name"},
    {"setup_ccd_client", (PyCFunction)setup_ccd_client, METH_NOARGS, "start INDIGO bus and attach driver"},
    {"cleanup_ccd_client", (PyCFunction)cleanup_ccd_client, METH_NOARGS, "detach driver and stop INDIGO bus"},
    {"take_shot_with_exposure", (PyCFunction)take_shot_with_ccd, METH_VARARGS, "request new image from driver and optional set new callback"},
    {NULL, NULL, 0, NULL}  /* Sentinel */
};

static struct PyModuleDef _pyindigo = {
    PyModuleDef_HEAD_INIT,
    "_pyindigo",
    "Python interface to INDIGO operations. Used by wrapper class and should not be imported directly!",
    -1,
    methods
};

PyMODINIT_FUNC PyInit__pyindigo(void)
{
    pyindigo_IndigoException = PyErr_NewException("pyindigo.IndigoException", NULL, NULL);
    return PyModule_Create(&_pyindigo);
}
