import json
import boto3
import datetime
import random
from decimal import Decimal

#Hello from local environment
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')

def authenticate_merchant(merchant_name, merchant_token):
    
    merchant_table = dynamodb.Table('Merchant')
    response = merchant_table.scan()

    items = response['Items']
    db_token = None
    for item in items:
        if item.get('MerchantName') == merchant_name:
            db_token = item.get('Token')
            break

    if merchant_token == db_token:
        return True
    else:
        return False 

def bad_merchant_res(merchant_name, merchant_token):
    return "Declined - Invalid Merchant Credentials."

error_res = "Declined - Invalid Bank or Card Information."

declined_res = "Declined - Insufficient Funds."

def write_transaction(m_name, m_token, cc_num, bank, amount, timestamp, status):
    transaction_table = dynamodb.Table('Transactions')
    cc_stored = "**** **** **** " + cc_num[-4:]
    item={}
    item['MerchantId'] = m_token
    item['DateTime'] = timestamp
    item['MerchantName'] = m_name
    item['AccountNumber'] = cc_stored
    item['TransactionAmount'] = amount
    item['TransactionStatus'] = status
    item['BankName'] = bank
    transaction_table.put_item(Item=item)
    
    
    
def lambda_handler(event, context):
    
    if 'body' in event and event['body'] is not None:
        body = json.loads(event['body'])
        merchant_name = body.get('merchant_name')
        merchant_token = body.get('merchant_token')
        bank = body.get('bank')
        cc_num = body.get('cc_num')
        card_type = body.get('card_type')
        security_code = body.get('security_code')
        amount = body.get('amount')
        card_zip = body.get('card_zip')
        timestamp = body.get('timestamp')

        #if amount is float turn it to decimal
        amount = Decimal(amount)



        if not authenticate_merchant(merchant_name, merchant_token):
            return bad_merchant_res(merchant_name, merchant_token)

        bank_table = dynamodb.Table('Bank')
        response = bank_table.get_item(
            Key={
                'BankName': bank,
                'AccountNum': cc_num
            }
        )

        item = response.get('Item')
        #Bank account or Bank Name not found
        if item is None:
            last_four = "**** **** **** " + cc_num[-4:]
            error_res['body']['bank'] = bank
            error_res['body']['cc_num'] = last_four
            error_res['body']['merchant_name'] = merchant_name
            error_res['body']['merchant_token'] = merchant_token
            error_res['body']['timestamp'] = timestamp
            
            write_transaction(merchant_name, merchant_token, cc_num, bank, amount, timestamp, "Declined - Invalid Bank or Card Information.")
            return error_res
            
        # If Debit Card
        if card_type == "Debit":
            balance = item.get("Balance")

            if float(balance) - float(amount) < 0:
                last_four = "**** **** **** " + cc_num[-4:]
                declined_res['body']['bank'] = bank
                declined_res['body']['cc_num'] = last_four
                declined_res['body']['amount'] = amount
                declined_res['body']['merchant_name'] = merchant_name
                declined_res['body']['merchant_token'] = merchant_token
                declined_res['body']['timestamp'] = timestamp
                
                write_transaction(merchant_name, merchant_token, cc_num, bank, amount, timestamp, "Declined - Insufficient Funds")
                return declined_res
            else:
                approved = "approved"
                #write to the bank table
                item['Balance'] = Decimal(balance) - Decimal(amount)
                bank_table.put_item(Item=item)

        # card type is credit
        else:
            credit_limit = item.get("CreditLimit")
            credit_used = item.get("CreditUsed")

            if float(credit_used) + float(amount) > float(credit_limit):
                last_four = "**** **** **** " + cc_num[-4:]
                declined_res['body']['bank'] = bank
                declined_res['body']['cc_num'] = last_four
                declined_res['body']['amount'] = amount
                declined_res['body']['merchant_name'] = merchant_name
                declined_res['body']['merchant_token'] = merchant_token
                declined_res['body']['timestamp'] = timestamp
                
                write_transaction(merchant_name, merchant_token, cc_num, bank, amount, timestamp, "Declined - Insufficient Funds")
                return declined_res
            else:
                approved = "approved"
                # write to the bank table
                item['CreditUsed'] = Decimal(credit_used) + Decimal(amount)
                bank_table.put_item(Item=item)

    # error no body found
    else:
        return {
            "statusCode": 404,
            "headers": { "Content-Type": "*/*" },
            "body": {
                "error": "There was an error, no body found"
            }
        }
        
    # Everything went well
    last_four = "**** **** **** " + cc_num[-4:]
    randomnumber = random.randint(1,10)
    if randomnumber == 1:
        write_transaction(merchant_name, merchant_token, cc_num, bank, amount, timestamp, "bank not available")
        return "Error - Bank Not Available."

    res = "Approved."
    write_transaction(merchant_name, merchant_token, cc_num, bank, amount, timestamp, "Approved.")
    return res
