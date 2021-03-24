# Betting Splits Insights Ingestion

Retrieve betting splits insights from Sports Radar. Ingestion is kicked off using Cloudwatch events every 15 minutes and dumped into s3 buckets. A dynamodb table tracks when files are updated.

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
aws cloudformation create-stack --stack-name dataeng-bettingsplits-sr-ingest --template-body file://build/pipeline-qa.yml --capabilities CAPABILITY_NAMED_IAM --parameters '[{"ParameterKey":"ProjectName","ParameterValue":"dataeng-bettingsplits-sr-ingest"}]'
```

## Deploy from local to dev
With your own personalized stackName (STAGE=usernameMMDD)
The default serverless deploy creates a stack named ${self:service}-${self:provider.stage}
```bash
# Create new stack in scoring-dev account named: dataeng-bettingsplits-sr-ingest-hkbaro0125
AWS_PROFILE=scoring-qa; STAGE=hkbaro0125; serverless deploy --stage $STAGE --verbose --aws-s3-accelerate
```
