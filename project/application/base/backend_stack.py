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
import aws_cdk.aws_secretsmanager as sm
from aws_cdk import Duration
from aws_cdk import Size

from project.application.base.stack_base import StackBase

ECR_NAME = "backend-registry"
REGIONAL_SSL_CERT_ARN = "arn:aws:acm:eu-west-1:046201199215:certificate/1934a654-53e7-4c68-99ff-9e72b1ab212a"


class BackendStack(StackBase):
    """
    This class contains the basic methods and properties required for backend deployment
    """

    '''
    The SSL certificate for the backend is different from the frontend, as ECS load balancers are hosted
    at the regional level, for which certs are defined in the eu-west-1 region.
    '''

    def fetch_regional_ssl_cert(self) -> cert.ICertificate:
        return self.fetch_ssl_cert("RegionalTLSCertificate", REGIONAL_SSL_CERT_ARN)

    '''
    Registries should only be created once, and imported afterwards. Creation of this resource is stored
    as a separate stack.
    '''

    def fetch_registry(self) -> ecr.IRepository:
        ecs_role = iam.Role(
            self, "EcsTaskRole",
            assumed_by=iam.ServicePrincipal('ecs-tasks.amazonaws.com')
        )

        backend_ecr = ecr.Repository.from_repository_name(
            self, "BackendRegistry",
            repository_name=ECR_NAME,
        )

        backend_ecr.grant_pull(ecs_role)

        return backend_ecr

    '''
    Clusters can be created whenever required
    '''

    def create_cluster(self, name: str) -> ecs.Cluster:
        return ecs.Cluster(
            self, f"{name}Cluster",
            cluster_name=name
        )

    '''
    Backend task definitions and services can be recreated for each update required
    '''

    def create_service(
            self,
            cluster: ecs.ICluster,
            cluster_name: str,
            backend_ecr: ecr.IRepository,
            ssl_cert: cert.ICertificate,
            backend_cognito_client: cognito.UserPoolClient,
            swagger_cognito_client: cognito.UserPoolClient,
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
            environment=dict(
                SPRING_PROFILES_ACTIVE=cluster_name.lower(),
                OIDC_SWAGGER_CLIENT_ID=swagger_cognito_client.user_pool_client_id,
                OIDC_SERVER_CLIENT_ID=backend_cognito_client.user_pool_client_id,
                # TODO This should be passed as a secret instead
                OIDC_SERVER_CLIENT_SECRET=backend_cognito_client.user_pool_client_secret.unsafe_unwrap(),
            ),
            secrets=dict(
                SERVER_HOST=self.fetch_secret(f"{cluster_name}Secrets", "ServerHost"),
                DATABASE_URL=self.fetch_secret(f"{cluster_name}Secrets", "DatabaseUrl"),
                DATABASE_DIALECT=self.fetch_secret(f"{cluster_name}Secrets", "DatabaseDialect"),
                DATABASE_USERNAME=self.fetch_secret(f"{cluster_name}Secrets", "DatabaseUsername"),
                DATABASE_PASSWORD=self.fetch_secret(f"{cluster_name}Secrets", "DatabasePassword"),
                OIDC_PROVIDER_CONFIG_URL=self.fetch_secret(f"{cluster_name}Secrets", "OidcConfigUrl"),
                OIDC_PROVIDER_JWK_URL=self.fetch_secret(f"{cluster_name}Secrets", "OidcJwkUrl"),
                OIDC_USER_INFO_ENDPOINT=self.fetch_secret(f"{cluster_name}Secrets", "OidcUserInfoEndpoint"),
            ),
            port_mappings=[ecs.PortMapping(
                container_port=8080,
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
            # TODO This should use actuator to check health
            health_check_grace_period=Duration.seconds(180),
        )

        return backend_service

    '''
    Secrets can be created manually. With this method, a single environment variables can be fetched from a 
    multi key-value pair secret. 
    '''

    def fetch_secret(self, name: str, field: str) -> ecs.Secret:
        return ecs.Secret.from_secrets_manager(
            field=field,
            secret=sm.Secret.from_secret_name_v2(
                self,
                id=str(uuid.uuid4()),
                secret_name=name
            )
        )

    ''' 
    DNS Records may be recreated at any time
    '''

    def create_dns_record(
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
    Authentication clients can be recreated at any time, as their values are passed through cdk
    '''

    @staticmethod
    def create_authentication_client(user_pool: cognito.IUserPool, domain_name: str) -> cognito.UserPoolClient:
        client = user_pool.add_client(
            id=f"BackendClient:{domain_name}",
            access_token_validity=Duration.hours(1),
            generate_secret=True,
            o_auth=cognito.OAuthSettings(
                flows=cognito.OAuthFlows(
                    authorization_code_grant=True,
                ),
            ),
        )
        return client

    '''
    Authentication clients can be recreated at any time, as their values are passed through cdk
    '''

    @staticmethod
    def create_swagger_authentication_client(user_pool: cognito.IUserPool, domain_name: str) -> cognito.UserPoolClient:
        client = user_pool.add_client(
            id=f"SwaggerClient:{domain_name}",
            access_token_validity=Duration.hours(1),
            generate_secret=False,
            o_auth=cognito.OAuthSettings(
                callback_urls=[f"https://{domain_name}/swagger-ui/oauth2-redirect.html"],
                flows=cognito.OAuthFlows(
                    authorization_code_grant=True,
                ),
            ),
        )
        return client
