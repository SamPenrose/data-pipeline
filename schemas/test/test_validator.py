import json, os, unittest
from jsonschema import validate, ValidationError

LOCAL = os.path.dirname(__file__)
SAMPLE_PING_PATH = os.path.join(LOCAL, 'sample_v4_ping.json')
PAYLOAD_BLOB_PATH = os.path.join(LOCAL, 'sample_v4_payload.json')
APPLICATION_SCHEMA_PATH = os.path.join(LOCAL, 'application.schema.json')
MAIN_SCHEMA_PATH = os.path.join(LOCAL, 'main.schema.json')
PAYLOAD_SCHEMA_PATH = os.path.join(LOCAL, 'payload-main.schema.json')
ENVIRONMENT_SCHEMA_PATH = os.path.join(LOCAL, 'environment.schema.json')


class Test_validate(unittest.TestCase):

    def setUp(self):
        with open(SAMPLE_PING_PATH) as f:
            self.ping = json.load(f)

    def test_main(self):
        # The presence of $schema means that validate() will test
        # for specific JSON-Schema features
        with open(MAIN_SCHEMA_PATH) as f:
            main_schema = json.load(f)
        self.failUnless("$schema" in main_schema)
        # Sanity
        self.failUnless("properties" in main_schema)
        self.failUnless("required" in main_schema)
        self.assertRaises(ValidationError, validate, {}, main_schema)
        validate(self.ping, main_schema)

        self.ping['creationDate'] = self.ping['creationDate'][:1]
        self.assertRaises(ValidationError, validate, self.ping, main_schema)

    def test_environment(self):
        env = self.ping['environment']
        with open(ENVIRONMENT_SCHEMA_PATH) as f:
            env_schema = json.load(f)['environment']

        validate(env, env_schema)
        del env['addons']
        # validate(env, env_schema)

    def test_application(self):
        with open(APPLICATION_SCHEMA_PATH) as f:
            app_schema = json.load(f)['application']
        app = self.ping['application']
        validate(app, app_schema)
        app['noExtraProperties'] = 1
        self.assertRaises(ValidationError, validate, app, app_schema)

    def test_payload(self):
        with open(PAYLOAD_SCHEMA_PATH) as f:
            payload_schema = json.load(f)['payload']
        with open(PAYLOAD_BLOB_PATH) as g:
            payload = json.load(g)['payload']

        validate({}, payload_schema)
        # payload = self.ping['payload']
        # del payload['log']
        validate(payload, payload_schema)
        payload["grok"] = 1
        payload_schema["additionalProperties"] = False
        self.assertRaises(ValidationError, validate, payload, payload_schema)


if __name__ == '__main__':
    unittest.main()
