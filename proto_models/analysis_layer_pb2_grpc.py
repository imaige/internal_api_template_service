# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from . import analysis_layer_pb2 as analysis__layer__pb2


class AnalysisLayerStub(object):
    """Service definition
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.AiModelOutputRequestHandler = channel.unary_stream(
                '/information_superhighway.AnalysisLayer/AiModelOutputRequestHandler',
                request_serializer=analysis__layer__pb2.AiModelOutputRequest.SerializeToString,
                response_deserializer=analysis__layer__pb2.StatusReply.FromString,
                )


class AnalysisLayerServicer(object):
    """Service definition
    """

    def AiModelOutputRequestHandler(self, request, context):
        """AI output request
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_AnalysisLayerServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'AiModelOutputRequestHandler': grpc.unary_stream_rpc_method_handler(
                    servicer.AiModelOutputRequestHandler,
                    request_deserializer=analysis__layer__pb2.AiModelOutputRequest.FromString,
                    response_serializer=analysis__layer__pb2.StatusReply.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'information_superhighway.AnalysisLayer', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class AnalysisLayer(object):
    """Service definition
    """

    @staticmethod
    def AiModelOutputRequestHandler(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/information_superhighway.AnalysisLayer/AiModelOutputRequestHandler',
            analysis__layer__pb2.AiModelOutputRequest.SerializeToString,
            analysis__layer__pb2.StatusReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
