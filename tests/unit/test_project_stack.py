import aws_cdk as core
import aws_cdk.assertions as assertions

from project.project_name import ProjectStack

# example tests. To run these tests, uncomment this file along with the example
# resource in project/project_name.py
def test_sqs_queue_created():
    app = core.App()
    stack = ProjectStack(app, "project")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
