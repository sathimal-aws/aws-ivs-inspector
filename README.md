# NOTE—Creating this infrastructure may incur costs. Please refer to the AWS pricing for more information.

## Installation

This installation guide leverages GitHub Actions to streamline the deployment process. Ensure you have the necessary permissions and configurations in place before proceeding.

#### Prerequisites

- **AWS Account & Permissions:** An AWS account with an IAM user possessing `AdministratorAccess` policy.
- **Important:** Limit or remove these permissions after deployment for security best practices.
- **S3 Bucket:** An S3 bucket to store Terraform state files. Note the bucket name and region.

Wiki: [Link to the Prerequisites](https://github.com/sathimal-aws/aws-ivs-inspector/wiki/01:-Prerequisites)

#### Deployment

:TODO: Add short description

Wiki: [Link to the Deployment](https://github.com/sathimal-aws/aws-ivs-inspector/wiki/02:-Backend-Infrastructure-Deployment)

## Accessing the Web Application

:TODO: Add short description

Wiki: [Link to the Web Application Access](https://github.com/sathimal-aws/aws-ivs-inspector/wiki/03:-Accessing-the-Web-Application)

<!-- 1. After all workflows complete successfully, go to the AWS console.
2. Navigate to the Amplify service in the region where you deployed your application.
3. Select your IVS Inspector application.
4. Under "Overview" > "Production branch," click the domain link to access your deployed IVS Inspector application.
5. You can now use the IVS Inspector web application using the default username `admin@ivs-inspector.com`, and the password `123Qwe,./`

![06-IvsInspectorAppLink.png](documentation/screenshots/06-IvsInspectorAppLink.png) -->

## Renaming the Project

If you wish to change the default project name (`ivs-inspector`):

1. Go to your repository's `Settings` > `Secrets and variables` > `Actions`.
2. Update the value of the `IVS_PROJECT_NAME` variable.

<!-- ## Pricing and Resource Usage

This document details the AWS resources used by IVS Inspector, their usage patterns, and associated costs, both during operation and at rest.

## Resource Usage

The following AWS services are used:

- **AWS Lambda:** [List Lambda functions and their purpose, e.g., API endpoints, stream processing].
- **Amazon API Gateway:** [Explain its role, e.g., exposing Lambda functions as HTTP APIs].
- **Amazon S3:** [Describe how S3 is used, e.g., storing Terraform state, website hosting].
- **AWS Amplify (If applicable):** [Explain how Amplify is used, e.g., web app hosting, CI/CD].
- **Amazon DynamoDB (If applicable):** [Describe how it is used, e.g. storing passenger and vehicle data.]
- **Amazon Cognito (if applicable):** [Describe how it is used, e.g., for Authentication.]

Example cost breakdown for a single lambda function:

- **`list-channels`:**
  - Memory: 128 MB
  - Estimated Invocations/month: 10,000
  - Estimated Avg. Duration: 200ms
  - Estimated Cost: $0.00417/month (calculated as shown above)

## Pricing

Costs are categorized by service and usage type.

**(Repeat this section for EACH service identified above)**

### [Service Name] (e.g., Amazon IVS)

**Operational Costs ("On Usage"):**

- [Specific usage metrics and pricing. E.g., IVS Channel Hours, Ingest hours, Playback hours].
- [Example: Channel Hours: $X per hour. Estimated usage: Y hours/month. Estimated monthly cost: $X * Y].

**Costs at Rest:**

- [Describe costs incurred even when the service isn't actively processing, e.g., storage fees for DynamoDB, data storage for S3].
- [Example: Storage costs for recordings are $Z per GB. Expected usage A GB. Expected monthly cost $Z * A.]

**Pricing Link:** [Link to the official AWS pricing page for this service].

## Cost Optimization Strategies (General)

- **Right-sizing:** Choose appropriate instance sizes for EC2, Lambda memory for Lambda functions, etc.
- **Scheduled Start/Stop:** Configure scheduled start/stop for EC2 instances or other resources used only during specific times.
- **Delete Unused Resources:** Remove unused resources when no longer required.
- **Free Tier:** Utilize the AWS Free Tier whenever possible.

## Detailed Pricing Information

[Add any further context on pricing estimates and how they were calculated]. -->
