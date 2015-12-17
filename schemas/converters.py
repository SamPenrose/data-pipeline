try:
    from pyspark.sql import types as T # * masks e.g. types.StringType
    JS_Type2ParquetClass = {
        "boolean": T.BooleanType,
        "number": T.LongType, # XXX ?
        "string": T.StringType,
    }
except ImportError:
    # Hypothetical use outside pyspark
    T = None
    JS_Type2ParquetClass = None

class ConversionError(ValueError):
    '''
    When is a type error not a TypeError?
    '''


def jsonschema2parquet(js_schema):
    '''
    Convert a JSONSchema blob into the equivalent Parquet data structure.
    '''
    if T is None:
        raise ImportError("Can't create Parquet objects outside pyspark.")
    parquet_schema = T.StructType()
    js_top = js_schema.get('type')
    if js_top == 'object':
        parquet_schema.add(_object2parquet(js_top))
    elif js_top == 'array':
        # XXX minItems, maxItems, additionalItems
        parquet_schema.add(_array2parquet(js_top))
    else:
        raise ConversionError("Can't handle JSON-Schema type '%s'" % container)
    return parquet_schema


def _array2parquet(js_array):
    parquet_list = T.List()
    for js_item in js_array:
        js_type = jsitem['type']
        try:
            klass = JS_Type2ParquetClass[js_type]
        except KeyError:
            raise ConversionError("Can't convert JSON item: %s" % js_item)
        parquet_item = klass()


def _object2parquet(js_object):
    required = js_object.get('required', [])
    properties = js_object.get('properties', {})
    for property_name, property_value in properties.items():
        pass
