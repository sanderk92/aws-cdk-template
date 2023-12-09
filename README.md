
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
- Create a new root account
- Run `cdk deploy Permissions` with this root account
- Create a IAM user
- Assign the IAM user to the created group
- Create the required SSL certificates (including all subdomains)
- Set the required constants in `backend_stack.py`, `frontend_stack.py` and `stack_base.py`
- Run `cdk deploy {stack}` for all remaining stacks in the `infrastructure` folder
- Run `cdk deploy {stack}` for the required stacks in the `application` folder

