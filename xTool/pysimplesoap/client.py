#!/usr/bin/python
# -*- coding: latin-1 -*-
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation; either version 3, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTIBILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.

"""Pythonic simple SOAP Client implementation"""

from __future__ import unicode_literals
import sys
if sys.version > '3':
    unicode = str
    basestring = str
    long = int
try:
    import cPickle as pickle
except ImportError:
    import pickle
import copy

TIMEOUT = 60

import hashlib
import logging
import os
import tempfile
import warnings

from . import __author__, __copyright__, __license__, __version__, TIMEOUT
try:
    import urllib2
except ImportError:
    import urllib.request as urllib2
try:
    from urlparse import urlsplit
except ImportError:
    from urllib.parse import urlsplit
try:
    # Python 2.X
    from urllib2 import urlopen
except ImportError:
    # Python 3.X
    from urllib.request import urlopen
from .simplexml import SimpleXMLElement, TYPE_MAP, REVERSE_TYPE_MAP, OrderedDict, Struct
from .transport import get_http_wrapper, set_http_wrapper, get_Http
# Utility functions used throughout wsdl_parse, moved aside for readability
from .helpers import Alias, fetch, sort_dict, make_key, process_element, \
                     postprocess_element, get_message, preprocess_schema, \
                     get_local_name, get_namespace_prefix, TYPE_MAP, urlsplit
from .wsse import UsernameToken

log = logging.getLogger(__name__)

class SoapFault(RuntimeError):
    def __init__(self, faultcode, faultstring, detail=None):
        self.faultcode = faultcode
        self.faultstring = faultstring
        self.detail = detail
        RuntimeError.__init__(self, faultcode, faultstring, detail)

    def __unicode__(self):
        return '%s: %s' % (self.faultcode, self.faultstring)

    if sys.version > '3':
        __str__ = __unicode__
    else:
        def __str__(self):
            return self.__unicode__().encode('ascii', 'ignore')

    def __repr__(self):
        return "SoapFault(faultcode = %s, faultstring %s, detail = %s)" % (repr(self.faultcode),
                                                                           repr(self.faultstring),
                                                                           repr(self.detail))


# soap protocol specification & namespace
soap_namespaces = dict(
    soap11='http://schemas.xmlsoap.org/soap/envelope/',
    soap='http://schemas.xmlsoap.org/soap/envelope/',
    soapenv='http://schemas.xmlsoap.org/soap/envelope/',
    soap12='http://www.w3.org/2003/05/soap-env',
)


class SoapClient(object):
    """Simple SOAP Client (simil PHP)"""
    def __init__(self, location=None, action=None, namespace=None,
                 cert=None, exceptions=True, proxy=None, ns=None,
                 soap_ns=None, wsdl=None, wsdl_basedir='', cache=False, cacert=None,
                 sessions=False, soap_server=None, timeout=TIMEOUT,
                 http_headers=None, trace=False,
                 username=None, password=None,
                 key_file=None, plugins=None, strict=True,
                 ):
        """
        :param http_headers: Additional HTTP Headers; example: {'Host': 'ipsec.example.com'}
        """
        self.certssl = cert
        self.keyssl = key_file
        self.location = location        # server location (url)
        self.action = action            # SOAP base action
        self.namespace = namespace      # message
        self.exceptions = exceptions    # lanzar execpiones? (Soap Faults)
        self.xml_request = self.xml_response = ''
        self.http_headers = http_headers or {}
        self.plugins = plugins or []
        self.strict = strict
        # extract the base directory / url for wsdl relative imports:
        if wsdl and wsdl_basedir == '':
            # parse the wsdl url, strip the scheme and filename
            url_scheme, netloc, path, query, fragment = urlsplit(wsdl)
            wsdl_basedir = os.path.dirname(netloc + path)

        self.wsdl_basedir = wsdl_basedir

        # shortcut to print all debugging info and sent / received xml messages
        if trace:
            if trace is True:
                level = logging.DEBUG           # default logging level
            else:
                level = trace                   # use the provided level
            logging.basicConfig(level=level)
            log.setLevel(level)

        if not soap_ns and not ns:
            self.__soap_ns = 'soap'  # 1.1
        elif not soap_ns and ns:
            self.__soap_ns = 'soapenv'  # 1.2
        else:
            self.__soap_ns = soap_ns

        # SOAP Server (special cases like oracle, jbossas6 or jetty)
        self.__soap_server = soap_server

        # SOAP Header support
        self.__headers = {}         # general headers
        self.__call_headers = None  # Struct to be marshalled for RPC Call

        # check if the Certification Authority Cert is a string and store it
        if cacert and cacert.startswith('-----BEGIN CERTIFICATE-----'):
            fd, filename = tempfile.mkstemp()
            f = os.fdopen(fd, 'w+b', -1)
            log.debug("Saving CA certificate to %s" % filename)
            f.write(cacert)
            cacert = filename
            f.close()
        self.cacert = cacert

        # Create HTTP wrapper
        Http = get_Http()
        self.http = Http(timeout=timeout, cacert=cacert, proxy=proxy, sessions=sessions)
        if username and password:
            if hasattr(self.http, 'add_credentials'):
                self.http.add_credentials(username, password)
        if cert and key_file:
            if hasattr(self.http, 'add_certificate'):
                self.http.add_certificate(key=key_file, cert=cert, domain='')


        # namespace prefix, None to use xmlns attribute or False to not use it:
        self.__ns = ns
        if not ns:
            self.__xml = """<?xml version="1.0" encoding="UTF-8"?>
<%(soap_ns)s:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:xsd="http://www.w3.org/2001/XMLSchema"
    xmlns:%(soap_ns)s="%(soap_uri)s">
<%(soap_ns)s:Header/>
<%(soap_ns)s:Body>
    <%(method)s xmlns="%(namespace)s">
    </%(method)s>
</%(soap_ns)s:Body>
</%(soap_ns)s:Envelope>"""
        else:
            self.__xml = """<?xml version="1.0" encoding="UTF-8"?>
<%(soap_ns)s:Envelope xmlns:%(soap_ns)s="%(soap_uri)s" xmlns:%(ns)s="%(namespace)s">
<%(soap_ns)s:Header/>
<%(soap_ns)s:Body><%(ns)s:%(method)s></%(ns)s:%(method)s></%(soap_ns)s:Body></%(soap_ns)s:Envelope>"""

        # parse wsdl url
        self.services = wsdl and self.wsdl_parse(wsdl, cache=cache)
        self.service_port = None                 # service port for late binding

    def __getattr__(self, attr):
        """Return a pseudo-method that can be called"""
        if not self.services:  # not using WSDL?
            return lambda *args, **kwargs: self.call(attr, *args, **kwargs)
        else:  # using WSDL:
            return lambda *args, **kwargs: self.wsdl_call(attr, *args, **kwargs)

    def call(self, method, *args, **kwargs):
        """Prepare xml request and make SOAP call, returning a SimpleXMLElement.

        If a keyword argument called "headers" is passed with a value of a
        SimpleXMLElement object, then these headers will be inserted into the
        request.
        """
        #TODO: method != input_message
        # Basic SOAP request:
        soap_uri = soap_namespaces[self.__soap_ns]
        xml = self.__xml % dict(method=method,              # method tag name
                                namespace=self.namespace,   # method ns uri
                                ns=self.__ns,               # method ns prefix
                                soap_ns=self.__soap_ns,     # soap prefix & uri
                                soap_uri=soap_uri)
        request = SimpleXMLElement(xml, namespace=self.__ns and self.namespace,
                                        prefix=self.__ns)

        request_headers = kwargs.pop('headers', None)

        # serialize parameters
        if kwargs:
            parameters = list(kwargs.items())
        else:
            parameters = args
        if parameters and isinstance(parameters[0], SimpleXMLElement):
            body = request('Body', ns=list(soap_namespaces.values()),)
            # remove default body parameter (method name)
            delattr(body, method)
            # merge xmlelement parameter ("raw" - already marshalled)
            body.import_node(parameters[0])
        elif parameters:
            # marshall parameters:
            use_ns = None if (self.__soap_server == "jetty" or self.qualified is False) else True
            for k, v in parameters:  # dict: tag=valor
                if hasattr(v, "namespaces") and use_ns:
                    ns = v.namespaces.get(None, True)
                else:
                    ns = use_ns
                getattr(request, method).marshall(k, v, ns=ns)
        elif self.__soap_server in ('jbossas6',):
            # JBossAS-6 requires no empty method parameters!
            delattr(request("Body", ns=list(soap_namespaces.values()),), method)

        # construct header and parameters (if not wsdl given) except wsse
        if self.__headers and not self.services:
            self.__call_headers = dict([(k, v) for k, v in list(self.__headers.items())
                                        if not k.startswith('wsse:')])
        # always extract WS Security header and send it (backward compatible)
        if 'wsse:Security' in self.__headers and not self.plugins:
            warnings.warn("Replace wsse:Security with UsernameToken plugin",
                          DeprecationWarning)
            self.plugins.append(UsernameToken())

        if self.__call_headers:
            header = request('Header', ns=list(soap_namespaces.values()),)
            for k, v in list(self.__call_headers.items()):
                ##if not self.__ns:
                ##    header['xmlns']
                if isinstance(v, SimpleXMLElement):
                    # allows a SimpleXMLElement to be constructed and inserted
                    # rather than a dictionary. marshall doesn't allow ns: prefixes
                    # in dict key names
                    header.import_node(v)
                else:
                    header.marshall(k, v, ns=self.__ns, add_children_ns=False)
        if request_headers:
            header = request('Header', ns=list(soap_namespaces.values()),)
            for subheader in request_headers.children():
                header.import_node(subheader)

        # do pre-processing using plugins (i.e. WSSE signing)
        for plugin in self.plugins:
            plugin.preprocess(self, request, method, args, kwargs,
                                    self.__headers, soap_uri)

        self.xml_request = request.as_xml()
        self.xml_response = self.send(method, self.xml_request)
        response = SimpleXMLElement(self.xml_response, namespace=self.namespace,
                                    jetty=self.__soap_server in ('jetty',))
        if self.exceptions and response("Fault", ns=list(soap_namespaces.values()), error=False):
            detailXml = response("detail", ns=list(soap_namespaces.values()), error=False)
            detail = None

            if detailXml and detailXml.children():
                if self.services is not None:
                    operation = self.get_operation(method)
                    fault_name = detailXml.children()[0].get_name()
                    # if fault not defined in WSDL, it could be an axis or other
                    # standard type (i.e. "hostname"), try to convert it to string
                    fault = operation['faults'].get(fault_name) or unicode
                    detail = detailXml.children()[0].unmarshall(fault, strict=False)
                else:
                    detail = repr(detailXml.children())

            raise SoapFault(unicode(response.faultcode),
                            unicode(response.faultstring),
                            detail)

        # do post-processing using plugins (i.e. WSSE signature verification)
        for plugin in self.plugins:
            plugin.postprocess(self, response, method, args, kwargs,
                                     self.__headers, soap_uri)

        return response

    def send(self, method, xml):
        """Send SOAP request using HTTP"""
        if self.location == 'test': return
        # location = '%s' % self.location #?op=%s" % (self.location, method)
        http_method = str('POST')
        location = str(self.location)

        if self.services:
            soap_action = str(self.action)
        else:
            soap_action = str(self.action) + method

        headers = {
            'Content-type': 'text/xml; charset="UTF-8"',
            'Content-length': str(len(xml)),
        }

        if self.action is not None:
            headers['SOAPAction'] = soap_action

        headers.update(self.http_headers)
        log.info("POST %s" % location)
        log.debug('\n'.join(["%s: %s" % (k, v) for k, v in list(headers.items())]))
        log.debug(xml)

        if sys.version < '3':
            # Ensure http_method, location and all headers are binary to prevent
            # UnicodeError inside httplib.HTTPConnection._send_output.

            # httplib in python3 do the same inside itself, don't need to convert it here
            headers = dict((str(k), str(v)) for k, v in list(headers.items()))

        response, content = self.http.request(
            location, http_method, body=xml, headers=headers)
        self.response = response
        self.content = content

        log.debug('\n'.join(["%s: %s" % (k, v) for k, v in list(response.items())]))
        log.debug(content)
        return content

    def get_operation(self, method):
        # try to find operation in wsdl file
        soap_ver = self.__soap_ns.startswith('soap12') and 'soap12' or 'soap11'
        if not self.service_port:
            for service_name, service in list(self.services.items()):
                for port_name, port in [port for port in list(service['ports'].items())]:
                    if port['soap_ver'] == soap_ver:
                        self.service_port = service_name, port_name
                        break
                else:
                    raise RuntimeError('Cannot determine service in WSDL: '
                                       'SOAP version: %s' % soap_ver)
        else:
            port = self.services[self.service_port[0]]['ports'][self.service_port[1]]
        if not self.location:
            self.location = port['location']
        operation = port['operations'].get(method)
        if not operation:
            raise RuntimeError('Operation %s not found in WSDL: '
                               'Service/Port Type: %s' %
                               (method, self.service_port))
        return operation

    def wsdl_call(self, method, *args, **kwargs):
        """Pre and post process SOAP call, input and output parameters using WSDL"""
        return self.wsdl_call_with_args(method, args, kwargs)

    def wsdl_call_with_args(self, method, args, kwargs):
        """Pre and post process SOAP call, input and output parameters using WSDL"""
        soap_uri = soap_namespaces[self.__soap_ns]
        operation = self.get_operation(method)

        # get i/o type declarations:
        input = operation['input']
        output = operation['output']
        header = operation.get('header')
        if 'action' in operation:
            self.action = operation['action']

        if 'namespace' in operation:
            self.namespace = operation['namespace'] or ''
            self.qualified = operation['qualified']

        # construct header and parameters
        if header:
            self.__call_headers = sort_dict(header, self.__headers)
        method, params = self.wsdl_call_get_params(method, input, args, kwargs)

        # call remote procedure
        response = self.call(method, *params)
        # parse results:
        resp = response('Body', ns=soap_uri).children().unmarshall(output, strict=self.strict)
        return resp and list(resp.values())[0]  # pass Response tag children

    def wsdl_call_get_params(self, method, input, args, kwargs):
        """Build params from input and args/kwargs"""
        if input and args:
            # convert positional parameters to named parameters:
            d = [(k, arg) for k, arg in zip(list(input.values())[0].keys(), args)]
            kwargs.update(dict(d))
        if input and kwargs:
            params = list(sort_dict(list(input.values())[0], kwargs).items())
            if self.__soap_server == "axis":
                # use the operation name
                method = method
            else:
                # use the message (element) name
                method = list(input.keys())[0]
        #elif not input:
            #TODO: no message! (see wsmtxca.dummy)
        else:
            params = kwargs and list(kwargs.items())

        return (method, params)

    def help(self, method):
        """Return operation documentation and invocation/returned value example"""
        operation = self.get_operation(method)
        input = operation.get('input')
        input = input and list(input.values()) and list(input.values())[0]
        if isinstance(input, dict):
            input = ", ".join("%s=%s" % (k, repr(v)) for k, v in list(input.items()))
        elif isinstance(input, list):
            input = repr(input)
        output = operation.get('output')
        if output:
            output = list(operation['output'].values())[0]
        headers = operation.get('headers') or None
        return "%s(%s)\n -> %s:\n\n%s\nHeaders: %s" % (
            method,
            input or '',
            output and output or '',
            operation.get('documentation', ''),
            headers,
        )

    soap_ns_uris = {
        'http://schemas.xmlsoap.org/wsdl/soap/': 'soap11',
        'http://schemas.xmlsoap.org/wsdl/soap12/': 'soap12',
    }
    wsdl_uri = 'http://schemas.xmlsoap.org/wsdl/'
    xsd_uri = 'http://www.w3.org/2001/XMLSchema'
    xsi_uri = 'http://www.w3.org/2001/XMLSchema-instance'

    def wsdl_parse(self, url, debug=False, cache=False):
        "Parse Web Service Description v1.1"

        log.debug("wsdl url: %s" % url)
        # Try to load a previously parsed wsdl:
        force_download = False
        if cache:
            # make md5 hash of the url for caching...
            filename_pkl = "%s.pkl" % hashlib.md5(url).hexdigest()
            if isinstance(cache, basestring):
                filename_pkl = os.path.join(cache, filename_pkl)
            if os.path.exists(filename_pkl):
                log.debug("Unpickle file %s" % (filename_pkl, ))
                f = open(filename_pkl, "r")
                pkl = pickle.load(f)
                f.close()
                # sanity check:
                if pkl['version'][:-1] != __version__.split(" ")[0][:-1] or pkl['url'] != url:
                    import warnings
                    warnings.warn('version or url mismatch! discarding cached wsdl', RuntimeWarning)
                    if debug:
                        log.debug('Version: %s %s' % (pkl['version'], __version__))
                        log.debug('URL: %s %s' % (pkl['url'], url))
                    force_download = True
                else:
                    self.namespace = pkl['namespace']
                    self.documentation = pkl['documentation']
                    return pkl['services']

        soap_ns = {
            'http://schemas.xmlsoap.org/wsdl/soap/': 'soap11',
            'http://schemas.xmlsoap.org/wsdl/soap12/': 'soap12',
        }
        wsdl_uri = 'http://schemas.xmlsoap.org/wsdl/'
        xsd_uri = 'http://www.w3.org/2001/XMLSchema'
        xsi_uri = 'http://www.w3.org/2001/XMLSchema-instance'

        get_local_name = lambda s: s and str((':' in s) and s.split(':')[1] or s)
        get_namespace_prefix = lambda s: s and str((':' in s) and s.split(':')[0] or None)

        # always return an unicode object:
        REVERSE_TYPE_MAP['string'] = unicode
        REVERSE_TYPE_MAP['int'] = int
        REVERSE_TYPE_MAP['long'] = long

        def fetch(url):
            "Download a document from a URL, save it locally if cache enabled"

            # check / append a valid schema if not given:
            url_scheme, netloc, path, query, fragment = urlsplit(url)
            if not url_scheme in ('http','https', 'file'):
                for scheme in ('http','https', 'file'):
                    try:
                        if not url.startswith("/") and scheme in ('http', 'https'):
                            tmp_url = "%s://%s" % (scheme, url)
                        else:
                            tmp_url = "%s:%s" % (scheme, url)
                        if debug: log.debug("Scheme not found, trying %s" % scheme)
                        return fetch(tmp_url)
                    except Exception as e:
                        log.error(e)
                raise RuntimeError("No scheme given for url: %s" % url)

            # make md5 hash of the url for caching...
            filename = '%s.xml' % hashlib.md5(url.encode('utf8')).hexdigest()
            if isinstance(cache, basestring):
                filename = os.path.join(cache, filename)
            if cache and os.path.exists(filename) and not force_download:
                log.info("Reading file %s" % (filename, ))
                f = open(filename, "r")
                xml = f.read()
                f.close()
            else:
                if url_scheme == 'file':
                    log.info("Fetching url %s using urllib2" % (url, ))
                    f = urlopen(url)
                    xml = f.read()
                else:
                    log.info("GET %s using %s" % (url, self.http._wrapper_version))
                    response, xml = self.http.request(url, "GET", None, {})
                if cache:
                    log.info("Writing file %s" % (filename, ))
                    if not os.path.isdir(cache):
                        os.makedirs(cache)
                    f = open(filename, "w")
                    f.write(xml)
                    f.close()
            return xml

        # Open uri and read xml:
        xml = fetch(url)
        # Parse WSDL XML:
        wsdl = SimpleXMLElement(xml, namespace=wsdl_uri)

        # detect soap prefix and uri (xmlns attributes of <definitions>)
        xsd_ns = None
        soap_uris = {}
        for k, v in wsdl[:]:
            if v in soap_ns and k.startswith("xmlns:"):
                soap_uris[get_local_name(k)] = v
            if v== xsd_uri and k.startswith("xmlns:"):
                xsd_ns = get_local_name(k)

        # Extract useful data:
        self.namespace = wsdl['targetNamespace']
        self.documentation = unicode(wsdl('documentation', error=False) or '')

        services = {}
        bindings = {}           # binding_name: binding
        operations = {}         # operation_name: operation
        port_type_bindings = {} # port_type_name: binding
        messages = {}           # message: element
        elements = {}           # element: type def

        for service in wsdl.service:
            service_name=service['name']
            if not service_name:
                continue # empty service?
            if debug: log.debug("Processing service %s" % service_name)
            serv = services.setdefault(service_name, {'ports': {}})
            serv['documentation']=service['documentation'] or ''
            for port in service.port:
                binding_name = get_local_name(port['binding'])
                address = port('address', ns=list(soap_uris.values()), error=False)
                location = address and address['location'] or None
                soap_uri = address and soap_uris.get(address.get_prefix())
                soap_ver = soap_uri and soap_ns.get(soap_uri)
                bindings[binding_name] = {'service_name': service_name,
                    'location': location,
                    'soap_uri': soap_uri, 'soap_ver': soap_ver,
                    }
                serv['ports'][port['name']] = bindings[binding_name]

        for binding in wsdl.binding:
            binding_name = binding['name']
            if debug: log.debug("Processing binding %s" % service_name)
            soap_binding = binding('binding', ns=list(soap_uris.values()), error=False)
            transport = soap_binding and soap_binding['transport'] or None
            port_type_name = get_local_name(binding['type'])
            bindings[binding_name].update({
                'port_type_name': port_type_name,
                'transport': transport, 'operations': {},
                })
            port_type_bindings[port_type_name] = bindings[binding_name]
            for operation in binding.operation:
                op_name = operation['name']
                op = operation('operation',ns=list(soap_uris.values()), error=False)
                action = op and op['soapAction']
                d = operations.setdefault(op_name, {})
                bindings[binding_name]['operations'][op_name] = d
                d.update({'name': op_name})
                d['parts'] = {}
                # input and/or ouput can be not present!
                input = operation('input', error=False)
                body = input and input('body', ns=list(soap_uris.values()), error=False)
                d['parts']['input_body'] = body and body['parts'] or None
                output = operation('output', error=False)
                body = output and output('body', ns=list(soap_uris.values()), error=False)
                d['parts']['output_body'] = body and body['parts'] or None
                header = input and input('header', ns=list(soap_uris.values()), error=False)
                d['parts']['input_header'] = header and {'message': header['message'], 'part': header['part']} or None
                headers = output and output('header', ns=list(soap_uris.values()), error=False)
                d['parts']['output_header'] = header and {'message': header['message'], 'part': header['part']} or None
                #if action: #TODO: separe operation_binding from operation
                if action:
                    d["action"] = action

        def make_key(element_name, element_type):
            "return a suitable key for elements"
            # only distinguish 'element' vs other types
            if element_type in ('complexType', 'simpleType'):
                eltype = 'complexType'
            else:
                eltype = element_type
            if eltype not in ('element', 'complexType', 'simpleType'):
                raise RuntimeError("Unknown element type %s = %s" % (unicode(element_name), eltype))
            return (unicode(element_name), eltype)

        #TODO: cleanup element/schema/types parsing:
        def process_element(element_name, node, element_type):
            "Parse and define simple element types"
            if debug:
                log.debug("Processing element %s %s" % (element_name, element_type))
            for tag in node:
                if tag.get_local_name() in ("annotation", "documentation"):
                    continue
                elif tag.get_local_name() in ('element', 'restriction'):
                    if debug: log.debug("%s has not children! %s" % (element_name,tag))
                    children = tag # element "alias"?
                    alias = True
                elif tag.children():
                    children = tag.children()
                    alias = False
                else:
                    if debug: log.debug("%s has not children! %s" % (element_name,tag))
                    continue #TODO: abstract?
                d = OrderedDict()
                for e in children:
                    t = e['type']
                    if not t:
                        t = e['base'] # complexContent (extension)!
                    if not t:
                        t = 'anyType' # no type given!
                    t = t.split(":")
                    if len(t)>1:
                        ns, type_name = t
                    else:
                        ns, type_name = None, t[0]
                    if element_name == type_name:
                        pass ## warning with infinite recursion
                    uri = ns and e.get_namespace_uri(ns) or xsd_uri
                    if uri==xsd_uri:
                        # look for the type, None == any
                        fn = REVERSE_TYPE_MAP.get(unicode(type_name), None)
                    else:
                        fn = None
                    if not fn:
                        # simple / complex type, postprocess later
                        fn = elements.setdefault(make_key(type_name, "complexType"), OrderedDict())

                    if e['name'] is not None and not alias:
                        e_name = unicode(e['name'])
                        d[e_name] = fn
                    else:
                        if debug: log.debug("complexConent/simpleType/element %s = %s" % (element_name, type_name))
                        d[None] = fn
                    if e['maxOccurs']=="unbounded" or (ns == 'SOAP-ENC' and type_name == 'Array'):
                        # it's an array... TODO: compound arrays?
                        d.array = True
                    if e is not None and e.get_local_name() == 'extension' and e.children():
                        # extend base element:
                        process_element(element_name, e.children(), element_type)
                elements.setdefault(make_key(element_name, element_type), OrderedDict()).update(d)

        # check axis2 namespace at schema types attributes
        self.namespace = dict(wsdl.types("schema", ns=xsd_uri)[:]).get('targetNamespace', self.namespace)

        imported_schemas = {}

        def preprocess_schema(schema):
            "Find schema elements and complex types"
            for element in schema.children() or []:
                if element.get_local_name() in ('import', ):
                    schema_namespace = element['namespace']
                    schema_location = element['schemaLocation']
                    if schema_location is None:
                        if debug: log.debug("Schema location not provided for %s!" % (schema_namespace, ))
                        continue
                    if schema_location in imported_schemas:
                        if debug: log.debug("Schema %s already imported!" % (schema_location, ))
                        continue
                    imported_schemas[schema_location] = schema_namespace
                    if debug: print("Importing schema %s from %s" % (schema_namespace, schema_location))
                    # Open uri and read xml:
                    xml = fetch(schema_location)
                    # Parse imported XML schema (recursively):
                    imported_schema = SimpleXMLElement(xml, namespace=xsd_uri)
                    preprocess_schema(imported_schema)

                element_type = element.get_local_name()
                if element_type in ('element', 'complexType', "simpleType"):
                    element_name = unicode(element['name'])
                    if debug: log.debug("Parsing Element %s: %s" % (element_type, element_name))
                    if element.get_local_name() == 'complexType':
                        children = element.children()
                    elif element.get_local_name() == 'simpleType':
                        children = element("restriction", ns=xsd_uri)
                    elif element.get_local_name() == 'element' and element['type']:
                        children = element
                    else:
                        children = element.children()
                        if children:
                            children = children.children()
                        elif element.get_local_name() == 'element':
                            children = element
                    if children:
                        process_element(element_name, children, element_type)

        def postprocess_element(elements):
            "Fix unresolved references (elements referenced before its definition, thanks .net)"
            for k,v in list(elements.items()):
                if isinstance(v, OrderedDict):
                    if v.array:
                        elements[k] = [v] # convert arrays to python lists
                    if v!=elements: #TODO: fix recursive elements
                        postprocess_element(v)
                    if None in v and v[None]: # extension base?
                        if isinstance(v[None], dict):
                            for i, kk in enumerate(v[None]):
                                # extend base -keep orginal order-
                                if v[None] is not None:
                                    elements[k].insert(kk, v[None][kk], i)
                            del v[None]
                        else:  # "alias", just replace
                            if debug: log.debug("Replacing %s = %s" % (k, v[None]))
                            elements[k] = v[None]
                            #break
                if isinstance(v, list):
                    for n in v: # recurse list
                        postprocess_element(n)


        # process current wsdl schema:
        for schema in wsdl.types("schema", ns=xsd_uri):
            preprocess_schema(schema)

        postprocess_element(elements)

        for message in wsdl.message:
            for part in message('part', error=False) or []:
                element = {}
                element_name = part['element']
                if not element_name:
                    # some implementations (axis) uses type instead
                    element_name = part['type']
                type_ns = get_namespace_prefix(element_name)
                type_uri = wsdl.get_namespace_uri(type_ns)
                part_name = part['name'] or None
                if type_uri == self.xsd_uri:
                    element_name = get_local_name(element_name)
                    fn = REVERSE_TYPE_MAP.get(element_name, None)
                    element = {part_name: fn}
                    # emulate a true Element (complexType)
                    message = messages.setdefault((message['name'], None), {message['name']: OrderedDict()})
                    list(message.values())[0].update(element)
                else:
                    element_name = get_local_name(element_name)
                    fn = elements.get(make_key(element_name, 'element'))
                    if not fn:
                        # some axis servers uses complexType for part messages
                        fn = elements.get(make_key(element_name, 'complexType'))
                        element = {message['name']: {part['name']: fn}}
                    else:
                        element = {element_name: fn}
                    messages[(message['name'], part['name'])] = element

        for port_type in wsdl.portType:
            port_type_name = port_type['name']
            if debug: log.debug("Processing port type %s" % port_type_name)
            binding = port_type_bindings[port_type_name]

            for operation in port_type.operation:
                op_name = operation['name']
                op = operations[op_name]
                op['documentation'] = unicode(operation('documentation', error=False) or '')
                if binding['soap_ver']:
                    #TODO: separe operation_binding from operation (non SOAP?)
                    if operation("input", error=False):
                        input_msg = get_local_name(operation.input['message'])
                        input_header = op['parts'].get('input_header')
                        if input_header:
                            header_msg = get_local_name(input_header.get('message'))
                            header_part = get_local_name(input_header.get('part'))
                            # warning: some implementations use a separate message!
                            header = get_message(messages, header_msg or input_msg, header_part)
                        else:
                            header = None   # not enought info to search the header message:
                        op['input'] = get_message(messages, input_msg, op['parts'].get('input_body'), op.get('parameter_order'))
                        op['header'] = header
                    else:
                        op['input'] = None
                        op['header'] = None
                    if operation("output", error=False):
                        output_msg = get_local_name(operation.output['message'])
                        op['output'] = get_message(messages, output_msg, op['parts'].get('output_body'))
                    else:
                        op['output'] = None

        # dump the full service/port/operation map
        #log.debug(pprint.pformat(services))

        # Save parsed wsdl (cache)
        if cache:
            f = open(filename_pkl, "wb")
            pkl = {
                'version': __version__.split(' ')[0],
                'url': url,
                'namespace': self.namespace,
                'documentation': self.documentation,
                'services': services,
            }
            pickle.dump(pkl, f)
            f.close()

        return services

    def __setitem__(self, item, value):
        """Set SOAP Header value - this header will be sent for every request."""
        self.__headers[item] = value

    def close(self):
        """Finish the connection and remove temp files"""
        self.http.close()
        if self.cacert.startswith(tempfile.gettempdir()):
            log.debug('removing %s' % self.cacert)
            os.unlink(self.cacert)

    def __repr__(self):
        s = 'SOAP CLIENT'
        s += '\n ELEMENTS'
        for e in self.elements:
            if isinstance(e, type):
                e = e.__name__
            elif isinstance(e, Alias):
                e = e.xml_type
            elif isinstance(e, Struct) and e.key[1]=='element':
                e = repr(e)
            else:
                continue
            s += '\n  %s' % e
        for service in self.services:
            s += '\n SERVICE (%s)' % service
            ports = self.services[service]['ports']
            for port in ports:
                port = ports[port]
                if port['soap_ver'] == None: continue
                s += '\n   PORT (%s)' % port['name']
                s += '\n    Location: %s' % port['location']
                s += '\n    Soap ver: %s' % port['soap_ver']
                s += '\n    Soap URI: %s' % port['soap_uri']
                s += '\n    OPERATIONS'
                operations = port['operations']
                for operation in sorted(operations):
                    operation = self.get_operation(operation)
                    input = operation.get('input')
                    input = input and list(input.values()) and list(input.values())[0]
                    input_str = ''
                    if isinstance(input, dict):
                        if 'parameters' not in input or input['parameters']!=None:
                            for k, v in list(input.items()):
                                if isinstance(v, type):
                                    v = v.__name__
                                elif isinstance(v, Alias):
                                    v = v.xml_type
                                elif isinstance(v, Struct):
                                    v = v.key[0]
                                input_str += '%s: %s, ' % (k, v)
                    output = operation.get('output')
                    if output:
                        output = list(operation['output'].values())[0]
                    s += '\n     %s(%s)' % (
                        operation['name'],
                        input_str[:-2]
                        )
                    s += '\n      > %s' % output

        return s

def parse_proxy(proxy_str):
    """Parses proxy address user:pass@host:port into a dict suitable for httplib2"""
    proxy_dict = {}
    if proxy_str is None:
        return
    if '@' in proxy_str:
        user_pass, host_port = proxy_str.split('@')
    else:
        user_pass, host_port = '', proxy_str
    if ':' in host_port:
        host, port = host_port.split(':')
        proxy_dict['proxy_host'], proxy_dict['proxy_port'] = host, int(port)
    if ':' in user_pass:
        proxy_dict['proxy_user'], proxy_dict['proxy_pass'] = user_pass.split(':')
    return proxy_dict


if __name__ == '__main__':
    pass
