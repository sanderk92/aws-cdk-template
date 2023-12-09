#!/usr/bin/env python3

import aws_cdk as cdk

from project.application.acceptance_backend import AcceptanceBackend
from project.application.acceptance_frontend import AcceptanceFrontend
from project.application.production_backend import ProductionBackend
from project.application.production_frontend import ProductionFrontend
from project.infrastructure.authentication import Authentication
from project.infrastructure.permissions import Permissions
from project.infrastructure.registries import Registries

# TODO Fetch account from env variable
# TODO Fix resource id's for updates
# TODO Better localize configurable parameters

app = cdk.App()
env = cdk.Environment(account="046201199215", region="eu-west-1")

Permissions(app, "Permissions", env=env)
Registries(app, "ImageRegistries", env=env)
Authentication(app, "AuthenticationServer", env=env)

ProductionBackend(app, "ProductionBackend", env=env)
ProductionFrontend(app, "ProductionFrontend", env=env)
AcceptanceBackend(app, "AcceptanceBackend", env=env)
AcceptanceFrontend(app, "AcceptanceFrontend", env=env)

app.synth()
