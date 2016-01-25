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

try:
    import ujson as json
except ImportError:
    import json

JS_TYPE_2_AVRO_TYPE = {
    'string': 'string',
    'number': 'double',
    'object': 'record'
}

class ConversionError(ValueError):
    '''
    When is a type error not a TypeError?
    '''


def jsonschema2parquet(js_schema):
    '''
    Convert a JSONSchema blob into the equivalent Parquet data structure.

    We test only the parts of the blob that we need to return something
    plausible.
    '''
    if T is None:
        raise ImportError("Can't create Parquet objects outside pyspark.")
    js_top = js_schema.get('type')
    if js_top == 'object':
        fields = _object2parquet(js_top)
    elif js_top == 'array':
        # XXX minItems, maxItems, additionalItems
        # XXX test for missing/empty items and raise ConversionError
        fields = _array2parquet(js_schema['items'])
    elif js_top is None:
        raise ConversionError("JSON-Schema is missing 'type' property")
    else:
        raise ConversionError("Can't handle JSON-Schema type '%s'" % js_top)
    parquet_schema = T.StructType(fields)
    return parquet_schema


def _array2parquet(js_array):
    parquet_list = []
    for js_item in js_array:
        js_type = js_item['type']
        # XXX ugly
        name = js_item['description'].split(':')[0]
        try:
            klass = JS_Type2ParquetClass[js_type]
        except KeyError:
            raise ConversionError("Can't convert JSON item: %s" % js_item)
        field = T.StructField(name, klass(), False)
        parquet_list.append(field)
    return parquet_list


def _object2parquet(js_object):
    required = js_object.get('required', [])[:]
    properties = js_object.get('properties', {})
    parquet_list = []
    for property_name, js_item in properties.items():
        js_type = js_item['type']
        try:
            klass = JS_Type2ParquetClass[js_type]
        except KeyError:
            raise ConversionError("Can't convert JSON item: %s" % js_item)
        nullable = not property_name in required
        field = T.StructField(property_name, klass(), nullable)
        parquet_list.append(field)
    return parquet_list


def jsonschema2avro(js_schema, declare_namespace=True):
    if T is None:
        raise ImportError("Can't create Parquet objects outside pyspark.")
    avro = {'type': 'record', 'name': js_schema['name']}
    if declare_namespace:
        avro['namespace'] = 'org.mozilla.pipeline'
    js_top = js_schema.get('type')
    if js_top == 'object':
        fields = _object2avro(js_schema)
        avro['fields'] = fields
    return avro

def _object2avro(js_schema):
    properties = js_schema.get('properties', {})
    required = js_schema.get('required', [])[:]
    fields = []
    for property_name, js_item in properties.items():
        if property_name == 'required':
            continue
        if '$ref' in js_item:
            path, container_name = js_item['$ref'].split('#/')
            with open(path) as f:
                ref_schema = json.load(f)[container_name]
                ref_avro = jsonschema2avro(ref_schema, False)

#         we have to redo record creation to:
 #           {"name": <name> "type": {"name":<fake-name>, "type": record}}

                ref_avro = {'type': ref_avro}
                ref_avro['type']['name'] = container_name + '_subtype'
                fields.append(ref_avro)
            continue
        prop = {'name': property_name}
        avro_type = JS_TYPE_2_AVRO_TYPE[js_item['type']]
        if property_name not in required:
            avro_type = ["null", avro_type]
        prop['type'] = avro_type
        fields.append(prop)
    return fields
