# Instructions for using SAM and AWS-CLI to run lambda functions locally

I got this working on WSL on windows 10, so some things might be a little different if you're using a mac or even windows 11

## Downloading and setup

You need to have the following downloaded
* aws-cli
* SAM
    * Docker Desktop


### Docker

On mac you might be able to use the docker cli, but on my windows machine i had to download the gui software. I didn't need to sign in or setup anything really. I just downloaded it and made sure its running whenever I use any SAM commands. All of the SAM commands for running lambda stuff needs docker to work.

### Aws

You'll need to create a new user in IAM and give it access to your tables and the ability to update code

This is what the function update code policy looks like. 
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": "lambda:UpdateFunctionCode",
            "Resource": "arn:aws:lambda:us-east-2:211125766637:function:newProcessCreditCard"
        }
    ]
}
```

Run this after downloading aws-cli. You'll give it your new user access key id and secret key, default region, etc.
```bash
aws configure
```

## Project setup
(dir) = directory
project_directory is the directory where all your local lambda stuff goes, mine is called aws_project

### Directory 'Tree'

project_directory
* events (dir)
    * event.json
* existing_lambda (dir)
    * function.zip
    * lambda_function.py
* template.yaml

### events directory

You need an events directory to use as the testing event when you run your lambda with sam, event.json contains a json object with the same "String" that we used in the lambda console to test our lambda function.

my event.json
```json
{
      "body": "{\"bank\": \"Visa\",\n\"merchant_name\": \"Family Dollar\",\n\"cc_num\": \"4595895049543230\",\n\"merchant_token\": \"lwgNv5lM\",\n\"card_type\": \"Credit\",\n\"amount\": \"0\",\n\"timestamp\": \"2024-04-07 11:08:17.617190\" }"
}
```

### existing_lambda directory

existing_lambda is just a directory with the lambda function file and a zip file. The zip file gets created when you are ready to send your code changes to aws lambda in the cloud.

### template.yaml

The template you make for SAM to run your lambda

My template.yaml
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: 'AWS::Serverless-2016-10-31'
Description: Local environment for existing AWS Lambda function

Resources:
  ExistingLambdaFunction: # This is what you pass in to the SAM command to run your lambda
    Type: 'AWS::Serverless::Function'
    Properties:
      FunctionName: lambda_function # lambda function filename
      Handler: lambda_function.lambda_handler #[lambda filename].[lambda_function the function that has (event, context) as parameters]
      Runtime: python3.8  # or the runtime of your existing Lambda function
      CodeUri: ./existing_lambda/ #or the directory that contains your lambda function

```

### Small change to access dynamodb

Make sure to put the region_name parameter when accessing dynamodb to access all of your tables

```python
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
```

## After all the setup

NOTE! These are just my own instructions to remind myself of the process that I've included here. I use a python virtual environment as part of the process because something was going wrong with aws-cli or boto3 or something on my system so i made a virtual environment and it just worked.

### Testing locally

Change the JSON object in the event.json to change the test scenario, or create a new event.json

```bash
sam build
sam local invoke "ExistingLambdaFunction" -e events/event.json
```

### Deploying to AWS lambda

Enter python virtual environment

```bash
source myenv/bin/activate
```

Zip lambda function and deploy zip file to AWS lambda, run these commands in the same directory as the lambda function

```bash
zip -r function.zip lambda_function.py
aws lambda update-function-code --function-name newProcessCreditCard --zip-file fileb://function.zip
```
