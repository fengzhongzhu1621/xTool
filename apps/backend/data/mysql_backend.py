from django.db import transaction

from apps.backend.data.base_backend import BaseDataBackend
from apps.backend.models import Data


class MySQLDataBackend(BaseDataBackend):
    def exists(self, key):
        return Data.objects.filter(key=key).exists()

    def incr_expireat(self, name, amount, when=None):
        with transaction.atomic():
            try:
                data = Data.objects.select_for_update().get(key=name)
                data.value += 1
                # todo 过期重置value
                # 如果when不是None, 则表示需要更新过期时间
                if when:
                    data.expire_at = when
                data.save()
            except Data.DoesNotExist:
                data = Data.objects.create(key=name, value=amount, type="string", expire_at=when)

            return data.value
