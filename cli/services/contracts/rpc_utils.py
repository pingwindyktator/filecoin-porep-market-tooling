from cli.services.contracts.contract_service import ContractService
from web3.types import RPCEndpoint

from cli import utils

class RPCUtils:
    @staticmethod
    def get_state_client_allocations(actor_id: int) -> dict:
        method = "Filecoin.StateGetAllocations"
        response = ContractService.get_w3().provider.make_request(
            RPCEndpoint(method),
            [utils.int_id_to_f0_str(actor_id), None]
        )

        if "error" in response:
            raise Exception(response["error"])

        return response["result"]
    