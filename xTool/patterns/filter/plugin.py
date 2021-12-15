# -*- coding: utf-8 -*-

import logging

from xTool.plugin import PluginType, register_plugin
from .chain import BeforeFilter, AfterFilter


@register_plugin(PluginType.BEFORE_FILTER, "demo")
class DefaultBeforeFilter(BeforeFilter):
    def before_process(self, *args, **kwargs):
        logging.info("run before filter demo")

    async def async_before_process(self, *args, **kwargs):
        logging.info("run before filter demo")


@register_plugin(PluginType.BEFORE_FILTER, "demo")
class DefaultAfterFilter(AfterFilter):
    def after_process(self, *args, **kwargs):
        logging.info("run after filter demo")

    async def async_after_process(self, *args, **kwargs):
        logging.info("run after filter demo")
