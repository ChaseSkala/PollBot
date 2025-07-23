import os
import logging
import re
import pprint
from models import *
from services import *
from rendering import *
from actions.modals import *
from dotenv import load_dotenv
from slack_bolt import App, Ack
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient

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
def handle_poll_command(ack: Ack, command: dict):
    global client
    ack()
    modal = create_home_menu()
    modal["private_metadata"] = command["channel_id"]
    client.views_open(
        trigger_id=command["trigger_id"],
        view=modal,
    )

@app.command("/history")
def get_history(ack: Ack, command: dict):
    global client
    global manager
    ack()
    modal = show_poll_history(manager)
    channel = command["channel_id"]
    modal["private_metadata"] = channel
    client.views_open(
        trigger_id=command["trigger_id"],
        view=modal,
    )
@app.action("open-ended")
def handle_open_ended(ack: Ack, body:dict):
    global client
    ack()
    modal = create_open_ended()
    modal["private_metadata"] = body["view"]["private_metadata"]
    client.views_update(
        view_id=body["view"]["id"],
        view=modal,
    )

@app.action("multiple-choice")
def handle_multiple_choice(ack: Ack, body: dict):
    global client
    ack()
    modal = create_multiple_choice()
    modal["private_metadata"] = body["view"]["private_metadata"]
    client.views_update(
        view_id=body["view"]["id"],
        view=modal,
    )

@app.action("add-option")
def handle_choice_added(ack: Ack, body: dict):
    global client
    pprint.pprint(body)
    ack()
    channel = body['channel']['id']
    ts = body['message']['ts']
    modal = create_add_choices()
    modal["private_metadata"] = f"{channel}|{ts}"
    client.views_open(
        trigger_id=body["trigger_id"],
        view=modal,
    )

@app.view("adding-option")
def handle_add_option_added(ack: Ack, body: dict, view: dict):
    global client
    ack()

    channel, ts = body['view']['private_metadata'].split('|')
    poll_id = create_id(ts)
    poll = manager.get_poll(poll_id)
    user_input = body['view']['state']['values']['add_choice_block']['choice-added']['value']
    user_id = body['user']['id']
    user_info = client.users_info(user=user_id)
    user_name = user_info["user"]["name"]
    if can_add_more_options(poll, user_id):
        poll.options.append(PollOption(text=user_input, votes=1, voters={user_id: user_name}))
        response_num = len(poll.options)
        poll.options[-1].add_user(user_id, response_num)
        if poll.options[0].text == 'Add your responses!':
            blocks = render_open_ended_options(poll)
        else:
            blocks = render_multiple_choice_options(poll)
        client.chat_update(
            channel=channel,
            ts=ts,
            text="Poll update",
            blocks=blocks
        )
        poll.user_option_count[user_id] += 1
    else:
        client.chat_postEphemeral(
            channel=channel,
            user=user_id,
            text=f"You cannot add any more options!",
        )

@app.view("open-ended")
def create_open_ended_poll(ack: Ack, body, view, client, logger):
    ack()
    values = view["state"]["values"]
    question = None

    for block_id, block_data in values.items():
        if "question_input" in block_data:
            question = block_data["question_input"]["value"]
    if not question:
        logger.error("Missing question or choices!")
        return
    logger.info(f"Question: {question}")
    for block_id, block_data in values.items():
        if "max-options" in block_data:
            max_responses_count = block_data["max-options"]["value"]
        else:
            print("No response num to edit")
    anon_enabled = False
    can_add_choices = False
    for block_id, block_data in values.items():
        if "checkboxes-action" in block_data:
            selected = block_data["checkboxes-action"].get("selected_options", [])
            if selected and selected[0]["value"] == "anonymous":
                anon_enabled = True
    channel_id = view.get("private_metadata")
    user_id = body["user"]["id"]
    user_info = client.users_info(user=user_id)
    user_name = user_info["user"]["name"]



    response = client.chat_postMessage(
        channel=channel_id,
        text="Creating poll..."
    )

    pollID = create_id(response['ts'])
    creation_date = convert_unix_to_date(float(response['ts']))
    poll = manager.create_poll(
        poll_id=pollID,
        question=question,
        options=['Add your responses!'],
        creator=user_name,
        channel_id=channel_id,
        creation_date=creation_date,
        max_option_count=max_responses_count,
        anonymous=anon_enabled,
        can_add_choices=True,
    )
    client.chat_update(
        channel=channel_id,
        ts=response['ts'],
        text="Created OE Poll",
        blocks=render_open_ended(poll)
    )


@app.view("multiple-choice")
def create_multiple_choice_poll(ack: Ack, body, view, client, logger):
    ack()
    values = view["state"]["values"]
    question = None
    choices = None
    max_responses_count = 999
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
    pprint.pprint(choices)
    pprint.pprint(options)
    logger.info(f"Question: {question}")
    logger.info(f"Options: {options}")

    channel_id = view.get("private_metadata")
    user_id = body["user"]["id"]
    user_info = client.users_info(user=user_id)
    user_name = user_info["user"]["name"]

    anon_enabled = False
    can_add_choices = False
    for block_id, block_data in values.items():
        if "checkboxes-action" in block_data:
            selected = block_data["checkboxes-action"].get("selected_options", [])
            if selected and selected[0]["value"] == "anonymous":
                anon_enabled = True
            if selected and selected[0]["value"] == "can-users-add-new-choices":
                can_add_choices = True

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
        max_option_count=max_responses_count,
        anonymous = anon_enabled,
        can_add_choices = can_add_choices,
    )
    client.chat_update(
        channel=channel_id,
        ts=response['ts'],
        text="Created MC Poll",
        blocks=render_multiple_choice(poll)
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

    if poll.options[0].text == 'Add your responses!':
        blocks = render_open_ended_options(poll)
    else:
        blocks = render_multiple_choice_options(poll)
    client.chat_update(
        channel=channel,
        ts=ts,
        text="Poll update",
        blocks=blocks
    )

@app.action("back_to_history")
def handle_back_to_history(ack, body, client, logger):
    ack()
    modal = show_poll_history(manager)
    try:
        client.views_update(
            view_id=body['view']['id'],
            view=modal
        )
    except Exception as e:
        logger.error(f"Error updating modal: {e}")

@app.action(re.compile(r"poll_button-\d+"))
def handle_poll_button(ack: Ack, body, view, action, logger):
    ack()
    global client

    pprint.pprint(action)
    pprint.pprint(body)
    channel = body['view']["private_metadata"]
    poll_id = str(action["value"])
    poll = manager.get_poll(poll_id)

    if poll.options[0].text == 'Add your responses!':
        modal = all_open_ended(poll, channel)
        modal["private_metadata"] = channel
        client.views_update(
            view_id=body['view']['id'],
            view=modal,
        )
        logger.info("view-all-open-ended")
    else:
        modal = all_results(poll, channel)
        modal["private_metadata"] = channel
        client.views_update(
            view_id=body['view']['id'],
            view=modal,
        )
        logger.info("results")


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
    if poll.options[0].text == 'Add your responses!':
        blocks = render_open_ended_options(poll)
    else:
        blocks = render_multiple_choice_options(poll)
    client.chat_update(
        channel=channel,
        ts=ts,
        text="Poll update",
        blocks=blocks
    )

@app.action("results")
def handle_results(ack: Ack, body, action, logger):
    global client
    ack()
    ts = body['message']['ts']
    channel = body['channel']['id']
    poll_id = create_id(ts)
    poll = manager.get_poll(poll_id)
    modal = all_results(poll, channel)
    modal["private_metadata"] = channel
    client.views_open(
        trigger_id=body["trigger_id"],
        view=modal,
    )
    logger.info("results")

@app.action("view-all-open-ended")
def handle_view_all_open_ended(ack: Ack, body, action, logger):
    global client
    ack()
    ts = body['message']['ts']
    channel = body['channel']['id']
    poll_id = create_id(ts)
    poll = manager.get_poll(poll_id)
    modal = all_open_ended(poll, channel)
    modal["private_metadata"] = channel
    client.views_open(
        trigger_id=body["trigger_id"],
        view=modal,
    )
    logger.info("view-all-open-ended")

@app.action("edit-response")
def handle_edit_response(ack: Ack, body, action, logger):
    global client
    ack()
    ts = body['message']['ts']
    channel = body['channel']['id']
    modal = which_response_to_edit(ts, channel)
    client.views_open(
        trigger_id=body["trigger_id"],
        view=modal,
    )
    logger.info("view-all-open-ended")

@app.view("editing-response")
def handle_editing_response(ack: Ack, body, view, action, logger):
    global client
    ack()
    private_metadata = view.get("private_metadata", "")
    metadata = json.loads(private_metadata) if private_metadata else {}
    ts = metadata.get("ts")
    channel = metadata.get("channel")
    values = view["state"]["values"]
    poll_id = create_id(ts)
    poll = manager.get_poll(poll_id)
    user_id = body["user"]["id"]
    for block_id, block_data in values.items():
        if "which-response-to-edit" in block_data:
            response_num = block_data["which-response-to-edit"]["value"]
        else:
            print("No response num to edit")

    response_num = int(response_num)
    for i, response in enumerate(poll.options):
        if i == int(response_num):
            if response.check_user(user_id, response_num):
                allowed = True
                modal = editing_response(allowed, ts, channel, response_num)
                client.views_open(
                    trigger_id=body["trigger_id"],
                    view=modal,
                )
                logger.info("view-all-open-ended")
            else:
                allowed = False
                modal = editing_response(allowed, ts, channel, response_num)
                client.views_open(
                    trigger_id=body["trigger_id"],
                    view=modal,
                )
                logger.info("view-all-open-ended")
        else:
            continue

@app.view("submit-edit-response")
def handle_response_change(ack: Ack, body, view, action, logger):
    global client
    ack()
    private_metadata = view.get("private_metadata", "")
    metadata = json.loads(private_metadata) if private_metadata else {}
    ts = metadata.get("ts")
    channel = metadata.get("channel")
    response_num = metadata.get("response_num")
    values = view["state"]["values"]
    poll_id = create_id(ts)
    poll = manager.get_poll(poll_id)

    for block_id, block_data in values.items():
        if "new-response" in block_data:
            new_response = block_data["new-response"]["value"]
        else:
            print("No response num to edit")



    change_response(response_num, new_response, poll)

    blocks = render_open_ended_options(poll)
    client.chat_update(
        channel=channel,
        ts=ts,
        text="Poll update",
        blocks=blocks
    )

if __name__ == "__main__":
    SocketModeHandler(app, SLACK_APP_TOKEN).start()