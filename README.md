### Tools Used
I used the following tools:
* [Pipenv](https://pipenv-fork.readthedocs.io/en/latest/) - lets me separate dev and build dependencies for compacting lambda deploys.
* [serverless](https://serverless.com) - a framework built on node for generating and deploying cloudformation templates.

### Pre-requisites 
* Install pipenv:  `brew install pipenv`
* Install [docker](https://www.docker.com/products/docker-desktop)
* Install node and npm: `brew install node`
* Install serverless: `npm install`

## Service Resources
This service creates the following resources:
* A bucket named `relationship-file-lz`. If the bucket already exists we can add a plugin for existing buckets and setup an iam role.
* A DynamoDB table named `object_relationships` that uses the `name` field for it's key.
* A lambda named `file-to-dynamo` that triggers when a file is created in `relationship-file-lz`.


### Commands 
* Validate Linting: `npm run pylint`
* Validate serverless config: `pipenv run $(npm bin)/serverless deploy --stage dev --noDeploy`
* Deploy stack: `pipenv run $(npm bin)/serverless deploy --stage dev`
