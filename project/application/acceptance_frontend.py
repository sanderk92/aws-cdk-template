from constructs import Construct

from project.application.base.frontend_stack import FrontendStack
from project.application.base.stack_base import SECOND_LVL_DOMAIN, TOP_DOMAIN

CLUSTER_NAME = "Acc"

FE_DOMAIN = f"acc.{SECOND_LVL_DOMAIN}.{TOP_DOMAIN}"


class AcceptanceFrontend(FrontendStack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs: object) -> None:
        super().__init__(scope, construct_id, **kwargs)

        hosted_zone = self.fetch_hosted_zone()
        ssl_cert = self.fetch_global_ssl_cert()

        auth_server = self.fetch_authentication_server()
        self.create_web_client(auth_server, CLUSTER_NAME, FE_DOMAIN)

        bucket = self.create_bucket(CLUSTER_NAME, FE_DOMAIN)
        cloudfront = self.create_distribution(bucket, ssl_cert, CLUSTER_NAME, FE_DOMAIN)
        self.create_dns_records(cloudfront, FE_DOMAIN, hosted_zone)
