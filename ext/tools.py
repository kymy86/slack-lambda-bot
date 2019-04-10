import logging
import time
import hashlib
import hmac
import boto3

def bot_logger():
    """
    Instantiate the logger component
    """
    logger = logging.getLogger('bot')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
    ch.setFormatter(formatter)
    return logger

def is_bot_message(event: dict) -> bool:
    """
    Determine if the message is generated by
    the SlackBot or not.
    """
    if 'bot_id' in event:
        return True
    elif 'message' in event and 'bot_id' in event['message']:
        return True
    else:
        return False

def http_ok_status() -> dict:
    """
    Return an HTTP 200 ok status
    """
    return {"statusCode":200, "body":""}

def authenticate_request(event: dict, secret: str) -> dict:
    """
    Check if request came from Slack and if it's authorized to
    perform the API call
    """
    if 'X-Slack-Request-Timestamp' not in event['headers']:
        return {"statusCode":403, "body":"Request unauthorized"}

    timestamp = event['headers']['X-Slack-Request-Timestamp']
    slack_signature = event['headers']['X-Slack-Signature']
    slack_secret = bytes(secret, 'utf-8')
    components = ['v0', timestamp, event['body']]
    
    #Reply attack prevention
    if abs(int(time.time()) - int(timestamp)) > 60 * 5: 
        return {"statusCode": 502, "body":"request timeout"}
    
    basestr = ':'.join(components)
    digest = hmac.new(slack_secret, msg=basestr.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()
    signature = "v0="+digest
    if not hmac.compare_digest(signature, slack_signature):
        return {"statusCode": 403, "body":"Request unauthorized"}