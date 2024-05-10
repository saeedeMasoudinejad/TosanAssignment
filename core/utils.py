import os
from decimal import Decimal


def convertor(num, convert_to: ['decimal', 'integer']):
    if convert_to == 'decimal':
        result = round(Decimal(num / (10 ** int(os.environ['MAX_DECIMAL_PLACES']))), 2)
    else:
        result = int(num * (10 ** int(os.environ['MAX_DECIMAL_PLACES'])))
    return result
