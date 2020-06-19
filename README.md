# William Hill Futures ingest

Retrieve futures from apis. Ingestion is kicked off using Cloudwatch events hourly and dumped into s3 buckets. A dynamodb table tracks when files are updated.

## Folder Structure

| Folder        | Purpose       |
| ------------- |:-------------:|
|/build         | Build related configuration|
|/scripts | Shell scripts|
|/src/handler | Lambda handlers functions|
|/tests/unit | Unit test specs|

## Getting started
Requirements:
- Serverless Framework
- AWS CLI
- Okta.jar login with assumed role scoring-developer

## Pipelines
Pipelines are set up in  in dev, qa, and prod for automated deployments from github triggered by merge into master. They will be created by running:
```bash
aws cloudformation create-stack --stack-name dataeng-futures-wh-ingest --template-body file://build/pipeline-qa.yml --capabilities CAPABILITY_NAMED_IAM --parameters '[{"ParameterKey":"ProjectName","ParameterValue":"dataeng-futures-wh-ingest"}]'
```

## Deploy from local to dev
With your own personalized stackName (STAGE=usernameMMDD)
The default serverless deploy creates a stack named ${self:service}-${self:provider.stage}
```bash
# Create new stack in scoring-dev account named: dataeng-futures-wh-wh-gwyman1108
AWS_PROFILE=scoring-dev; STAGE=gwyman1108; serverless deploy --stage $STAGE --verbose --aws-s3-accelerate
```
