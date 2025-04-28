# Instructions for CI/CD

## Testing locally

Change the JSON object in the event.json to change the test scenario, or create a new event.json

```bash
sam build
sam local invoke "ExistingLambdaFunction" -e events/event.json
```

## Deploying to AWS lambda

Enter python virtual environment

```bash
source myenv/bin/activate
```

Zip lambda function and deploy zip file to AWS lambda, run these commands in the same directory as the lambda function

```bash
zip -r function.zip lambda_function.py
aws lambda update-function-code --function-name newProcessCreditCard --zip-file fileb://function.zip
```
