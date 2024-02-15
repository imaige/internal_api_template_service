# infer_input.py
from typing import List, Union, Optional, Dict
import numpy
import numpy as np

class InferInput:
    _name: str
    _shape: List[int]
    _datatype: str
    _parameters: Dict
    _data: Union[List, np.ndarray]

    def __init__(self, name: str, shape: List[int], datatype: str,
                 data: Union[List, np.ndarray] = None,
                 parameters: Optional[Union[List, Dict]] = None):  # note: made a few modifications here for simplicity
        """An object of InferInput class is used to describe the input tensor of an inference request.

        Args:
            name: The name of the inference input whose data will be described by this object.
            shape : The shape of the associated inference input.
            datatype : The data type of the associated inference input.
            data : The data of the inference input.
                   When data is not set, raw_data is used for gRPC to transmit with numpy array bytes
                   by using `set_data_from_numpy`.
            parameters : The additional inference parameters.
        """

        self._name = name
        self._shape = shape
        self._datatype = datatype.upper()
        self._parameters = parameters
        self._data = data
        self._raw_data = None


class InferRequest:
    id: Optional[str]
    model_name: str
    parameters: Optional[Dict]
    inputs: List[InferInput]
    from_grpc: bool

    def __init__(self, model_name: str, infer_inputs: List[InferInput],
                 request_id: Optional[str] = None,
                 raw_inputs=None,
                 from_grpc: Optional[bool] = False,
                 parameters: Optional[Union[List, Dict]] = None):  # note: made a few modifications here for simplicity
        """InferRequest Data Model.

        Args:
            model_name: The model name.
            infer_inputs: The inference inputs for the model.
            request_id: The id for the inference request.
            raw_inputs: The binary data for the inference inputs.
            from_grpc: Indicate if the data model is constructed from gRPC request.
            parameters: The additional inference parameters.
        """

        self.id = request_id
        self.model_name = model_name
        self.inputs = infer_inputs
        self.parameters = parameters
        self.from_grpc = from_grpc


# GRPC content datatype mappings constants
GRPC_CONTENT_DATATYPE_MAPPINGS = {
    "BOOL": "bool_contents",
    "INT8": "int_contents",
    "INT16": "int_contents",
    "INT32": "int_contents",
    "INT64": "int64_contents",
    "UINT8": "uint_contents",
    "UINT16": "uint_contents",
    "UINT32": "uint_contents",
    "UINT64": "uint64_contents",
    "FP32": "fp32_contents",
    "FP64": "fp64_contents",
    "BYTES": "bytes_contents"
}
