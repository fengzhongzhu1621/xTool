# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: codec.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor.FileDescriptor(
    name="codec.proto",
    package="",
    syntax="proto3",
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
    serialized_pb=b'\n\x0b\x63odec.proto"\x1a\n\x07Request\x12\x0f\n\x07message\x18\x01 \x01(\tb\x06proto3',
)


_REQUEST = _descriptor.Descriptor(
    name="Request",
    full_name="Request",
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    create_key=_descriptor._internal_create_key,
    fields=[
        _descriptor.FieldDescriptor(
            name="message",
            full_name="Request.message",
            index=0,
            number=1,
            type=9,
            cpp_type=9,
            label=1,
            has_default_value=False,
            default_value=b"".decode("utf-8"),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    serialized_options=None,
    is_extendable=False,
    syntax="proto3",
    extension_ranges=[],
    oneofs=[],
    serialized_start=15,
    serialized_end=41,
)

DESCRIPTOR.message_types_by_name["Request"] = _REQUEST
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Request = _reflection.GeneratedProtocolMessageType(
    "Request",
    (_message.Message,),
    {
        "DESCRIPTOR": _REQUEST,
        "__module__": "codec_pb2",
        # @@protoc_insertion_point(class_scope:Request)
    },
)
_sym_db.RegisterMessage(Request)


# @@protoc_insertion_point(module_scope)
