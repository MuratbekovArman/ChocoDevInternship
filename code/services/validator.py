from cerberus import Validator
import uuid

booking_body_schema = {'offer_id': {'type': 'string'},
                       'phone': {'type': 'string'},
                       'email': {'type': 'string'},
                       'passengers': {'type': ['dict', 'list']}}

search_body_schema = {"cabin": {'type': 'string', 'allowed': ['Economy', 'Business']},
                      "origin": {'type': 'string', 'minlength': 3, 'maxlength': 3},
                      "destination": {'type': 'string', 'minlength': 3, 'maxlength': 3},
                      "dep_at": {'type': 'string'},
                      "arr_at": {'type': 'string'},
                      "adults": {'type': 'integer'},
                      "children": {'type': 'integer'},
                      "infants": {'type': 'integer'},
                      "currency": {'type': 'string'}
                      }


def booking_body_validated(data):
    v = Validator(booking_body_schema)
    return v.validate(data) and is_valid_uuid(data.get('offer_id'))


def search_body_validated(data):
    v = Validator(search_body_schema)
    return v.validate(data)


def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False
