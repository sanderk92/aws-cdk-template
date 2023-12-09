import aws_cdk.aws_iam as iam
from aws_cdk import Stack
from constructs import Construct


# TODO group with minimal required permissions
class Permissions(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs: object) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.create_group()

    def create_group(self) -> iam.Group:
        policy = iam.ManagedPolicy(
            self, "AdminGroupAdditional",
            managed_policy_name="AdminAdditional",
            statements=[iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "ec2:Describe*",
                    "iam:ListRoles",
                    "sts:AssumeRole",
                    "tag:GetResources",
                    "cloudformation:*"
                ],
                resources=["*"]
            )]
        )

        group = iam.Group(
            self, "AdminGroup",
            group_name="Admin",
            managed_policies=[
                policy,
                iam.ManagedPolicy.from_aws_managed_policy_name("AdministratorAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEC2ContainerRegistryFullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEC2FullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonECS_FullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonElasticContainerRegistryPublicFullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMFullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AWSCloudFormationFullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("IAMFullAccess"),
            ]
        )

        return group
