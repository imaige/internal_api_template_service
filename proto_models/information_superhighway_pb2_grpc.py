# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from . import information_superhighway_pb2 as information__superhighway__pb2


class InformationSuperhighwayServiceStub(object):
    """Service definition
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.ImageAiAnalysisRequest = channel.unary_unary(
                '/information_superhighway.InformationSuperhighwayService/ImageAiAnalysisRequest',
                request_serializer=information__superhighway__pb2.ImageAnalysisRequest.SerializeToString,
                response_deserializer=information__superhighway__pb2.SuperhighwayStatusReply.FromString,
                )


class InformationSuperhighwayServiceServicer(object):
    """Service definition
    """

    def ImageAiAnalysisRequest(self, request, context):
        """AI analysis request
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_InformationSuperhighwayServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'ImageAiAnalysisRequest': grpc.unary_unary_rpc_method_handler(
                    servicer.ImageAiAnalysisRequest,
                    request_deserializer=information__superhighway__pb2.ImageAnalysisRequest.FromString,
                    response_serializer=information__superhighway__pb2.SuperhighwayStatusReply.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'information_superhighway.InformationSuperhighwayService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class InformationSuperhighwayService(object):
    """Service definition
    """

    @staticmethod
    def ImageAiAnalysisRequest(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/information_superhighway.InformationSuperhighwayService/ImageAiAnalysisRequest',
            information__superhighway__pb2.ImageAnalysisRequest.SerializeToString,
            information__superhighway__pb2.SuperhighwayStatusReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
