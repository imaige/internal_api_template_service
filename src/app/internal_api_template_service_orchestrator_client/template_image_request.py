import grpc
from proto_models.internal_api_template_service_pb2 import (
    ImageRequest, ImageReply, ModelInferRequest, ModelInferResponse
)
from proto_models.internal_api_template_service_pb2_grpc import (
    InternalApiTemplateServiceStub
)
from proto_models.infer_input import InferInput, GRPC_CONTENT_DATATYPE_MAPPINGS
from ...libraries.logging_file_format import configure_logger
from ...libraries.get_tls_certs import get_secret_data

import asyncio
import logging
import base64
from PIL import Image
from io import BytesIO
import json
import os
import numpy

logger = logging.getLogger(__name__)
configure_logger(logger, level=logging.INFO)


async def template_image_request(req: ImageRequest | None, port: str, request_location: str) -> None:
    # flow for running locally
    client_key = open(f'./tls_certs/{request_location}/client-key.pem', 'rb').read()
    client_cert = open(f'./tls_certs/{request_location}/client-cert.pem', 'rb').read()
    ca_cert = open(f'./tls_certs/{request_location}/ca-cert.pem', 'rb').read()

    # flow for running on k8s
    # tls_certs = get_secret_data("default", "tls-certs")
    # client_key = tls_certs.get("client-key")
    # client_cert = tls_certs.get("client-cert")
    # ca_cert = tls_certs.get("ca-cert")

    channel_credentials = grpc.ssl_channel_credentials(
        root_certificates=ca_cert, private_key=client_key, certificate_chain=client_cert
    )

    async with grpc.aio.secure_channel(port, channel_credentials) as channel:
    # async with grpc.aio.insecure_channel(port) as channel:
        stub = InternalApiTemplateServiceStub(channel)
        logger.info(f"Client making InternalApiTemplateImageRequest to port {port}")
        with open('test_image.jpg', 'rb') as file:
            image = file.read()
            encoded_image = base64.b64encode(image)
            async for response in stub.InternalApiTemplateImageRequest(
                ImageRequest(b64image=encoded_image)
            ):
                # get image
                response_image = response.b64image
                # convert image: decode to b64, convert to BytesIO, convert to Pillow image using open, optionally show
                decoded_image = base64.b64decode(response_image)
                bytes_image = BytesIO(decoded_image)
                final_image = Image.open(bytes_image)
                final_image.show()


async def template_image_tensor_request(req: ImageRequest | None, port: str, request_location: str) -> None:
    # flow for running locally
    client_key = open(f'./tls_certs/{request_location}/client-key.pem', 'rb').read()
    client_cert = open(f'./tls_certs/{request_location}/client-cert.pem', 'rb').read()
    ca_cert = open(f'./tls_certs/{request_location}/ca-cert.pem', 'rb').read()

    # flow for running on k8s
    # tls_certs = get_secret_data("default", "tls-certs")
    # client_key = tls_certs.get("client-key")
    # client_cert = tls_certs.get("client-cert")
    # ca_cert = tls_certs.get("ca-cert")

    channel_credentials = grpc.ssl_channel_credentials(
        root_certificates=ca_cert, private_key=client_key, certificate_chain=client_cert
    )

    # async with grpc.aio.secure_channel(port, channel_credentials) as channel:
    async with grpc.aio.insecure_channel(port) as channel:
        stub = InternalApiTemplateServiceStub(channel)
        logger.info(f"Client making InferenceRequest to port {port}")
        with open('test_image.json') as file:
            data = json.load(file)
            infer_input = InferInput(name="input-0", shape=[1], datatype="BYTES",
                                     data=[base64.b64decode(data["instances"][0]["image"]["b64"])])
            # conversion attempt
            infer_inputs = []
            # if isinstance(infer_input._data, numpy.ndarray):
            #     img = load_image_from_json(infer_input._data)
            infer_input_dict = {"name": infer_input._name, "shape": infer_input._shape,
                                "datatype": infer_input._datatype, "contents": {}}

            data_key = GRPC_CONTENT_DATATYPE_MAPPINGS.get(infer_input._datatype, None)
            if data_key is not None:
                infer_input._data = [bytes(val, 'utf-8') if isinstance(val, str)
                                     else val for val in
                                     infer_input._data]  # str to byte conversion for grpc proto
                infer_input_dict["contents"][data_key] = infer_input._data
            else:
                raise Exception("invalid input datatype")

            # end attempt
            infer_inputs.append(infer_input_dict)

            request = ModelInferRequest(inputs=infer_inputs, model_name=os.environ["MODEL_NAME"])
            response = await stub.InferenceRequest(
                request
            )
            logger.info("response is from model: " + response.model_name)
