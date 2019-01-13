from abc import ABC, abstractmethod
from .json_rpc import Request, Response


# handler for client
class IClientHandler(ABC):
    @abstractmethod
    def process_response(self, req: Request, resp: Response):
        pass

    @abstractmethod
    def process_request(self, req: Request):
        pass
