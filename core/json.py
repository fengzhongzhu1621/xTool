import datetime
import decimal
import json
import uuid

import pytz
from django.utils.duration import duration_iso_string
from django.utils.functional import Promise
from django.utils.timezone import is_aware

from core.utils.time_tools import strftime_local
from xTool.time_utils.convert import date_to_string


class DjangoJSONEncoderExtend(json.JSONEncoder):
    """
    JSONEncoder subclass that knows how to encode date/time, decimal types and UUIDs.
    """

    def default(self, o):  # pylint: disable=too-many-return-statements
        # See "Date Time String Format" in the ECMA-262 specification.
        if isinstance(o, datetime.datetime):
            return strftime_local(o, fmt="%Y-%m-%d %H:%M:%S%z")
        elif isinstance(o, type(pytz.UTC)):
            return strftime_local(o.localize(datetime.datetime.utcnow()), fmt="%Y-%m-%d %H:%M:%S%z")
        elif isinstance(o, datetime.date):
            return date_to_string(o)
        elif isinstance(o, datetime.time):
            if is_aware(o):
                raise ValueError("JSON can't represent timezone-aware times.")
            iso_format = o.isoformat()
            if o.microsecond:
                iso_format = iso_format[:12]
            return iso_format
        elif isinstance(o, datetime.timedelta):
            return duration_iso_string(o)
        elif isinstance(o, (uuid.UUID, decimal.Decimal)):
            return str(o)
        elif isinstance(o, Promise):
            return str(o)
        elif isinstance(o, bytes):
            return str(o, encoding="utf-8")
        elif isinstance(o, set):
            return list(o)

        return super().default(o)
