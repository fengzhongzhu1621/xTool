# -*- coding: utf-8 -*-
import logging

from opentelemetry import trace

tracer = trace.get_tracer("drf_resource")
logger = logging.getLogger("drf_resource")
