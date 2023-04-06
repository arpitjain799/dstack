## Install the CLI

Use `pip` to install `dstack`:

<div class="termy">

```shell
$ pip install dstack --upgrade
```

</div>

!!! info "NOTE:"
    By default, workflows run locally. To run workflows locally, it is required to have either Docker or [NVIDIA Docker](https://github.com/NVIDIA/nvidia-docker) 
    pre-installed.

### Configure a remote

To run workflows remotely (e.g. in a configured cloud account),
configure a remote using the `dstack config` command.

<div class="termy">

```shell
$ dstack config
? Choose backend. Use arrows to move, type to filter
> [aws]
  [gcp]
```

</div>

[//]: # (If you intend to collaborate in a team and would like to manage cloud credentials, users and other settings )
[//]: # (via a user interface, it is recommended to choose `hub`.)

[//]: # (!!! info "NOTE:")
[//]: # (    Choosing the `hub` remote with the `dstack config` CLI command requires you to have a Hub application up)
[//]: # (    and running. Refer to [Hub]&#40;#hub&#41; for the details.)

[//]: # (If you intend to work alone and wish to run workflows directly in the cloud without any intermediate, )
[//]: # (feel free to choose `aws` or `gcp`.)

If you intend to run remote workflows directly in the cloud using local cloud credentials, 
feel free to choose `aws` or `gcp`. Refer to [AWS](#aws) and [GCP](#gcp) correspondingly for the details.

[//]: # (If you would like to manage cloud credentials, users and other settings centrally)
[//]: # (via a user interface, it is recommended to choose `hub`. )

[//]: # (## Hub)

[//]: # ()
[//]: # (Hub allows you to manage cloud credentials, users and other settings via a user interface.)

[//]: # ()
[//]: # (This way is preferred if you intend to collaborate as a team, and don't want every user to have )

[//]: # (cloud credentials configured locally.)

[//]: # ()
[//]: # (In this case, the `dstack config` command is given with the URL of the Hub application and)

[//]: # (the personal access token.)

[//]: # ()
[//]: # (### 1. Start the Hub application)

[//]: # ()
[//]: # (Before you can use Hub, you first have to start the Hub application.)

[//]: # (You can run it either locally, on a dedicated server, or in the cloud.)

[//]: # ()
[//]: # (!!! info "NOTE:")

[//]: # (    You can skip this step if the Hub application is already set up, and you're given with its URL)

[//]: # (    and a personal access token.)

[//]: # ()
[//]: # (Run the Hub application:)

[//]: # ()
[//]: # (```shell)

[//]: # (dstack hub start)

[//]: # (```)

[//]: # ()
[//]: # (If needed, the command allows you to override the port, host, and the admin token:)

[//]: # ()
[//]: # (![dstack config]&#40;assets/dstack-hub-help.png&#41;)

[//]: # ()
[//]: # (Once the application is started, click the URL in the output to login as an admin.)

[//]: # ()
[//]: # (!!! warning "TODO:")

[//]: # (    Add a screenshot of the `dstack hub start` command output with the login URL)

[//]: # ()
[//]: # (### 2. Create a hub)

[//]: # ()
[//]: # (After you've logged in as an admin, you can create a specific hub, and the user)

[//]: # (that will access the hub.)

[//]: # ()
[//]: # (!!! warning "TODO:")

[//]: # (    Add a screenshot of the Hub Backend Edit page)

[//]: # ()
[//]: # (When creating a hub, you have to specify the corresponding cloud settings, incl.)

[//]: # (the credentials to the cloud, the region, the bucket, etc.)

[//]: # ()
[//]: # (!!! info "NOTE:")

[//]: # (    You can configure multiple hubs, and for each specify different cloud settings and )

[//]: # (    assign a different team.)

[//]: # ()
[//]: # (### 3. Configure the CLI)

[//]: # ()
[//]: # (Once the hub is created, copy the corresponding code snippet to configure)

[//]: # (this hub as a remote via the `dstack config` command.)

[//]: # ()
[//]: # (!!! warning "TODO:")

[//]: # (    Add a screenshot of the Hub View Page showing the CLI code snippet)

[//]: # ()
[//]: # (The command includes the URL of the created hub accompanied with the personal access token of the user: )

[//]: # ()
[//]: # (```shell)

[//]: # (dstack config hub --url http://localhost:3000/my-new-hub --token 8a019f6d-e01f-41e3-9e54-e3369f3deda0 )

[//]: # (```)

[//]: # ()
[//]: # (That's it! You've configured Hub as a remote.)

[//]: # ()
[//]: # (!!! warning "TODO:")

[//]: # (    _Elaborate on how to create users and let them log in into the Hub application_)

## AWS

### 1. Create an S3 bucket

In order to use AWS as a remote, you first have to create an S3 bucket in your AWS account.
This bucket will be used to store workflow artifacts and metadata.

!!! info "NOTE:"
    Make sure to create an S3 bucket in the AWS region where you'd like to run your workflows.

### 2. Configure AWS credentials

The next step is to configure AWS credentials on your local machine. The credentials should grant
the permissions to perform actions on `s3`, `logs`, `secretsmanager`, `ec2`, and `iam` services.

??? info "IAM policy template"
    If you'd like to limit the permissions to the most narrow scope, feel free to use the IAM policy template
    below.

    Replace `{bucket_name}` and `{bucket_name_under_score}` variables in the template below
    with the values that correspond to your S3 bucket.

    For `{bucket_name}`, use the name of the S3 bucket. 
    For `{bucket_name_under_score}`, use the same but with dash characters replaced to underscores 
    (e.g. if `{bucket_name}` is `dstack-142421590066-eu-west-1`, then  `{bucket_name_under_score}` 
    must be `dstack_142421590066_eu_west_1`.

    ```json
    {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Effect": "Allow",
          "Action": [
              "s3:PutObject",
              "s3:GetObject",
              "s3:DeleteObject",
              "s3:ListBucket",
              "s3:GetLifecycleConfiguration",
              "s3:PutLifecycleConfiguration",
              "s3:PutObjectTagging",
              "s3:GetObjectTagging",
              "s3:DeleteObjectTagging",
              "s3:GetBucketAcl"
          ],
          "Resource": [
            "arn:aws:s3:::{bucket_name}",
            "arn:aws:s3:::{bucket_name}/*"
          ]
        },
        {
          "Effect": "Allow",
          "Action": [
            "logs:DescribeLogGroups"
          ],
          "Resource": [
            "arn:aws:logs:*:*:log-group:*"
          ]
        },
        {
          "Effect": "Allow",
          "Action": [
            "logs:FilterLogEvents",
            "logs:TagLogGroup",
            "logs:CreateLogGroup",
            "logs:CreateLogStream"
          ],
          "Resource": [
            "arn:aws:logs:*:*:log-group:/dstack/jobs/{bucket_name}*:*",
            "arn:aws:logs:*:*:log-group:/dstack/runners/{bucket_name}*:*"
          ]
        },
        {
          "Effect": "Allow",
          "Action": [
            "secretsmanager:UpdateSecret",
            "secretsmanager:GetSecretValue",
            "secretsmanager:CreateSecret",
            "secretsmanager:PutSecretValue",
            "secretsmanager:PutResourcePolicy",
            "secretsmanager:TagResource",
            "secretsmanager:DeleteSecret"
          ],
          "Resource": [
            "arn:aws:secretsmanager:*:*:secret:/dstack/{bucket_name}/credentials/*",
            "arn:aws:secretsmanager:*:*:secret:/dstack/{bucket_name}/secrets/*"
          ]
        },
        {
          "Effect": "Allow",
          "Action": [
            "ec2:DescribeInstanceTypes",
            "ec2:DescribeSecurityGroups",
            "ec2:DescribeSubnets",
            "ec2:DescribeImages",
            "ec2:DescribeInstances",
            "ec2:DescribeSpotInstanceRequests",
            "ec2:RunInstances",
            "ec2:CreateTags",
            "ec2:CreateSecurityGroup",
            "ec2:AuthorizeSecurityGroupIngress",
            "ec2:AuthorizeSecurityGroupEgress"
          ],
          "Resource": "*"
        },
        {
          "Effect": "Allow",
          "Action": [
            "ec2:CancelSpotInstanceRequests",
            "ec2:TerminateInstances"
          ],
          "Resource": "*",
          "Condition": {
            "StringEquals": {
              "aws:ResourceTag/dstack_bucket": "{bucket_name}"
            }
          }
        },
        {
          "Effect": "Allow",
          "Action": [
            "iam:GetRole",
            "iam:CreateRole",
            "iam:AttachRolePolicy",
            "iam:TagRole"
          ],
          "Resource": "arn:aws:iam::*:role/dstack_role_{bucket_name_under_score}*"
        },
        {
          "Effect": "Allow",
          "Action": [
            "iam:CreatePolicy",
            "iam:TagPolicy"
          ],
          "Resource": "arn:aws:iam::*:policy/dstack_policy_{bucket_name_under_score}*"
        },
        {
          "Effect": "Allow",
          "Action": [
            "iam:GetInstanceProfile",
            "iam:CreateInstanceProfile",
            "iam:AddRoleToInstanceProfile",
            "iam:TagInstanceProfile",
            "iam:PassRole"
          ],
          "Resource": [
            "arn:aws:iam::*:instance-profile/dstack_role_{bucket_name_under_score}*",
            "arn:aws:iam::*:role/dstack_role_{bucket_name_under_score}*"
          ]
        }
      ]
    }
    ```

### 3. Configure the CLI

Once the AWS credentials are configured on your local machine, you can configure the CLI using the `dstack config` command.

This command will ask you to choose an AWS profile, an AWS region (must be the same for the S3 bucket), 
and the name of the S3 bucket.

<div class="termy">

```shell
$ dstack config

? Choose backend: aws
? AWS profile: default
? Choose AWS region: eu-west-1
? Choose S3 bucket: dstack-142421590066-eu-west-1
? Choose EC2 subnet: no preference
```

</div>

That's it! You've configured AWS as a remote.

## GCP

### 1. Create a project

In order to use GCP as a remote, you first have to create a project in your GCP account
and make sure that the required APIs and enabled for it.

??? info "Required APIs"
    Here's the list of APIs that have to be enabled for the project.

    ```
    cloudapis.googleapis.com
    compute.googleapis.com 
    logging.googleapis.com
    secretmanager.googleapis.com
    storage-api.googleapis.com
    storage-component.googleapis.com 
    storage.googleapis.com 
    ```

### 2. Create a storage bucket

Once the project is set up, you can proceed and create a storage bucket. This bucket
will be used to store workflow artifacts and metadata.

!!! info "NOTE:"
    Make sure to create the bucket in the location where you'd like to run your workflows.

### 3. Create a service account

The next step is to create a service account in the created project and configure the
following roles for it: `Service Account User`, `Compute Admin`, `Storage Admin`, `Secret Manager Admin`,
and `Logging Admin`.

### 4. Create a service account key

Once the service account is set up, create a key for it and download the corresponding JSON file
to your local machine (e.g. to `~/Downloads/my-awesome-project-d7735ca1dd53.json`).

### 5. Configure the CLI

Once the service account key JSON file is on your machine, you can configure the CLI using the `dstack config` command.

The command will ask you for a path to a service account key file, GCP region and zone, and storage bucket name.

<div class="termy">

```shell
$ dstack config

? Choose backend: gcp
? Enter path to credentials file: ~/Downloads/dstack-d7735ca1dd53.json
? Choose GCP geographic area: North America
? Choose GCP region: us-west1
? Choose GCP zone: us-west1-b
? Choose storage bucket: dstack-dstack-us-west1
? Choose VPC subnet: no preference
```

</div>

That's it! You've configured GCP as a remote.