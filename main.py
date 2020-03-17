import json
import os
from slack import WebClient
from ext.tools import bot_logger, authenticate_request, is_bot_message
from ext.parserequest import ParseRequest

_LOGGER = bot_logger()


def lambda_handler(event: dict, context: dict) -> dict:
    
    SECRET = os.getenv('SECRET')
    SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
    request = json.loads(event['body'])

    if 'type' in request and request['type'] == 'url_verification':
        return {"statusCode": 200, "body":json.dumps({"challenge":request['challenge']})}

    authenticate_request(event, SECRET)

    sc = WebClient(SLACK_BOT_TOKEN)
    _LOGGER.info(event)

    if not is_bot_message(request['event']):
        parser = ParseRequest(request['event']['text'])
        #handle the hello request
        if  parser.is_hello_request():
            sc.api_call(
                'chat.postMessage',
                channel=request['event']['channel'],
                text=f"Hello <@{request['event']['user']}> :hugging_face:")
            return {'statusCode':200,"body":""}
        #handle the action request
        elif parser.is_action_request():
            attachment = get_actions()
            sc.api_call(
                'chat.postMessage',
                channel=request['event']['channel'],
                text="What would you like to do?",
                attachments=attachment)
            return {'statusCode':200,"body":""}
        #handle the help request
        elif parser.is_help_request():
            text = f"""Hi <@{request['event']['user']}>! :male-teacher: If you digit `action` you can decide what to do!"""
            sc.api_call(
                'chat.postMessage',
                channel=request['event']['channel'],
                text=text
            )
            return {"statusCode":200, "body":""}
        else:
            sc.api_call(
                'chat.postMessage', 
                channel=request['event']['channel'],
                text=f"Sorry, <@{request['event']['user']}> I can't undertand :cry:"
            )
            return {'statusCode':200,"body":""}

def get_actions() -> dict:
    """
    Create the Slack interactive dialog
    """
    return [
        {
            "fallback":"Upgrade your Slack client to use messages like these.",
            "color":"#3AA3E3",
            "attachment_type":"default",
            "callback_id":"action_selection",
            "actions":[{
                "name":"action_selection",
                "text":"Choose an action!",
                "type":"select",
                "options":[
                    {
                        "text":"Save OK file",
                        "value":"ok_action"
                    },
                    {
                        "text":"Send KO file",
                        "value":"ko_action"
                    }
                ]
            },
            {
                "name":"cancel",
                "text":"Cancel",
                "type":"button",
                "value":"cancel"
            }]
        }
    ]