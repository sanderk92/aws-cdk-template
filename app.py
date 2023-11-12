#!/usr/bin/env python3

import aws_cdk as cdk

from project.application.acceptance import Acceptance
from project.application.production import Production
from project.infrastructure.authentication import Authentication
from project.infrastructure.registries import Registries

app = cdk.App()
env = cdk.Environment(account="046201199215", region="eu-west-1")

Production(app, "ProductionStack", env=env)
Acceptance(app, "AcceptanceStack", env=env)
Authentication(app, "AuthenticationStack", env=env)
Registries(app, "RegistriesStack", env=env)

app.synth()
