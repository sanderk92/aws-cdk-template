import aws_cdk.aws_cognito as cognito
from aws_cdk import Stack, RemovalPolicy
from constructs import Construct

SERVER_PREFIX = "sanderkrabbenborg"


class Authentication(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs: object) -> None:
        super().__init__(scope, construct_id, **kwargs)
        user_pool = self.create_authentication_server()
        self.add_cognito_domain(user_pool)

    '''
    Auth server must be retained after automatically created; do not remove.
    '''

    def create_authentication_server(self) -> cognito.IUserPool:
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

        return user_pool

    '''
     The domain registry under which the authentication server is accessible.
    '''

    @staticmethod
    def add_cognito_domain(user_pool):
        user_pool.add_domain(
            id="AuthenticationProviderCognitoDomain",
            cognito_domain=cognito.CognitoDomainOptions(
                domain_prefix=SERVER_PREFIX.lower(),
            )
        )
