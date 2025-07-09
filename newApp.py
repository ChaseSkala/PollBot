import os
import pprint
import shlex
from datastructures import *
from functions import *
from dotenv import load_dotenv
from slack_bolt import App, Ack, Respond
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient

manager = PollManager()

load_dotenv("tokens.env")

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN").strip()
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN").strip()

if not SLACK_BOT_TOKEN:
    raise ValueError("SLACK_BOT_TOKEN not found in environment")
if not SLACK_APP_TOKEN:
    raise ValueError("SLACK_APP_TOKEN not found in environment")

app = App(token=SLACK_BOT_TOKEN)

@app.command("/poll")
def create_pull(ack: Ack, command: dict):
    ack()
    pprint.pprint(command)
    client = WebClient(token=SLACK_BOT_TOKEN)
    user_name = command['user_name']
    channel_id = command['channel_id']
    poll_text = command['text'].strip()
    parts = shlex.split(poll_text)
    question, options, anonEnabled, user_name = isAnonymous(parts, user_name)

    response = client.chat_postMessage(
        channel=channel_id,
        text="Creating poll..."
    )
    pollID = response['ts']
    poll = manager.create_poll(
        poll_id = pollID,
        question = question,
        options = options,
        creator=user_name,
        channel_id = channel_id,
        anonymous = anonEnabled
    )

    client.chat_update(
        channel=channel_id,
        ts=pollID,
        text=poll.formatted_results
    )

    emoji_options_2 = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
    for i in range(len(options)):
        client.reactions_add(channel=channel_id, name=emoji_options_2[i], timestamp=pollID)
@app.command("/results")
def get_results(ack: Ack, command: dict):
    ack()
    pprint.pprint(command)
    ts = command.get("text").strip()
    channel_id = command["channel_id"]
    client = WebClient(token=SLACK_BOT_TOKEN)

    poll = manager.get_poll(ts)
    print(poll_text)
    client.chat_postMessage(channel=channel_id, text=poll_text)

@app.event("reaction_added")
def handle_reaction_added(event, client, logger):
    ts = event['item']['ts']
    channel = event["item"]["channel"]
    user_id = event["user"]
    reaction = event["reaction"]
    poll = manager.get_poll(ts)

    if not poll:
        raise Exception("Poll not found")

    emoji_to_index = {
        "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
        "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9
    }

    option_index = emoji_to_index[reaction]
    poll.add_vote(option_index, user_id)

    client.chat_update(
        channel=channel,
        ts=ts,
        text=poll.formatted_results
    )

@app.event("reaction_removed")
def handle_reaction_removed(event, client, logger):
    ts = event['item']['ts']
    channel = event["item"]["channel"]
    user_id = event["user"]
    reaction = event["reaction"]
    poll = manager.get_poll(ts)

    if not poll:
        raise Exception("Poll not found")

    emoji_to_index = {
        "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
        "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9
    }

    option_index = emoji_to_index[reaction]

    poll.remove_vote(option_index, user_id)

    client.chat_update(
        channel=channel,
        ts=ts,
        text=poll.formatted_results
    )
if __name__ == "__main__":
    SocketModeHandler(app, SLACK_APP_TOKEN).start()