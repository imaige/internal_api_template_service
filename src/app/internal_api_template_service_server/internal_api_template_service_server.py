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

import grpc
import asyncio
from google.rpc import status_pb2, code_pb2, error_details_pb2
from google.protobuf import any_pb2

from collections import deque
import uuid

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


async def process_image_comparison_model(model: str, request_image, photo_id: int, analysis_layer_port: str):
    logger.info(f"starting {model} flow for photo {photo_id}")
    results = []
    try:
        # TODO: this could use better error handling
        image_comparison_output = await kserve_request.image_comparison_request(
            getenv("IMAGE_COMPARISON_MODEL_URL"),
            request_image, model)

        output = image_comparison_output.outputs[0]
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
        result = ({
            "average_hash": average_hash,
            "perceptual_hash": perceptual_hash,
            "difference_hash": difference_hash,
            "wavelet_hash_haar": wavelet_hash_haar,
            "color_hash": color_hash
        })

        logger.info(f"for id {photo_id}, returning output: {result}")
        return result

    except Exception as e:
        logger.error(f"Caught error processing {model} for photo {photo_id}: {e}")
        code = code_pb2.INVALID_ARGUMENT
        details = any_pb2.Any()
        details.Pack(
            error_details_pb2.DebugInfo(
                detail=f"Error processing {model} for photo {photo_id}."
            )
        )
        message = "Internal server error."
        response = status_pb2.Status(
            code=code,
            message=message,
            details=[details]
        )
        results.append(response)


async def process_colors_model(model: str, request_image, photo_id: int, analysis_layer_port: str):
    logger.info(f"starting {model} flow for photo {photo_id}")
    results = []
    try:
        colors_output = await kserve_request.colors_request(
            getenv("COLORS_MODEL_URL"),
            request_image, model)

        shape = colors_output.outputs[0].shape[0]
        contents = []
        for j in range(0, shape):
            byte_string = colors_output.outputs[0].contents.bytes_contents[j].decode('utf-8')
            contents.append(byte_string)

        result = {
            "color_averages": json.dumps(contents)
        }

        logger.info(f"for id {photo_id}, returning output: {result}")
        return result

    except Exception as e:
        logger.error(f"Caught error processing {model} for photo {photo_id}: {e}")
        code = code_pb2.INVALID_ARGUMENT
        details = any_pb2.Any()
        details.Pack(
            error_details_pb2.DebugInfo(
                detail=f"Error processing {model} for photo {photo_id}."
            )
        )
        message = "Internal server error."
        response = status_pb2.Status(
            code=code,
            message=message,
            details=[details]
        )
        results.append(response)


async def process_face_detect_model(model: str, request_image, photo_id: int, analysis_layer_port: str):
    logger.info(f"starting {model} flow for photo {photo_id}")
    results = []
    try:
        face_detect_output = await kserve_request.face_detect_request(
            getenv("FACE_DETECT_MODEL_URL"),
            request_image, model
        )

        shape = face_detect_output.outputs[0].shape[0]

        contents = []
        # TODO: once face model decoding is ready, split into the different faces
        contents.extend(face_detect_output.raw_output_contents)

        result = ({
            "bounding_boxes_from_faces_model": shape
        })

        logger.info(f"for id {photo_id}, returning output: {result}")
        return result

    except Exception as e:
        logger.error(f"Caught error processing {model} for photo {photo_id}: {e}")
        code = code_pb2.INVALID_ARGUMENT
        details = any_pb2.Any()
        details.Pack(
            error_details_pb2.DebugInfo(
                detail=f"Error processing {model} for photo {photo_id}."
            )
        )
        message = "Internal server error."
        response = status_pb2.Status(
            code=code,
            message=message,
            details=[details]
        )
        results.append(response)


async def process_image_classification_model(model: str, request_image, photo_id: int, analysis_layer_port: str):
    logger.info(f"starting {model} flow for photo {photo_id}")
    results = []
    try:
        classification_output = await kserve_request.image_classification_request(
            getenv("IMAGE_CLASSIFICATION_MODEL_URL"),
            request_image, model)

        contents = []
        contents.extend(classification_output.raw_output_contents)

        result = ({
            "labels_from_classifications_model": contents
        })

        logger.info(f"for id {photo_id}, returning output: {result}")
        return result

    except Exception as e:
        logger.error(f"Caught error processing {model} for photo {photo_id}: {e}")
        code = code_pb2.INVALID_ARGUMENT
        details = any_pb2.Any()
        details.Pack(
            error_details_pb2.DebugInfo(
                detail=f"Error processing {model} for photo {photo_id}."
            )
        )
        message = "Internal server error."
        # yield status_pb2.Status(
        #     code=code,
        #     message=message,
        #     details=[details]
        # )
        response = status_pb2.Status(
            code=code,
            message=message,
            details=[details]
        )
        results.append(response)


# Service Class Definition #
class InformationSuperhighway(InformationSuperhighwayServiceServicer):
    def __init__(self):
        self.semaphore = asyncio.Semaphore(5)
        self.request_queue = deque()
        self.active_requests = {}

    async def process_queue(self):
        if not self.request_queue:
            return

        async with self.semaphore:
            request_id, request, future = self.request_queue.popleft()
            self.active_requests[request_id] = request
            try:
                results = await self.process_request(request_id, request)
                future.set_result(results)
            except Exception as e:
                logger.error(f"Error processing request {request_id}: {e}")
                future.set_exception(e)
            finally:
                del self.active_requests[request_id]

    async def process_request(self, request_id: str, request: ImageAnalysisRequest):
        logger.info(
            f"Processing request {request_id} for photo id: {request.photo_id} and models: {request.models}"
        )
        request_image = request.b64image
        analysis_layer_port = f'{getenv("ANALYSIS_LAYER_URL")}:80'
        model_functions = {
            "image_comparison_hash_model": process_image_comparison_model,
            "colors_basic_model": process_colors_model,
            "image_classification_model": process_image_classification_model,
            "face_detect_model": process_face_detect_model
        }

        tasks = []
        results = []
        for model in request.models:
            if model in model_functions:
                task = asyncio.create_task(
                    model_functions[model](model, request_image, request.photo_id, analysis_layer_port))
                tasks.append(task)
            else:
                logger.info(f"Provided model name of {model} is invalid.")
                results.append(status_pb2.Status(
                    code=code_pb2.INVALID_ARGUMENT,
                    message="Invalid argument error.",
                    details=[any_pb2.Any().Pack(
                        error_details_pb2.DebugInfo(
                            detail=f"Invalid argument: model name of {model} is invalid."
                        )
                    )]
                ))

        task_results = await asyncio.gather(*tasks, return_exceptions=True)

        combined_result = {}
        for result in task_results:
            if isinstance(result, Exception):
                logger.error(f"Task resulted in an exception: {result}")
                results.append(status_pb2.Status(
                    code=code_pb2.INTERNAL,
                    message="Internal server error.",
                    details=[any_pb2.Any().Pack(
                        error_details_pb2.DebugInfo(
                            detail=f"Error processing model for photo {request.photo_id}."
                        )
                    )]
                ))
            else:
                combined_result.update(result)

        if combined_result:
            analysis_layer_input = AiModelOutputRequest(photo_id=request.photo_id, model_name="all", **combined_result)
            try:
                analysis_layer_response = await analysis_layer_request(analysis_layer_input, analysis_layer_port)
                logger.info(f"response from analysis layer is: {analysis_layer_response}")
                results.append(SuperhighwayStatusReply(message="OK"))
            except Exception as e:
                logger.error(f"Error sending combined results to analysis layer: {e}")
                results.append(status_pb2.Status(
                    code=code_pb2.INTERNAL,
                    message="Analysis layer request error.",
                    details=[any_pb2.Any().Pack(
                        error_details_pb2.DebugInfo(
                            detail=f"Error sending results to analysis layer for photo {request.photo_id}: {str(e)}"
                        )
                    )]
                ))

        return results

    # Endpoint definition #
    # Matches name in InformationSuperhighwayServiceServicer
    async def ImageAiAnalysisRequest(
        self, request: ImageAnalysisRequest, context: grpc.aio.ServicerContext
    ) -> Union[SuperhighwayStatusReply, status_pb2.Status]:
        request_id = str(uuid.uuid4())
        logger.info(
            f"Serving AI model request {request_id} for photo id: {request.photo_id} and models: {request.models}"
        )

        # Add request to queue
        future = asyncio.get_running_loop().create_future()
        self.request_queue.append((request_id, request, future))

        # Start processing if semaphore is available
        asyncio.create_task(self.process_queue())

        try:
            results = await asyncio.wait_for(future, timeout=300)  # 5 minute timeout
            for result in results:
                yield result
        except asyncio.TimeoutError:
            logger.error(f"Request {request_id} timed out")
            yield status_pb2.Status(
                code=code_pb2.DEADLINE_EXCEEDED,
                message="Request processing timed out.",
                details=[any_pb2.Any().Pack(
                    error_details_pb2.DebugInfo(
                        detail=f"Processing for photo {request.photo_id} exceeded time limit."
                    )
                )]
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
