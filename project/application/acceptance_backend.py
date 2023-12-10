from constructs import Construct

from project.application.base.backend_stack import BackendStack
from project.application.base.stack_base import SECOND_LVL_DOMAIN, TOP_DOMAIN

CLUSTER_NAME = "Acc"

BE_DOMAIN = f"api.acc.{SECOND_LVL_DOMAIN}.{TOP_DOMAIN}"


class AcceptanceBackend(BackendStack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs: object) -> None:
        super().__init__(scope, construct_id, **kwargs)

        registry = self.fetch_registry()
        hosted_zone = self.fetch_hosted_zone()
        ssl_cert = self.fetch_regional_ssl_cert()

        auth_server = self.fetch_authentication_server()
        server_client = self.create_server_authentication_client(auth_server, CLUSTER_NAME)
        swagger_client = self.create_swagger_authentication_client(auth_server, CLUSTER_NAME, BE_DOMAIN)

        cluster = self.create_cluster(CLUSTER_NAME)
        backend = self.create_service(cluster, CLUSTER_NAME, registry, ssl_cert, server_client, swagger_client)
        self.create_dns_record(hosted_zone, backend.load_balancer, BE_DOMAIN)
