import hashlib
import os

from django.db import models
from django.utils.translation import gettext_lazy as _lazy

from core.constants import LEN_LONG, LEN_MIDDLE, LEN_SHORT
from core.models import SoftDeleteModel


def media_file_name(instance, filename):
    h = instance.md5sum
    basename, ext = os.path.splitext(filename)
    return os.path.join("files", h[:1], h[1:2], h + ext.lower())


class FileList(SoftDeleteModel):
    name = models.CharField(max_length=LEN_LONG, null=True, blank=True, verbose_name=_lazy("名称"))
    url = models.FileField(upload_to=media_file_name, null=True, blank=True)
    file_url = models.CharField(max_length=LEN_LONG, blank=True, verbose_name=_lazy("文件地址"))
    engine = models.CharField(max_length=LEN_MIDDLE, default="local", blank=True, verbose_name=_lazy("引擎"))
    mime_type = models.CharField(max_length=LEN_MIDDLE, blank=True, verbose_name=_lazy("Mime类型"))
    size = models.CharField(max_length=LEN_SHORT, blank=True, verbose_name=_lazy("文件大小"))
    md5sum = models.CharField(max_length=LEN_SHORT, blank=True, verbose_name=_lazy("文件md5"))

    def save(self, *args, **kwargs):
        # 计算文件的 md5
        if not self.md5sum:
            md5 = hashlib.md5()
            for chunk in self.url.chunks():
                md5.update(chunk)
            self.md5sum = md5.hexdigest()
        # 获得文件的大小
        if not self.size:
            self.size = self.url.size
        # 构造文件的存储路径
        if not self.file_url:
            url = media_file_name(self, self.name)
            self.file_url = f"media/{url}"
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _lazy("文件管理")
        verbose_name_plural = verbose_name
