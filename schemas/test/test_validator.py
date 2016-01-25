import json, os, unittest
from jsonschema import validate, ValidationError

LOCAL = os.path.dirname(__file__)
SAMPLE_PING_PATH = os.path.join(LOCAL, 'sample_v4_ping.json')
MAIN_SCHEMA_PATH = os.path.join(LOCAL, 'main.schema.json')


class Test_validate(unittest.TestCase):

    def setUp(self):
        with open(SAMPLE_PING_PATH) as f:
            self.ping = json.load(f)

    def test_main(self):
        # The presence of $schema means that validate() will test
        # for specific JSON-Schema features
        with open(MAIN_SCHEMA_PATH) as f:
            schema = json.load(f)
        self.failUnless("$schema" in schema)
        # Sanity
        self.failUnless("properties" in schema)
        self.failUnless("required" in schema)
        self.assertRaises(ValidationError, validate, {}, schema)
        validate(self.ping, schema)


if __name__ == '__main__':
    unittest.main()
