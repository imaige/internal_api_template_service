# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: information_superhighway.proto
# Protobuf Python Version: 4.25.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1einformation_superhighway.proto\x12\x18information_superhighway\"J\n\x14ImageAnalysisRequest\x12\x10\n\x08photo_id\x18\x01 \x01(\x03\x12\x10\n\x08\x62\x36\x34image\x18\x02 \x01(\t\x12\x0e\n\x06models\x18\x03 \x03(\t\"(\n\x15ImageAnalysisResponse\x12\x0f\n\x07message\x18\x01 \x01(\t\"\x07\n\x05\x45mpty2\x8f\x01\n\x1eInformationSuperhighwayService\x12m\n\x16ImageAiAnalysisRequest\x12..information_superhighway.ImageAnalysisRequest\x1a\x1f.information_superhighway.Empty\"\x00\x30\x01\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'information_superhighway_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_IMAGEANALYSISREQUEST']._serialized_start=60
  _globals['_IMAGEANALYSISREQUEST']._serialized_end=134
  _globals['_IMAGEANALYSISRESPONSE']._serialized_start=136
  _globals['_IMAGEANALYSISRESPONSE']._serialized_end=176
  _globals['_EMPTY']._serialized_start=178
  _globals['_EMPTY']._serialized_end=185
  _globals['_INFORMATIONSUPERHIGHWAYSERVICE']._serialized_start=188
  _globals['_INFORMATIONSUPERHIGHWAYSERVICE']._serialized_end=331
# @@protoc_insertion_point(module_scope)
