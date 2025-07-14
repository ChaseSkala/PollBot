import os
import logging
import re

from models import *
from services import *
from rendering import *
from actions.createPoll import *
from dotenv import load_dotenv
from slack_bolt import App, Ack
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient
from slack_sdk.models.blocks import SectionBlock, ActionsBlock
from slack_sdk.models.blocks.block_elements import ButtonElement

logger = logging.getLogger(__name__)

manager = PollManager()

load_dotenv("tokens.env")

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"].strip()
SLACK_APP_TOKEN = os.environ["SLACK_APP_TOKEN"].strip()

if not SLACK_BOT_TOKEN:
    raise ValueError("SLACK_BOT_TOKEN not found in environment")
if not SLACK_APP_TOKEN:
    raise ValueError("SLACK_APP_TOKEN not found in environment")

app = App(token=SLACK_BOT_TOKEN)
client = WebClient(token=SLACK_BOT_TOKEN)

@app.command("/poll")
def send_ui(ack: Ack, command: dict):
    global client
    ack()
    modal = create_poll()
    modal["private_metadata"] = command["channel_id"]
    client.views_open(
        trigger_id=command["trigger_id"],
        view=modal,
    )
    logger.info("poll")

@app.view("poll")
def create_pull(ack: Ack, body, view, client, logger):
    ack()
    values = view["state"]["values"]
    question = None
    choices = None

    for block_id, block_data in values.items():
        if "question_input" in block_data:
            question = block_data["question_input"]["value"]
        elif "choices_input" in block_data:
            choices = block_data["choices_input"]["value"]
    if question and choices:
        options = [choice.strip() for choice in choices.splitlines()]
    if not question or not choices:
        logger.error("Missing question or choices!")
        return

    logger.info(f"Question: {question}")
    logger.info(f"Options: {options}")

    channel_id = view.get("private_metadata")
    user_id = body["user"]["id"]
    user_info = client.users_info(user=user_id)
    user_name = user_info["user"]["name"]

    anon_enabled = False
    for block_id, block_data in values.items():
        if "checkboxes-action" in block_data:
            selected = block_data["checkboxes-action"].get("selected_options", [])
            if selected and selected[0]["value"] == "anonymous":
                anon_enabled = True

    response = client.chat_postMessage(
        channel=channel_id,
        text="Creating poll..."
    )

    pollID = create_id(response['ts'])
    creation_date = convert_unix_to_date(float(response['ts']))
    poll = manager.create_poll(
        poll_id = pollID,
        question = question,
        options = options,
        creator=user_name,
        channel_id = channel_id,
        creation_date=creation_date,
        anonymous = anon_enabled,
    )
    client.chat_update(
        channel=channel_id,
        ts=response['ts'],
        blocks=render_results(poll)
    )

@app.command("/results")
def get_results(ack: Ack, command: dict):
    global client
    ack()
    ts = command.get("text").strip()
    poll = manager.get_poll(ts)
    channel_id = command["channel_id"]
    client.chat_postMessage(channel=channel_id, blocks=render_results(poll))

@app.command("/history")
def get_history(ack: Ack, command: dict):
    global client
    ack()
    ts = command.get("text").strip()
    channel_id = command["channel_id"]
    poll_text = render_history(manager.history)
    client.chat_postMessage(
        channel=channel_id,
        text=poll_text,
    )

@app.action(re.compile(r"actionId-\d+"))
def handle_vote(ack: Ack, body, action, logger):
    ack()
    global client
    action_id = action["action_id"]
    index = int(action_id.split('-')[1])
    ts = body['message']['ts']
    channel = body['channel']['id']
    poll_id = create_id(ts)
    poll = manager.get_poll(poll_id)

    user_id = body["user"]["id"]
    user_info = client.users_info(user=user_id)
    username = user_info["user"]["profile"]["display_name"]

    option = poll.options[index]

    if user_id in option.voters:
        poll.remove_vote(index, user_id, username)
    else:
        poll.add_vote(index, user_id, username)

    client.chat_update(
        channel=channel,
        ts=ts,
        text="Poll update",
        blocks=render_options(poll, user_id)
    )

@app.action("poll_option_select")
def handle_dropdown_vote(ack: Ack, body, action, logger):
    ack()
    global client
    index = int(action["selected_option"]["value"])
    ts = body['message']['ts']
    channel = body['channel']['id']
    poll_id = create_id(ts)
    poll = manager.get_poll(poll_id)

    user_id = body["user"]["id"]
    user_info = client.users_info(user=user_id)
    username = user_info["user"]["profile"]["display_name"]

    option = poll.options[index]

    if user_id in option.voters:
        poll.remove_vote(index, user_id, username)
    else:
        poll.add_vote(index, user_id, username)

    client.chat_update(
        channel=channel,
        ts=ts,
        text="Poll update",
        blocks=render_options(poll, user_id)
    )



if __name__ == "__main__":
    SocketModeHandler(app, SLACK_APP_TOKEN).start()