from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class StatusResponse(_message.Message):
    __slots__ = ("message",)
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...

class ImageComparisonOutput(_message.Message):
    __slots__ = ("model_name", "id", "name", "datatype", "shape", "contents")
    MODEL_NAME_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DATATYPE_FIELD_NUMBER: _ClassVar[int]
    SHAPE_FIELD_NUMBER: _ClassVar[int]
    CONTENTS_FIELD_NUMBER: _ClassVar[int]
    model_name: str
    id: str
    name: str
    datatype: str
    shape: int
    contents: _containers.RepeatedScalarFieldContainer[bytes]
    def __init__(self, model_name: _Optional[str] = ..., id: _Optional[str] = ..., name: _Optional[str] = ..., datatype: _Optional[str] = ..., shape: _Optional[int] = ..., contents: _Optional[_Iterable[bytes]] = ...) -> None: ...
