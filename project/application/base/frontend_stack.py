import uuid

import aws_cdk.aws_cloudfront as cf
import aws_cdk.aws_cloudfront_origins as cfo
import aws_cdk.aws_cognito as cognito
import aws_cdk.aws_iam as iam
import aws_cdk.aws_route53 as r53
import aws_cdk.aws_certificatemanager as cert
import aws_cdk.aws_route53_targets as r53_targets
import aws_cdk.aws_s3 as s3
from aws_cdk import Duration
from aws_cdk import RemovalPolicy

from project.application.base.stack_base import StackBase

GLOBAL_SSL_CERT_ARN = "arn:aws:acm:us-east-1:046201199215:certificate/263923ff-71c4-4630-b93b-5a3fca30e9dd"


class FrontendStack(StackBase):
    """
    This class contains the basic methods and properties required for frontend deployment
    """

    '''
    The SSL certificate for the frontend is different from the backend, as S3 buckets are always hosted
    at the global level, for which certs are defined in the us-east-1 region.
    '''

    def fetch_global_ssl_cert(self) -> cert.ICertificate:
        return self.fetch_ssl_cert("GlobalTLSCertificate", GLOBAL_SSL_CERT_ARN)

    '''
    Frontend bucket should not be recreated, as the name must be unique and equal to our domain
    '''

    def create_bucket(
            self,
            cluster_name: str,
            domain_name: str,
    ) -> s3.Bucket:
        # TODO currently requires client id set in source code
        bucket = s3.Bucket(
            self,
            f"{cluster_name}FrontendBucket",
            encryption=s3.BucketEncryption.S3_MANAGED,
            enforce_ssl=True,
            versioned=False,
            public_read_access=True,
            bucket_name=domain_name,
            website_index_document="index.html",
            website_error_document="index.html",
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=False,
                block_public_policy=False,
                ignore_public_acls=False,
                restrict_public_buckets=False,
            ),
            # TODO check if this cors rule is required
            cors=[s3.CorsRule(
                allowed_headers=["*"],
                allowed_origins=["*"],
                allowed_methods=[
                    s3.HttpMethods.GET,
                    s3.HttpMethods.DELETE,
                    s3.HttpMethods.PUT,
                    s3.HttpMethods.POST,
                    s3.HttpMethods.HEAD
                ],
            )],
            # TODO set to retain as bucket names are unique
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        # TODO this bucket policy still requires manual deletion 'DENY *'
        bucket.grant_read(iam.AnyPrincipal())

        return bucket

    ''' 
    Distributions may be recreated at any time
    '''

    def create_distribution(self, bucket: s3.Bucket, ssl_cert: cert.ICertificate, cluster_name: str, domain_name: str):
        return cf.Distribution(
            self,
            f"{cluster_name}FrontendDistribution",
            certificate=ssl_cert,
            domain_names=[domain_name],
            enabled=True,
            default_behavior=cf.BehaviorOptions(
                origin=cfo.S3Origin(
                    bucket=bucket,
                )
            ),
            price_class=cf.PriceClass.PRICE_CLASS_ALL
        )

    ''' 
    DNS Records may be recreated at any time
    '''

    def create_dns_record(
            self,
            cloudfront: cf.Distribution,
            domain_name: str,
            hosted_zone: r53.IHostedZone
    ) -> r53.ARecord:
        return r53.ARecord(
            self, str(uuid.uuid4()),
            zone=hosted_zone,
            delete_existing=False,
            record_name=domain_name,
            target=r53.RecordTarget.from_alias(r53_targets.CloudFrontTarget(cloudfront)),
        )

    '''
    Authentication clients can be recreated at any time, as their values are passed through cdk
    '''

    @staticmethod
    def create_authentication_client(user_pool: cognito.IUserPool, domain_name: str) -> cognito.UserPoolClient:
        return user_pool.add_client(
            id=f"FrontendClient:{domain_name}",
            access_token_validity=Duration.hours(1),
            generate_secret=False,
            o_auth=cognito.OAuthSettings(
                callback_urls=[f"https://{domain_name}"],
                flows=cognito.OAuthFlows(
                    authorization_code_grant=True,
                ),
            ),
        )
