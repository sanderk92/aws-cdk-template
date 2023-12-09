from constructs import Construct

from project.application.base.frontend_stack import FrontendStack
from project.application.base.stack_base import SECOND_LVL_DOMAIN, TOP_DOMAIN

CLUSTER_NAME = "Prd"

FE_DOMAIN = f"{SECOND_LVL_DOMAIN}.{TOP_DOMAIN}"


class ProductionFrontend(FrontendStack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs: object) -> None:
        super().__init__(scope, construct_id, **kwargs)

        hosted_zone = self.fetch_hosted_zone()
        ssl_cert = self.fetch_global_ssl_cert()

        auth_server = self.fetch_authentication_server()
        self.create_authentication_client(auth_server, FE_DOMAIN)

        bucket = self.create_bucket(CLUSTER_NAME, FE_DOMAIN)
        cloudfront = self.create_distribution(bucket, ssl_cert, CLUSTER_NAME, FE_DOMAIN)
        self.create_dns_records(cloudfront, FE_DOMAIN, hosted_zone)
