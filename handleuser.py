import json
import os
from urllib.parse import unquote
import boto3
from ext.tools import bot_logger, authenticate_request, http_ok_status
from slackclient import SlackClient

_LOGGER = bot_logger()

def lambda_handler(event: dict, context: dict) -> str:
    SECRET = os.getenv('SECRET')
    SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')

    authenticate_request(event, SECRET)

    payload_raw = unquote(event['body'])
    payload = json.loads(payload_raw.strip("payload="))

    _LOGGER.info(payload)

    sc = SlackClient(SLACK_BOT_TOKEN)

    if payload['callback_id'] == 'action_selection':
        # user cancels the action
        if payload['actions'][0]['type']=='button':
            cancel_action(sc, payload['channel']['id'], payload['message_ts'])
            return http_ok_status()
        elif payload['actions'][0]['selected_options'][0]['value'] == 'ok_action':
            ok_json = save_json_file("ok")
            sc.api_call('chat.update',
                channel=payload['channel']['id'],
                ts=payload['message_ts'],
                text="The OK file saved is:\n\n ```{}```".format(ok_json),
                attachments=[])
            return http_ok_status()
        elif payload['actions'][0]['selected_options'][0]['value'] == 'ko_action':
            ko_json = save_json_file("ko")
            sc.api_call('chat.update',
                channel=payload['channel']['id'],
                ts=payload['message_ts'],
                text="The KO file saved:\n\n ```{}```".format(ko_json),
                attachments=[])
            return http_ok_status()
        else:
            #Option not exists
            return http_ok_status()


def cancel_action(sc: object, channel_id: str, msg_timestamp: str):
    """
    Cancel the current action
    """
    sc.api_call('chat.update',
            channel=channel_id,
            ts=msg_timestamp,
            text=":face_with_raised_eyebrow: Operation cancelled... :face_with_symbols_on_mouth:",
            attachments=[])

def save_json_file(kind: str) -> str:
    """
    Save file in S3
    """
    json_structure = {
        "foo":"bar",
        "number":1,
        "kind":kind
    }

    json_string = json.dumps(json_structure)
    s3 = boto3.resource('s3')
    s3.Object(os.getenv('BUCKET_NAME'), "action.json",).put(Body=json_string)

    return json_string