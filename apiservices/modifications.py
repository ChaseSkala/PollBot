import json
import re

from actions.modals.modification import create_add_choices, which_response_to_edit, editing_response
from actions.rendering.options import render_open_ended_options, render_multiple_choice_options
from models import PollOption
from generalservices import create_id, can_add_more_options, change_response


def register_add_option(app):
    @app.action("add-option")
    def handle_choice_added(client, ack, body: dict):
        ack()
        channel = body['channel']['id']
        ts = body['message']['ts']
        modal = create_add_choices()
        modal["private_metadata"] = f"{channel}|{ts}"
        client.views_open(
            trigger_id=body["trigger_id"],
            view=modal,
        )

def register_adding_option(app, manager):
    @app.view("adding-option")
    def handle_add_option_added(client, ack, body: dict):
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

def register_votes(app, manager):
    @app.action(re.compile(r"actionId-\d+"))
    def handle_vote(client, ack, body, action):
        ack()
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

def register_dropdown_vote(app, manager):
    @app.action("poll_option_select")
    def handle_dropdown_vote(client, ack, body, action):
        ack()
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
def register_edit_response(app):
    @app.action("edit-response")
    def handle_edit_response(client, ack, body, logger):
        ack()
        ts = body['message']['ts']
        channel = body['channel']['id']
        modal = which_response_to_edit(ts, channel)
        client.views_open(
            trigger_id=body["trigger_id"],
            view=modal,
        )
        logger.info("view-all-open-ended")

def register_editing_response(app, manager):
    @app.view("editing-response")
    def handle_editing_response(client, ack, body, view, logger):
        ack()
        private_metadata = view.get("private_metadata", "")
        metadata = json.loads(private_metadata) if private_metadata else {}
        ts = metadata.get("ts")
        channel = metadata.get("channel")
        values = view["state"]["values"]
        poll_id = create_id(ts)
        poll = manager.get_poll(poll_id)
        user_id = body["user"]["id"]
        response_num = None
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

def register_submit_edit_response(app, manager):
    @app.view("submit-edit-response")
    def handle_response_change(client, ack, view):
        ack()
        private_metadata = view.get("private_metadata", "")
        metadata = json.loads(private_metadata) if private_metadata else {}
        ts = metadata.get("ts")
        channel = metadata.get("channel")
        response_num = metadata.get("response_num")
        values = view["state"]["values"]
        poll_id = create_id(ts)
        poll = manager.get_poll(poll_id)

        new_response = None
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
