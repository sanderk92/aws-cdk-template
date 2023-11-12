import aws_cdk.aws_ecr as ecr
from aws_cdk import Stack
from constructs import Construct


class Registries(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs: object) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.create_registries()

    def create_registries(self):
        ecr.Repository(
            self, "FrontendRegistry",
            repository_name="frontend-registry"
        )

        ecr.Repository(
            self, "BackendRegistry",
            repository_name="backend-registry"
        )
