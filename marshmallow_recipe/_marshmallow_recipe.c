#include <Python.h>
#include <datetime.h>
#include <stdbool.h>
#include "jansson.h"

static PyObject *uuid_type = NULL;
static PyObject *decimal_type = NULL;
static PyObject *is_dataclass_func = NULL;
static PyObject *known_dataclasses = NULL;

static bool _is_dataclass(PyObject *obj) {
    PyObject* obj_type = PyObject_Type(obj);
    int is_known_dataclass_found = PySequence_Contains(known_dataclasses, obj_type);
    if (is_known_dataclass_found > 0) {
        return true;
    }
    PyObject *is_dataclass_result = PyObject_CallFunctionObjArgs(is_dataclass_func, obj_type, NULL);
    if (is_dataclass_result == NULL) {
        return false;
    }
    bool is_dataclass = Py_IsTrue(is_dataclass_result);
    Py_DecRef(is_dataclass_result);
    if (is_dataclass) {
        PyList_Append(known_dataclasses, obj_type);
    }
    return is_dataclass;
}

static PyObject *_dump(PyObject *obj_schema, PyObject *obj) {
    if (!PyDict_Check(obj_schema)) {
        PyErr_SetString(PyExc_ValueError, "Schema must be a dict");
        return NULL;
    }

    if (PyList_Check(obj)) {
        PyObject *list = PyList_New(0);
        for (Py_ssize_t i = 0; i < PyList_Size(obj); i++) {
            PyObject *item = PyList_GetItem(obj, i);
            PyObject *dumped_item = _dump(obj_schema, item);
            if (dumped_item == NULL) {
                return NULL;
            }
            PyList_Append(list, dumped_item);
        }
        return list;
    }

    if (!_is_dataclass(obj)) {
        PyErr_SetString(PyExc_ValueError, "Object must be a dataclass");
        return NULL;
    }

    PyObject *dumped = PyDict_New();
    PyObject *obj_schema_field_name, *obj_schema_field_schema;
    Py_ssize_t obj_schema_pos = 0;
    while (PyDict_Next(obj_schema, &obj_schema_pos, &obj_schema_field_name, &obj_schema_field_schema)) {
        PyObject *name = PyDict_GetItemString(obj_schema_field_schema, "name");
        if (name == NULL || !PyUnicode_Check(name)) {
            PyErr_SetString(PyExc_ValueError, "Schema field must have a string name");
            return NULL;
        }

        PyObject *optional = PyDict_GetItemString(obj_schema_field_schema, "optional");
        if (optional == NULL || !PyBool_Check(optional)) {
            PyErr_SetString(PyExc_ValueError, "Schema field must have a bool optional");
            return NULL;
        }

        PyObject *type = PyDict_GetItemString(obj_schema_field_schema, "type");
        if (type == NULL) {
            PyErr_SetString(PyExc_ValueError, "Schema field must have a type");
            return NULL;
        }

        PyObject *obj_field_value = PyObject_GetAttr(obj, obj_schema_field_name);
        if (obj_field_value == NULL) {
            PyErr_SetString(PyExc_ValueError, "Cannot get an object field");
            return NULL;
        }

        if (obj_field_value == Py_None) {
            if (Py_IsTrue(optional)) {
                continue;
            }

            PyErr_SetString(PyExc_ValueError, "Object field is a non-optional");
            return NULL;
        }

        if (!PyObject_IsInstance(obj_field_value, type)) {
            PyErr_SetString(PyExc_ValueError, "Object field has a wrong type");
            return NULL;
        }

        if (PyDateTime_Check(obj_field_value) || PyDate_Check(obj_field_value)) {
            PyObject *isoformat_result = PyObject_CallMethod(obj_field_value, "isoformat", NULL);
            if (isoformat_result == NULL) {
                return NULL;
            }
            obj_field_value = isoformat_result;
        } else if (PyObject_IsInstance(obj_field_value, uuid_type)) {
            PyObject* str_result = PyObject_Str(obj_field_value);
            if (str_result == NULL) {
                return NULL;
            }
            obj_field_value = str_result;
        } else if (PyObject_IsInstance(obj_field_value, decimal_type)) {
             PyObject *_is_nan_result =  PyObject_CallMethod(obj_field_value, "is_nan", NULL);
             if (_is_nan_result == NULL) {
                 return NULL;
             }
            if (Py_IsTrue(_is_nan_result)) {
                PyErr_SetString(PyExc_ValueError, "Decimal should not be NAN");
                 return NULL;
            }
            PyObject* str_result = PyObject_Str(obj_field_value);
            if (str_result == NULL) {
                return NULL;
            }
            obj_field_value = str_result;
        }
        else if (PyBool_Check(obj_field_value)) {
            // pass as is
        } else if (PyUnicode_Check(obj_field_value)) {
            // pass as is
        } else if (PyLong_Check(obj_field_value)) {
            // pass as is
        } else if (PyFloat_Check(obj_field_value)) {
            // pass as is
        } else if (_is_dataclass(obj_field_value)) {
            PyObject *dataclass_schema = PyDict_GetItemString(obj_schema_field_schema, "schema");
            if (dataclass_schema == NULL) {
                PyErr_SetString(PyExc_ValueError, "Schema field must have a schema");
                return NULL;
            }
            PyObject *dataclass_dumped = _dump(dataclass_schema, obj_field_value);
            if (dataclass_dumped == NULL) {
                PyErr_SetString(PyExc_ValueError, "Schema field must have a schema");
                return NULL;
            }
            obj_field_value = dataclass_dumped;
        }

        if (PyDict_SetItem(dumped, name, obj_field_value) < 0) {
            return NULL;
        }
    }

    return dumped;
}


static PyObject *_fast_dump(PyObject *self, PyObject *args) {
    PyObject *obj_schema, *obj;
    if (!PyArg_ParseTuple(args, "OO", &obj_schema, &obj)) {
        return NULL;
    }

    return _dump(obj_schema, obj);
}



static json_t *_dump_to_json(PyObject *obj_schema, PyObject *obj) {
    if (!PyDict_Check(obj_schema)) {
        PyErr_SetString(PyExc_ValueError, "Schema must be a dict");
        return NULL;
    }

    if (PyList_Check(obj)) {
        json_t *json_arr = json_array();
        for (Py_ssize_t i = 0; i < PyList_Size(obj); i++) {
            PyObject *item = PyList_GetItem(obj, i);
            json_t *dumped_item = _dump_to_json(obj_schema, item);
            if (dumped_item == NULL) {
                return NULL;
            }
            json_array_append_new(json_arr, dumped_item);
        }
        return json_arr;
    }

    if (!_is_dataclass(obj)) {
        PyErr_SetString(PyExc_ValueError, "Object must be a dataclass");
        return NULL;
    }

    json_t* json_obj = json_object();

    PyObject *obj_schema_field_name, *obj_schema_field_schema;
    Py_ssize_t obj_schema_pos = 0;
    while (PyDict_Next(obj_schema, &obj_schema_pos, &obj_schema_field_name, &obj_schema_field_schema)) {
        PyObject *name = PyDict_GetItemString(obj_schema_field_schema, "name");
        if (name == NULL || !PyUnicode_Check(name)) {
            PyErr_SetString(PyExc_ValueError, "Schema field must have a string name");
            return NULL;
        }

        PyObject *optional = PyDict_GetItemString(obj_schema_field_schema, "optional");
        if (optional == NULL || !PyBool_Check(optional)) {
            PyErr_SetString(PyExc_ValueError, "Schema field must have a bool optional");
            return NULL;
        }

        PyObject *type = PyDict_GetItemString(obj_schema_field_schema, "type");
        if (type == NULL) {
            PyErr_SetString(PyExc_ValueError, "Schema field must have a type");
            return NULL;
        }

        PyObject *obj_field_value = PyObject_GetAttr(obj, obj_schema_field_name);
        if (obj_field_value == NULL) {
            PyErr_SetString(PyExc_ValueError, "Cannot get an object field");
            return NULL;
        }

        json_t *json_value = NULL;
        if (obj_field_value == Py_None) {
            if (Py_IsTrue(optional)) {
                continue;
            }

            PyErr_SetString(PyExc_ValueError, "Object field is a non-optional");
            return NULL;
        }

        if (!PyObject_IsInstance(obj_field_value, type)) {
            PyErr_SetString(PyExc_ValueError, "Object field has a wrong type");
            return NULL;
        }

        if (PyDateTime_Check(obj_field_value) || PyDate_Check(obj_field_value)) {
            PyObject *isoformat_result = PyObject_CallMethod(obj_field_value, "isoformat", NULL);
            if (isoformat_result == NULL) {
                return NULL;
            }
            Py_ssize_t tmpSize;
            const char* tmp = PyUnicode_AsUTF8AndSize(isoformat_result, &tmpSize);
            json_value = json_stringn(tmp, tmpSize);
        } else if (
            PyObject_IsInstance(obj_field_value, uuid_type)
            || PyObject_IsInstance(obj_field_value, decimal_type)
        ) {
            PyObject* str_result = PyObject_Str(obj_field_value);
            if (str_result == NULL) {
                return NULL;
            }
            Py_ssize_t tmpSize;
            const char* tmp = PyUnicode_AsUTF8AndSize(str_result, &tmpSize);
            json_value = json_stringn(tmp, tmpSize);
        } else if (PyBool_Check(obj_field_value)) {
            json_value = json_boolean(Py_IsTrue(obj_field_value));
        } else if (PyUnicode_Check(obj_field_value)) {
            Py_ssize_t tmpSize;
            const char* tmp = PyUnicode_AsUTF8AndSize(obj_field_value, &tmpSize);
            json_value = json_stringn(tmp, tmpSize);
        } else if (PyLong_Check(obj_field_value)) {
            json_value = json_integer(PyLong_AsLong(obj_field_value));
        } else if (PyFloat_Check(obj_field_value)) {
            json_value = json_real(PyFloat_AsDouble(obj_field_value));
        } else if (_is_dataclass(obj_field_value)) {
            PyObject *dataclass_schema = PyDict_GetItemString(obj_schema_field_schema, "schema");
            if (dataclass_schema == NULL) {
                PyErr_SetString(PyExc_ValueError, "Schema field must have a schema");
                return NULL;
            }
            json_value = _dump_to_json(dataclass_schema, obj_field_value);
            if (json_value == NULL) {
                PyErr_SetString(PyExc_ValueError, "Schema field must have a schema");
                return NULL;
            }
        } else {
            PyErr_SetString(PyExc_ValueError, "Unsupported type");
            return NULL;
        }
        json_object_set_new(json_obj, PyUnicode_AsUTF8(name), json_value);
    }

    return json_obj;
}


static PyObject *_fast_dump_bytes(PyObject *self, PyObject *args) {
    PyObject *obj_schema, *obj;
    if (!PyArg_ParseTuple(args, "OO", &obj_schema, &obj)) {
        return NULL;
    }
    json_t *json = _dump_to_json(obj_schema, obj);
    if (json == NULL) {
        return NULL;
    }
    PyObject* bytes = PyBytes_FromString(json_dumps(json, JSON_COMPACT));
    json_decref(json);
    return bytes;
}

static struct PyMethodDef methods[] = {
    {"fast_dump", (PyCFunction) _fast_dump, METH_VARARGS},
    {"fast_dump_bytes", (PyCFunction) _fast_dump_bytes, METH_VARARGS},
    {NULL, NULL}
};

static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "_marshmallow_recipe",
    NULL,
    -1,
    methods
};


static int uuid_init(void) {
    PyObject* uuid_module = NULL;

    uuid_module = PyImport_ImportModule("uuid");
    if (uuid_module == NULL) {
        goto error;
    }

    uuid_type = PyObject_GetAttrString(uuid_module, "UUID");
    if (uuid_type == NULL) {
        goto error;
    }
    return 0;
error:
    Py_DecRef(uuid_type);
    Py_DecRef(uuid_module);
    return -1;
}

static int dataclasses_init(void) {
    PyObject* dataclasses_module = NULL;
    dataclasses_module = PyImport_ImportModule("dataclasses");
    if (dataclasses_module == NULL) {
        goto error;
    }

    is_dataclass_func = PyObject_GetAttrString(dataclasses_module, "is_dataclass");
    if (is_dataclass_func == NULL) {
        goto error;
    }
    return 0;
error:
    Py_DecRef(dataclasses_module);
    Py_DecRef(is_dataclass_func);
    return -1;
}

static int decimal_init(void) {
    PyObject* decimal_module = NULL;
    decimal_module = PyImport_ImportModule("decimal");
    if (decimal_module == NULL) {
        goto error;
    }
    decimal_type = PyObject_GetAttrString(decimal_module, "Decimal");
    if (decimal_type == NULL) {
        goto error;
    }
    return 0;
error:
    Py_DecRef(decimal_module);
    Py_DecRef(decimal_type);
    return -1;
}

PyMODINIT_FUNC PyInit__marshmallow_recipe(void) {
    if (uuid_init() < 0) {
        return NULL;
    }
    if (dataclasses_init() < 0) {
        return NULL;
    }
    if (decimal_init() < 0) {
        return NULL;
    }
    known_dataclasses = PyList_New(0);
    if (known_dataclasses == NULL) {
        return NULL;
    }
    PyDateTime_IMPORT;
    return PyModule_Create(&module);
}
