#!/usr/bin/env python3

import aws_cdk as cdk

from project.project_name import ProjectName

app = cdk.App()

# ProjectName(app, "ProjectName")

ProjectName(
    app,
    construct_id="ProjectName",
    env=cdk.Environment(
        account="046201199215",
        region="eu-west-1"
    )
)

app.synth()
