import uuid

import aws_cdk.aws_certificatemanager as cert
import aws_cdk.aws_cognito as cognito
import aws_cdk.aws_ecr as ecr
import aws_cdk.aws_ecs as ecs
import aws_cdk.aws_ecs_patterns as ecsp
import aws_cdk.aws_elasticloadbalancingv2 as elbv2
import aws_cdk.aws_iam as iam
import aws_cdk.aws_route53 as r53
import aws_cdk.aws_route53_targets as r53_targets
from aws_cdk import Stack, Duration, Size, RemovalPolicy
from constructs import Construct

TOP_DOMAIN = "com"
SECOND_LVL_DOMAIN = "sanderkrabbenborg"

PRD_FE_DOMAIN = f"{SECOND_LVL_DOMAIN}.{TOP_DOMAIN}"
PRD_BE_DOMAIN = f"api.{SECOND_LVL_DOMAIN}.{TOP_DOMAIN}"
ACC_FE_DOMAIN = f"acc.{SECOND_LVL_DOMAIN}.{TOP_DOMAIN}"
ACC_BE_DOMAIN = f"api.acc.{SECOND_LVL_DOMAIN}.{TOP_DOMAIN}"
TST_FE_DOMAIN = f"tst.{SECOND_LVL_DOMAIN}.{TOP_DOMAIN}"
TST_BE_DOMAIN = f"api.tst.{SECOND_LVL_DOMAIN}.{TOP_DOMAIN}"

FE_ECR_NAME = "frontend-registry"
BE_ECR_NAME = "backend-registry"

SSL_CERT_ARN = "arn:aws:acm:eu-west-1:046201199215:certificate/1934a654-53e7-4c68-99ff-9e72b1ab212a"


# TODO Setup applications environment variables
# TODO Frontend + Backend must publish to ECR
# TODO Frontend must handle this domain scheme
# TODO Backend must allow CORS for this domain scheme
class ProjectName(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs: object) -> None:
        super().__init__(scope, construct_id, **kwargs)

        backend_ecr, frontend_ecr = self.fetch_registries()
        ssl_cert = self.fetch_ssl_cert()
        hosted_zone = self.fetch_hosted_zone()
        auth_server = self.authentication_server()

        clusters = [
            # ("Prd", PRD_FE_DOMAIN, PRD_BE_DOMAIN),
            ("Acc", ACC_FE_DOMAIN, ACC_BE_DOMAIN),
            # ("Tst", TST_FE_DOMAIN, TST_BE_DOMAIN),
        ]

        for (cluster_name, frontend_domain, backend_domain) in clusters:
            cluster = self.create_cluster(cluster_name)
            frontend = self.frontend(cluster, cluster_name, frontend_ecr, ssl_cert)
            backend = self.backend(cluster, cluster_name, backend_ecr, ssl_cert)

            self.authentication_client(auth_server, False)
            self.authentication_client(auth_server, True)
            self.dns_record(hosted_zone, frontend.load_balancer, frontend_domain)
            self.dns_record(hosted_zone, backend.load_balancer, backend_domain)

    '''
     Clusters can be removed and created at any time as long as all containers have stopped
    '''

    def create_cluster(self, name: str) -> ecs.Cluster:
        return ecs.Cluster(
            self, f"{name}Cluster",
            cluster_name=name
        )

    '''
     SSL Certs should be created through the ui/cli for a each domain in combination with route 53 registrations. This 
     single cert should contain all the subdomains applicable.
    '''

    def fetch_ssl_cert(self) -> cert.ICertificate:
        return cert.Certificate.from_certificate_arn(
            self, "TLSCertificate",
            certificate_arn=SSL_CERT_ARN,
        )

    '''
     Hosted zones are automatically created when ssl certs are issues by AWS. Do not remove manually, CDK won't either.
    '''

    def fetch_hosted_zone(self) -> r53.IHostedZone:
        return r53.HostedZone.from_lookup(
            self, "HostedZone",
            domain_name=f"{SECOND_LVL_DOMAIN}.{TOP_DOMAIN}"
        )

    '''
     Registries should only be created once (manually/cdk), and imported afterwards
    '''

    def fetch_registries(self) -> [ecr.IRepository, ecr.IRepository]:
        ecs_role = iam.Role(
            self, "EcsTaskRole",
            assumed_by=iam.ServicePrincipal('ecs-tasks.amazonaws.com')
        )

        frontend_ecr = ecr.Repository.from_repository_name(
            self, "FrontendRegistry",
            repository_name=FE_ECR_NAME
        )

        backend_ecr = ecr.Repository.from_repository_name(
            self, "BackendRegistry",
            repository_name=BE_ECR_NAME,
        )

        frontend_ecr.grant_pull(ecs_role)
        backend_ecr.grant_pull(ecs_role)
        return backend_ecr, frontend_ecr

    '''
     Frontend task definitions and services can be recreated for each update required
    '''

    def frontend(
            self,
            cluster: ecs.Cluster,
            cluster_name: str,
            frontend_ecr: ecr.IRepository,
            ssl_cert: cert.ICertificate,
    ) -> ecsp.ApplicationLoadBalancedFargateService:
        frontend_task = ecs.FargateTaskDefinition(
            self, cluster_name + "FrontendTask",
            cpu=256,
            memory_limit_mib=512,
        )

        frontend_task.add_container(
            str(uuid.uuid4()),
            image=ecs.ContainerImage.from_ecr_repository(frontend_ecr, "latest"),
            container_name=cluster_name + "FrontendContainer",
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix=cluster_name.lower(),
                mode=ecs.AwsLogDriverMode.NON_BLOCKING,
                max_buffer_size=Size.mebibytes(1),
            ),
            port_mappings=[ecs.PortMapping(
                container_port=8080,
            )]
        )

        frontend_service = ecsp.ApplicationLoadBalancedFargateService(
            self, str(uuid.uuid4()),
            certificate=ssl_cert,
            service_name=cluster_name + "FrontendService",
            cluster=cluster,
            public_load_balancer=True,
            redirect_http=True,
            desired_count=1,
            task_definition=frontend_task,
            health_check_grace_period=Duration.seconds(60),
        )
        return frontend_service

    '''
     Backend task definitions and services can be recreated for each update required
    '''

    def backend(
            self,
            cluster: ecs.ICluster,
            cluster_name: str,
            backend_ecr: ecr.IRepository,
            ssl_cert: cert.ICertificate,
    ) -> ecsp.ApplicationLoadBalancedFargateService:
        backend_task = ecs.FargateTaskDefinition(
            self, cluster_name + "BackendTask",
            cpu=256,
            memory_limit_mib=512,
        )

        backend_task.add_container(
            str(uuid.uuid4()),
            image=ecs.ContainerImage.from_ecr_repository(backend_ecr, "latest"),
            container_name=cluster_name + "BackendContainer",
            port_mappings=[ecs.PortMapping(
                container_port=5050,
            )],
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix=cluster_name.lower(),
                mode=ecs.AwsLogDriverMode.NON_BLOCKING,
                max_buffer_size=Size.mebibytes(1),
            ),
        )

        backend_service = ecsp.ApplicationLoadBalancedFargateService(
            self, str(uuid.uuid4()),
            certificate=ssl_cert,
            service_name=cluster_name + "BackendService",
            cluster=cluster,
            public_load_balancer=True,
            redirect_http=True,
            desired_count=1,
            task_definition=backend_task,
            health_check_grace_period=Duration.seconds(60),
        )
        return backend_service

    ''' 
     DNS Records may be recreated at any time
    '''

    def dns_record(
            self,
            hosted_zone: r53.IHostedZone,
            loadbalancer: elbv2.IApplicationLoadBalancer,
            domain_name: str,
    ) -> r53.ARecord:
        return r53.ARecord(
            self, str(uuid.uuid4()),
            zone=hosted_zone,
            delete_existing=False,
            record_name=domain_name,
            target=r53.RecordTarget.from_alias(r53_targets.LoadBalancerTarget(loadbalancer)),
        )

    '''
    Auth server must be retained after automatically created; do not remove.
    '''

    def authentication_server(self) -> cognito.IUserPool:
        user_pool = cognito.UserPool(
            self, "AuthenticationProvider",
            self_sign_up_enabled=True,
            sign_in_aliases=cognito.SignInAliases(
                email=True,
                phone=False,
                username=False,
                preferred_username=False,
            ),
            auto_verify=cognito.AutoVerifiedAttrs(
                email=True,
                phone=False,
            ),
            user_verification=cognito.UserVerificationConfig(
                email_subject="Verify your email",
                email_body="The code to verify your email is {####}",
                email_style=cognito.VerificationEmailStyle.CODE,
            ),
            standard_attributes=cognito.StandardAttributes(
                given_name=cognito.StandardAttribute(
                    mutable=False,
                    required=True,
                ),
                family_name=cognito.StandardAttribute(
                    mutable=False,
                    required=True,
                ),
                email=cognito.StandardAttribute(
                    mutable=False,
                    required=True,
                ),
                preferred_username=cognito.StandardAttribute(
                    mutable=False,
                    required=True,
                ),
            ),
            password_policy=cognito.PasswordPolicy(
                min_length=8,
                require_uppercase=True,
                require_lowercase=True,
                require_digits=True,
                require_symbols=True,
            ),
            account_recovery=cognito.AccountRecovery.EMAIL_ONLY,
            removal_policy=RemovalPolicy.RETAIN,
        )

        user_pool.add_domain(
            id=str(uuid.uuid4()),
            cognito_domain=cognito.CognitoDomainOptions(
                domain_prefix=SECOND_LVL_DOMAIN.lower(),
            )
        )
        return user_pool

    @staticmethod
    def authentication_client(user_pool: cognito.IUserPool, generate_secret: bool) -> cognito.UserPoolClient:
        client = user_pool.add_client(
            id=str(uuid.uuid4()),
            access_token_validity=Duration.hours(1),
            generate_secret=generate_secret,
            o_auth=cognito.OAuthSettings(
                flows=cognito.OAuthFlows(
                    authorization_code_grant=True,
                ),
            ),
        )
        return client
