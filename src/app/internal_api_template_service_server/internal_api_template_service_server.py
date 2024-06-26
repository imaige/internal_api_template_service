from proto_models.internal_api_template_service_pb2 import (
    TemplateRequest, TemplateReply, ImageRequest, ImageReply
)
from proto_models.internal_api_template_service_pb2_grpc import (
    InternalApiTemplateServiceServicer, add_InternalApiTemplateServiceServicer_to_server
)
from proto_models.image_comparison_outputs_pb2 import (
    ImageComparisonOutput, StatusResponse
)
from proto_models.image_comparison_outputs_pb2_grpc import (
    ImageComparisonOutputServiceServicer, add_ImageComparisonOutputServiceServicer_to_server
)
from proto_models.information_superhighway_pb2 import (
    ImageAnalysisRequest, SuperhighwayStatusReply
)
from proto_models.information_superhighway_pb2_grpc import (
    InformationSuperhighwayServiceServicer, add_InformationSuperhighwayServiceServicer_to_server
)
from proto_models.analysis_layer_pb2 import (
    AiModelOutputRequest,
)
import json
from ...libraries import kserve_request
from ...libraries.grpc_server_factory import create_secure_server
from ...libraries.grpc_analysis_layer_request import analysis_layer_request
from ...libraries.enums import AiModel
from ...libraries.logging_file_format import configure_logger
import logging

from os import getenv
import grpc
import asyncio
from google.rpc import status_pb2, code_pb2, error_details_pb2
from google.protobuf import any_pb2

import base64
from PIL import Image, ImageOps
from io import BytesIO

from os import getenv
from dotenv import load_dotenv

from typing import Union

load_dotenv()

# Check env
APP_ENV = getenv("IMAIGE_PYTHON_APP_ENVIRONMENT")
if APP_ENV == "LOCAL":
    load_dotenv(".env.local")

logger = logging.getLogger(__name__)
configure_logger(logger, level=logging.INFO)


# Service Class Definition #
# class TemplateRequester(InternalApiTemplateServiceServicer):
#     # Endpoint definition #
#     # Matches name in InternalApiTemplateServiceServicer
#     async def InternalApiTemplateRequest(
#             self, request: TemplateRequest, context: grpc.ServicerContext
#     ) -> Union[TemplateReply, status_pb2.Status]:
#         logger.info(f"Serving basic request with detail: {request}")
#         # Example error handling
#         # in this case, for using a protocol buffer that is not the designated one
#         # IMO, Python does not enforce the 'same protocol buffer' requirement as stringently as it should
#         # so it would be good practice to enforce this on our end using simple logic like the below
#         # Note - all fields in gRPC protocol buffers are optional, which we can take advantage of to pass as little
#         # information as possible; as such, the following type checking is (probably) excessive, but helpful as an
#         # illustrative example of error handling
#         if not isinstance(request, TemplateRequest):
#             logger.info(f"Failure in method call")
#             code = code_pb2.INVALID_ARGUMENT
#             details = any_pb2.Any()
#             # to access details for a particular error, use response[$index].details[0].value.decode('utf-8')
#             # as details is passed as a list and the value parameter is passed as a protobuf-serialized string
#             details.Pack(
#                 error_details_pb2.DebugInfo(
#                     detail="Invalid argument: request must use TemplateRequest protocol buffer."
#                 )
#             )
#             message = "Invalid argument error."
#             yield status_pb2.Status(
#                 code=code,
#                 message=message,
#                 details=[details]
#             )
#         # send response (optional, but recommended)
#         yield TemplateReply(message=f"Hello, {request.name}!")
#
#     async def InternalApiTemplateImageRequest(
#       self, request: ImageRequest, context: grpc.aio.ServicerContext
#     ) -> ImageReply:
#         if not isinstance(request, ImageRequest):
#             logger.info(f"Failure in photo request call")
#             code = code_pb2.INVALID_ARGUMENT
#             details = any_pb2.Any()
#             # to access details for a particular error, use response[$index].details[0].value.decode('utf-8')
#             # as details is passed as a list and the value parameter is passed as a protobuf-serialized string
#             details.Pack(
#                 error_details_pb2.DebugInfo(
#                     detail="Invalid argument: request must use ImageRequest protocol buffer."
#                 )
#             )
#             message = "Invalid argument error."
#             yield status_pb2.Status(
#                 code=code,
#                 message=message,
#                 details=[details]
#             )
#         logger.info(f"Serving photo request with detail: {request}")
#
#         # get image from request, decode from b64, cast to BytesIO, open
#         decoded_image = Image.open(BytesIO(base64.b64decode(request.b64image)))
#
#         # optionally, do something with the image, including but not limited to:
#         # modify color, scale down, crop, send request to other server
#         converted_image = ImageOps.grayscale(decoded_image)
#
#         image_stream = BytesIO()
#
#         decoded_image.save(image_stream, format="PNG")
#         # converted_image.save(image_stream, format="PNG")
#
#         bytes_image = image_stream.getvalue()
#         response_image = base64.b64encode(bytes_image)
#         yield ImageReply(b64image=response_image)
#
#
# class ImageComparisonOutputRequester(ImageComparisonOutputServiceServicer):
#     # Endpoint definition #
#     # Matches name in ImageComparisonOutputServiceServicer
#     async def ImageComparisonOutputRequest(
#         self, request: ImageComparisonOutput, context: grpc.aio.ServicerContext
#     ) -> StatusResponse:
#         logger.info(f"Serving image comparison output request with detail: {request}")
#
#         logger.info(f"Request contents is: {request.contents}")
#
#         yield StatusResponse(message="OK")


class InformationSuperhighway(InformationSuperhighwayServiceServicer):
    # Endpoint definition #
    # Matches name in InformationSuperhighwayServiceServicer
    async def ImageAiAnalysisRequest(
        self, request: ImageAnalysisRequest, context: grpc.aio.ServicerContext
    ) -> Union[SuperhighwayStatusReply, status_pb2.Status]:
        logger.info(f"Serving AI model request with photo id: {request.photo_id} and models: {request.models}")
        request_image = request.b64image
        analysis_layer_port = f'{getenv("ANALYSIS_LAYER_URL")}:80'
        for model in request.models:
            logger.info(f"starting {model} flow for photo {request.photo_id}")
            if model == "image_comparison_hash_model":
                try:
                    # TODO: this could use better error handling
                    image_comparison_output = await kserve_request.image_comparison_request(
                        # 'adea6b821626048b2a3c0032f0f71841-1183079.us-east-2.elb.amazonaws.com:80',
                        # '0.0.0.0:8081',
                        getenv("IMAGE_COMPARISON_MODEL_URL"),
                        request_image, model)
    
                    # TODO: do we need a loop here? there was one in the file that became kserve_request, but potentially can be nixed
                    for output in image_comparison_output.outputs:
                        shape = output.shape[0]
                        contents = []
                        for j in range(0, shape):
                            byte_string = output.contents.bytes_contents[j]
                            contents.extend([byte_string])
                        average_hash = output.contents.bytes_contents[0]
                        perceptual_hash = output.contents.bytes_contents[1]
                        difference_hash = output.contents.bytes_contents[2]
                        wavelet_hash_haar = output.contents.bytes_contents[3]
                        color_hash = output.contents.bytes_contents[4]
    
                        analysis_layer_input = AiModelOutputRequest(
                            photo_id=request.photo_id,
                            image_comparison_run_id=image_comparison_output.id,
                            image_comparison_name=output.name,
                            image_comparison_datatype=output.datatype,
                            image_comparison_shape=output.shape[0],
                            average_hash=average_hash,
                            perceptual_hash=perceptual_hash,
                            difference_hash=difference_hash,
                            wavelet_hash_haar=wavelet_hash_haar,
                            color_hash=color_hash
                        )
    
                        analysis_layer_response = await analysis_layer_request(analysis_layer_input, analysis_layer_port)
                        logger.info(f"response from analysis layer is: {analysis_layer_response}")
    
                        response = SuperhighwayStatusReply(message="OK")
                        logger.info(f"Superhighway sending response: {response}")
                        yield response
                except Exception as e:
                    logger.error(f"Caught error processing {model} for photo {request.photo_id}: {e}")
                    code = code_pb2.INVALID_ARGUMENT
                    details = any_pb2.Any()
                    details.Pack(
                        error_details_pb2.DebugInfo(
                            detail=f"Error processing {model} for photo {request.photo_id}."
                        )
                    )
                    message = "Internal server error."
                    yield status_pb2.Status(
                        code=code,
                        message=message,
                        details=[details]
                    ) 

            elif model == "colors_basic_model":
                try:
                    colors_output = await kserve_request.colors_request(
                        getenv("COLORS_MODEL_URL"),
                        request_image, model)
    
                    shape = colors_output.outputs[0].shape[0]
                    contents = []
                    for j in range(0, shape):
                        byte_string = colors_output.outputs[0].contents.bytes_contents[j].decode('utf-8')
                        contents.append(byte_string)
    
                    analysis_layer_input = AiModelOutputRequest(
                        photo_id=request.photo_id,
                        color_averages=json.dumps(contents)
                    )
    
                    analysis_layer_response = await analysis_layer_request(analysis_layer_input, analysis_layer_port)
                    logger.info(f"response from analysis layer is: {analysis_layer_response}")
    
                    response = SuperhighwayStatusReply(message="OK")
                    logger.info(f"Superhighway sending response: {response}")
                    yield response
                except Exception as e:
                    logger.error(f"Caught error processing {model} for photo {request.photo_id}: {e}")
                    code = code_pb2.INVALID_ARGUMENT
                    details = any_pb2.Any()
                    details.Pack(
                        error_details_pb2.DebugInfo(
                            detail=f"Error processing {model} for photo {request.photo_id}."
                        )
                    )
                    message = "Internal server error."
                    yield status_pb2.Status(
                        code=code,
                        message=message,
                        details=[details]
                    )

            elif model == "image_classification_model":
                try:
                    classification_output = await kserve_request.image_classification_request(
                        getenv("IMAGE_CLASSIFICATION_MODEL_URL"),
                        request_image, model)
    
                    logger.info(f"output is: {classification_output}")
                    contents = []
                    contents.extend(classification_output.raw_output_contents)
                    logger.info(f"before send for photo {request.photo_id}, contents is: {contents}")
    
                    analysis_layer_input = AiModelOutputRequest(
                        photo_id=request.photo_id,
                        labels_from_classifications_model=contents
                    )
    
                    analysis_layer_response = await analysis_layer_request(analysis_layer_input, analysis_layer_port)
                    logger.info(f"response from analysis layer is: {analysis_layer_response}")
    
                    response = SuperhighwayStatusReply(message="OK")
                    logger.info(f"Superhighway sending response: {response}")
                    yield response
                except Exception as e:
                    logger.error(f"Caught error processing {model} for photo {request.photo_id}: {e}")
                    code = code_pb2.INVALID_ARGUMENT
                    details = any_pb2.Any()
                    details.Pack(
                        error_details_pb2.DebugInfo(
                            detail=f"Error processing {model} for photo {request.photo_id}."
                        )
                    )
                    message = "Internal server error."
                    yield status_pb2.Status(
                        code=code,
                        message=message,
                        details=[details]
                    ) 

            elif model == "face_detect_model":
                try:
                    face_detect_output = await kserve_request.face_detect_request(
                        getenv("FACE_DETECT_MODEL_URL"),
                        request_image, model
                    )

                    shape = face_detect_output.outputs[0].shape[0]

                    contents = []
                    # TODO: once face model decoding is ready, split into the different faces
                    contents.extend(face_detect_output.raw_output_contents)

                    analysis_layer_input = AiModelOutputRequest(
                        photo_id=request.photo_id,
                        # bounding_boxes_from_faces_model=json.dumps(contents)
                        bounding_boxes_from_faces_model=shape
                    )

                    analysis_layer_response = await analysis_layer_request(analysis_layer_input, analysis_layer_port)
                    logger.info(f"response from analysis layer is: {analysis_layer_response}")

                    response = SuperhighwayStatusReply(message="OK")
                    logger.info(f"Superhighway sending response: {response}")
                    yield response
                except Exception as e:
                    logger.error(f"Caught error processing {model} for photo {request.photo_id}: {e}")
                    code = code_pb2.INVALID_ARGUMENT
                    details = any_pb2.Any()
                    details.Pack(
                        error_details_pb2.DebugInfo(
                            detail=f"Error processing {model} for photo {request.photo_id}."
                        )
                    )
                    message = "Internal server error."
                    yield status_pb2.Status(
                        code=code,
                        message=message,
                        details=[details]
                    )

            else:
                logger.info(f"Provided model name of {model} is invalid.")
                code = code_pb2.INVALID_ARGUMENT
                details = any_pb2.Any()
                # to access details for a particular error, use response[$index].details[0].value.decode('utf-8')
                # as details is passed as a list and the value parameter is passed as a protobuf-serialized string
                details.Pack(
                    error_details_pb2.DebugInfo(
                        detail=f"Invalid argument: model name of {model} is invalid."
                    )
                )
                message = "Invalid argument error."
                yield status_pb2.Status(
                    code=code,
                    message=message,
                    details=[details]
                )


# Server Creation #
async def serve() -> None:
    # flow for running locally
    request_location = "k8s_info_superhighway"
    server_key = f'./tls_certs/{request_location}/server-key.pem'
    server_cert = f'./tls_certs/{request_location}/server-cert.pem'
    ca_cert = f'./tls_certs/{request_location}/ca-cert.pem'

    port = getenv("GRPC_SERVER_PORT").strip()
    service_classes = [
        # {
        #     "add_func": add_InternalApiTemplateServiceServicer_to_server,
        #     "add_class": TemplateRequester()
        # },
        # {
        #     "add_func": add_ImageComparisonOutputServiceServicer_to_server,
        #     "add_class": ImageComparisonOutputRequester()
        # },
        {
            "add_func": add_InformationSuperhighwayServiceServicer_to_server,
            "add_class": InformationSuperhighway()
        },
    ]

    server = create_secure_server(port, service_classes, server_key, server_cert, ca_cert)
    # server = create_insecure_server(port, service_classes)

    logger.info("Starting server on %s", port)
    await server.start()
    logger.info(f"Server started. Listening on port {port}...")
    await server.wait_for_termination()


if __name__ == '__main__':
    asyncio.run(serve())
