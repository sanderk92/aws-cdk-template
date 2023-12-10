
# Welcome to CDK

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the `.venv`
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

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

# Initial setup

When setting up a project using this CDK, you should perform the following actions in the specified order:

### 1. Permission group

- Create a new root account with access key
- Run `aws config` and configure the root access key
- Set env variable `CDK_ACCOUNT` to the account id (the number can be found in the account arn)
- Run `cdk deploy Permissions`
- Remove the access key for the root account

### 2. Deployment

- Create an IAM user with access key
- Assign the permission group to this user
- Create the required SSL certificates in the CertificatesManager for the backend (regional)
- Create the required SSL certificates in the CertificatesManager for the frontend (global)
- Create the required secrets in the SecretsManager
- Set the required constants in `app_config.py`
- Run `aws config` and configure the user access key
- Set env variable `CDK_ACCOUNT` to the account id (the number can be found in the account arn)
- Run `cdk deploy {stack}` for all remaining stacks in the `infrastructure` folder
- Run `cdk deploy {stack}` for the required stacks in the `application` folder

