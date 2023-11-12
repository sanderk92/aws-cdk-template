from constructs import Construct

from project.application.base.cluster_stack import ClusterStack, SECOND_LVL_DOMAIN, TOP_DOMAIN

CLUSTER_NAME = "Prd"

FE_DOMAIN = f"{SECOND_LVL_DOMAIN}.{TOP_DOMAIN}"
BE_DOMAIN = f"api.{SECOND_LVL_DOMAIN}.{TOP_DOMAIN}"


class Production(ClusterStack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs: object) -> None:
        super().__init__(scope, construct_id, **kwargs)

        ssl_cert = self.fetch_ssl_cert()
        hosted_zone = self.fetch_hosted_zone()
        backend_ecr, frontend_ecr = self.fetch_registries()

        auth_server = self.fetch_authentication_server()

        cluster = self.create_cluster(CLUSTER_NAME)
        frontend = self.create_frontend(cluster, CLUSTER_NAME, frontend_ecr, ssl_cert)
        backend = self.create_backend(cluster, CLUSTER_NAME, backend_ecr, ssl_cert)

        self.create_frontend_authentication_client(auth_server, FE_DOMAIN)
        self.create_backend_authentication_client(auth_server, BE_DOMAIN)
        self.create_swagger_authentication_client(auth_server, BE_DOMAIN)
        self.create_dns_record(hosted_zone, frontend.load_balancer, FE_DOMAIN)
        self.create_dns_record(hosted_zone, backend.load_balancer, BE_DOMAIN)
