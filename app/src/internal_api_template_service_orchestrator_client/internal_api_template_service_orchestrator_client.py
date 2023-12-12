import grpc
from proto_models.internal_api_template_service_pb2 import (
    TemplateRequest, TemplateReply
)
from proto_models.internal_api_template_service_pb2_grpc import (
    InternalApiTemplateServiceStub
)
from ...libraries.logging_file_format import configure_logger

import asyncio
import logging


logger = logging.getLogger(__name__)
configure_logger(logger, level=logging.INFO)


async def run() -> None:
    # logging.basicConfig(level=logging.INFO)
    # client_key = open('../tls_certs/client-key.pem', 'rb').read()
    # client_cert = open('../tls_certs/client-cert.pem', 'rb').read()
    # ca_cert = open('../tls_certs/ca-cert.pem', 'rb').read()

    # channel_credentials = grpc.ssl_channel_credentials(
    #     root_certificates=ca_cert, private_key=client_key, certificate_chain=client_cert
    # )

    # async with grpc.aio.secure_channel("localhost:50051", channel_credentials) as channel:
    async with grpc.aio.insecure_channel("localhost:50051") as channel:
        stub = InternalApiTemplateServiceStub(channel)
        test_stream = stub.InternalApiTemplateRequest(
            TemplateRequest(name="Caleb")
        )

        logger.info("Client making InternalApiTemplateRequest")
        async for response in stub.InternalApiTemplateRequest(TemplateRequest(name="Caleb")):
            logger.info("Client received from async generator: " + response.message)

            #
            # stream = await test_stream
            # print("stream: "+stream)
            # response = stream.read()
            # print("response: " + response)
            # if response == grpc.aio.EOF:
            #     break
            # print(
            #     "Client received from direct read: " + response.message
            # )

if __name__ == '__main__':
    logging.basicConfig()
    asyncio.run(run())
