
# Welcome to CDK

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the `.venv`
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

## Attention

This CDK is currently ment to be run once to set up the initial environment, after which updates are done manually.
Prior to running this CDK, the required ECR's and SSL certificate + Hosted Zone have been created manually. These 
components are referenced in this CDK.

## Required roles

The user to execute this CDK script has to have the roles below assigned to it. However, they may need to be pruned 
and/or combined in a single json policy:

1. AdministratorAccess	AWS managed - job function	Directly
2. AmazonEC2ContainerRegistryFullAccess	AWS managed	Directly
3. AmazonEC2FullAccess	AWS managed	Directly
4. AmazonECS_FullAccess	AWS managed	Directly
5. AmazonElasticContainerRegistryPublicFullAccess	AWS managed	Directly
6. AmazonS3FullAccess	AWS managed	Directly
7. AmazonSSMFullAccess	AWS managed	Directly
8. AWSCloudFormationFullAccess	AWS managed	Directly
9. IAMFullAccess
10. custom-policy

`custom-policy.json`:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:Describe*",
                "iam:ListRoles",
                "sts:AssumeRole",
                "tag:GetResources",
                "cloudformation:*"
            ],
            "Resource": "*"
        }
    ]
}
```

## Setup instructions Linux/MacOS

To manually create a virtualenv:

```
$ python -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

## Setup instructions Windows

To manually create a virtualenv:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

## Run instructions

At this point you can now run the CDK commands.

* `cdk ls`          list all stacks in the app
* `cdk synth`       emits the synthesized CloudFormation template
* `cdk deploy`      deploy this stack to your default AWS account/region
* `cdk diff`        compare deployed stack with current state
* `cdk docs`        open CDK documentation

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.


