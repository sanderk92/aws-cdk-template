import uuid

import aws_cdk.aws_certificatemanager as cert
import aws_cdk.aws_cognito as cognito
import aws_cdk.aws_route53 as r53
from aws_cdk import Stack

TOP_DOMAIN = "com"
SECOND_LVL_DOMAIN = "sanderkrabbenborg"
USER_POOL_ID = "eu-west-1_6wOiibFgH"


class StackBase(Stack):

    """
    The stack base contains methods and information required by any application in any cluster to deploy.
    """

    '''
    SSL Certs should be created through the ui/cli in combination with route 53 registrations. This 
    single cert should contain all the subdomains applicable, such as those with acc and tst prefixes.
    '''

    def fetch_ssl_cert(self, resource_id: str, certificate_arn: str) -> cert.ICertificate:
        return cert.Certificate.from_certificate_arn(
            self, resource_id,
            certificate_arn=certificate_arn,
        )

    '''
    Hosted zones are automatically created when ssl certs are issues by AWS. Do not remove manually.
    '''

    def fetch_hosted_zone(self) -> r53.IHostedZone:
        return r53.HostedZone.from_lookup(
            self, "HostedZone",
            domain_name=f"{SECOND_LVL_DOMAIN}.{TOP_DOMAIN}"
        )

    '''
    Authentication server should only be created once, and imported afterwards. Creation of this resource
    is stored as a separate stack.
    '''

    def fetch_authentication_server(self) -> cognito.IUserPool:
        return cognito.UserPool.from_user_pool_id(
            self,
            id=str(uuid.uuid4()),
            user_pool_id=USER_POOL_ID,
        )
