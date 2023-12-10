import aws_cdk.aws_certificatemanager as cert
import aws_cdk.aws_cloudfront as cf
import aws_cdk.aws_cloudfront_origins as cfo
import aws_cdk.aws_cognito as cognito
import aws_cdk.aws_iam as iam
import aws_cdk.aws_route53 as r53
import aws_cdk.aws_route53_targets as r53_targets
import aws_cdk.aws_s3 as s3
from aws_cdk import Duration
from aws_cdk import RemovalPolicy

from app_config import GLOBAL_SSL_CERT_ARN
from project.application.base.stack_base import StackBase


class FrontendStack(StackBase):
    """
    This class contains the basic methods and properties required for frontend deployment
    """

    '''
    The SSL certificate for the frontend is different from the backend, as S3 buckets are always hosted
    at the global level, for which certs are defined in the us-east-1 region.
    '''

    def fetch_global_ssl_cert(self) -> cert.ICertificate:
        return self.fetch_ssl_cert("GlobalTLSCertificateImport", GLOBAL_SSL_CERT_ARN)

    '''
    Frontend bucket should not be recreated, as the name must be unique and equal to our domain
    '''

    def create_bucket(self, cluster_name: str, domain_name: str) -> s3.Bucket:
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
            removal_policy=RemovalPolicy.RETAIN,
        )

        # TODO this bucket policy still requires manual deletion: 'DENY *'
        bucket.grant_read(iam.AnyPrincipal())

        return bucket

    def create_distribution(self, bucket: s3.Bucket, ssl_cert: cert.ICertificate, cluster_name: str, domain_name: str):
        return cf.Distribution(
            self,
            f"{cluster_name}FrontendDistribution",
            certificate=ssl_cert,
            domain_names=[f"www.{domain_name}", domain_name],
            enabled=True,
            default_behavior=cf.BehaviorOptions(
                origin=cfo.S3Origin(
                    bucket=bucket,
                )
            ),
            price_class=cf.PriceClass.PRICE_CLASS_ALL
        )

    def create_dns_records(
            self,
            cloudfront: cf.Distribution,
            domain_name: str,
            hosted_zone: r53.IHostedZone
    ) -> [r53.ARecord, r53.CnameRecord]:
        top_domain_record = r53.ARecord(
            self, f"FrontendDnsRecord:{domain_name}",
            zone=hosted_zone,
            delete_existing=False,
            record_name=domain_name,
            target=r53.RecordTarget.from_alias(r53_targets.CloudFrontTarget(cloudfront)),
        )

        www_subdomain_record = r53.CnameRecord(
            self, f"FrontendDnsRecord:www.{domain_name}",
            zone=hosted_zone,
            delete_existing=False,
            record_name="www",
            domain_name=domain_name,
        )

        return top_domain_record, www_subdomain_record

    @staticmethod
    def create_web_client(user_pool: cognito.IUserPool, cluster_name: str, domain_name: str) -> cognito.UserPoolClient:
        return user_pool.add_client(
            id=f"{cluster_name}FrontendClient",
            access_token_validity=Duration.hours(1),
            generate_secret=False,
            o_auth=cognito.OAuthSettings(
                callback_urls=[f"https://{domain_name}/redirect/"],
                flows=cognito.OAuthFlows(
                    authorization_code_grant=True,
                ),
            ),
        )
