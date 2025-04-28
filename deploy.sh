#! /bin/bash

sam build
source myenv/bin/activate
cd ./existing_lambda/
zip -r function.zip lambda_function.py
aws lambda update-function-code --function-name newProcessCreditCard --zip-file fileb://function.zip
