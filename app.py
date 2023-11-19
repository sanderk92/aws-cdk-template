#!/usr/bin/env python3

import aws_cdk as cdk

from project.application.acceptance_backend import AcceptanceBackend
from project.application.acceptance_frontend import AcceptanceFrontend
from project.application.production_backend import ProductionBackend
from project.application.production_frontend import ProductionFrontend
from project.infrastructure.authentication import Authentication
from project.infrastructure.registries import Registries

app = cdk.App()

# TODO Fetch account from env variable
env = cdk.Environment(account="046201199215", region="eu-west-1")

Registries(app, "ImageRegistries", env=env)
Authentication(app, "AuthenticationServer", env=env)

ProductionBackend(app, "ProductionBackend", env=env)
ProductionFrontend(app, "ProductionFrontend", env=env)
AcceptanceBackend(app, "AcceptanceBackend", env=env)
AcceptanceFrontend(app, "AcceptanceFrontend", env=env)

app.synth()
