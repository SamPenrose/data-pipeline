import json, os, unittest
from jsonschema import validate, ValidationError

LOCAL = os.path.dirname(__file__)
SAMPLE_PING_PATH = os.path.join(LOCAL, 'sample_v4_ping.json')
BASE_SET_PATH = os.path.join(LOCAL, '..', 'base_set.json')
EXECUTIVE_SUMMARY_PATH = os.path.join(LOCAL, '..', 'executive_summary.json')
VALID_CRASH_SUMMARY = [
  1446836356.902004, # XXX -> nanoseconds?
  '2015-01-01', # XXX also
  '6fd3eb50-8bec-4b9c-8778-59406171312a', # clientId
  'I am a 32 char string.Fix me pls', # buildVersion
  '20151103030248', # buildId
  'I am a 32 char string.Fix me pls', # buildArchitecture
  'release',
  'Windows',
  'I am a 32 char string.Fix me pls', # osVersion
  'I am a 32 char string.Fix me pls', # osServicepackMajor
  'I am a 32 char string.Fix me pls', # osServicepackMinor
  'I am a 32 char string.Fix me pls', # locale
  'I am a 32 char string.Fix me pls', # activeExperiment
  'I am a 32 char string.Fix me pls', # activeExperimentBranch
  '5char', # country
  False # hasCrashEnvironment
]

class TestBaseSet(unittest.TestCase):

    def test_base_set(self):
        with open(BASE_SET_PATH) as f:
            schema = json.load(f)
        # The presence of $schema means that validate will verify that
        # base_set.json meets the requirements for version 4 of JSON schema
        self.failUnless('$schema' in schema)
        self.assertRaises(ValidationError, validate, {}, schema)
        with open(SAMPLE_PING_PATH) as f:
            ping = json.load(f)
        validate(ping, schema)

    def test_executive_summary(self):
        with open(EXECUTIVE_SUMMARY_PATH) as f:
            schema = json.load(f)
        # The presence of $schema means that validate will verify that
        # the file meets the requirements for version 4 of JSON schema
        self.failUnless('$schema' in schema)
        self.assertRaises(ValidationError, validate, {}, schema)
        # validate(VALID_CRASH_SUMMARY, schema)


if __name__ == '__main__':
    unittest.main()
