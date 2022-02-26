import cerberus
from cerberus import Validator

# schema = {'id': {'type': 'string'},
#           'pnr': {'type': 'string'},
#           'expires_at': {'type': 'datetime'},
#           'phone': {'type': 'string'},
#           'email': {'type': 'string'},
#           'offer': {'type': 'dict'},
#           'passengers': {'type': ['dict', 'list']}}

schema = {'offer_id': {'type': 'string'},
          'phone': {'type': 'string'},
          'email': {'type': 'string'},
          'passengers': {'type': ['dict', 'list']}}

v = Validator(schema)


def validated(data):
    return v.validate(data)


print(str('abc'))
