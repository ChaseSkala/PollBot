import re

from actions.modals.creation import create_home_menu, create_open_ended, create_multiple_choice
from actions.rendering.rendering import render_open_ended, render_multiple_choice
from generalservices import create_id, convert_unix_to_date


def register_poll_command(app):
    @app.command("/poll")
    def handle_poll_command(client, ack, command: dict):
        ack()
        modal = create_home_menu()
        modal["private_metadata"] = command["channel_id"]
        client.views_open(
            trigger_id=command["trigger_id"],
            view=modal,
        )

def register_open_ended(app):
    @app.action("open-ended")
    def handle_open_ended(client, ack, body: dict):
        ack()
        modal = create_open_ended()
        modal["private_metadata"] = body["view"]["private_metadata"]
        client.views_update(
            view_id=body["view"]["id"],
            view=modal,
        )

def register_create_open_ended_poll(app, manager):
    @app.view("open-ended")
    def create_open_ended_poll(client, ack, body, view, logger):
        ack()
        values = view["state"]["values"]
        question = None
        anon_enabled = False
        max_responses_count = None
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

def register_multiple_choice(app):
    @app.action("multiple-choice")
    def handle_multiple_choice(client, ack, body: dict):
        ack()
        modal = create_multiple_choice()
        modal["private_metadata"] = body["view"]["private_metadata"]
        client.views_update(
            view_id=body["view"]["id"],
            view=modal,
        )

def register_create_multiple_choice_poll(app, manager):
    @app.view("multiple-choice")
    def create_multiple_choice_poll(client, ack, body, view,logger):
        ack()
        values = view["state"]["values"]
        question = None
        options = None
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
            poll_id=pollID,
            question=question,
            options=options,
            creator=user_name,
            channel_id=channel_id,
            creation_date=creation_date,
            max_option_count=max_responses_count,
            anonymous=anon_enabled,
            can_add_choices=can_add_choices,
        )
        client.chat_update(
            channel=channel_id,
            ts=response['ts'],
            text="Created MC Poll",
            blocks=render_multiple_choice(poll)
        )

def register_create_previous_poll(app, manager):
    @app.action(re.compile(r"previous-poll-\d+"))
    def create_previous_poll(client, ack, body, action):
        ack()
        channel_id = body['view']["private_metadata"]
        poll_id = str(action["value"])
        old_poll = manager.get_poll(poll_id)

        user_id = body["user"]["id"]
        user_info = client.users_info(user=user_id)
        user_name = user_info["user"]["name"]

        if old_poll.options[0].text == 'Add your responses!':
            response = client.chat_postMessage(
                channel=channel_id,
                text="Creating poll..."
            )

            pollID = create_id(response['ts'])
            creation_date = convert_unix_to_date(float(response['ts']))
            poll = manager.create_poll(
                poll_id=pollID,
                question=old_poll.question,
                options=['Add your responses!'],
                creator=user_name,
                channel_id=channel_id,
                creation_date=creation_date,
                max_option_count=old_poll.max_option_count,
                anonymous=old_poll.anonymous,
                can_add_choices=True,
            )
            client.chat_update(
                channel=channel_id,
                ts=response['ts'],
                text="Created OE Poll",
                blocks=render_open_ended(poll)
            )
        else:
            response = client.chat_postMessage(
                channel=channel_id,
                text="Creating poll..."
            )

            pollID = create_id(response['ts'])
            creation_date = convert_unix_to_date(float(response['ts']))
            poll = manager.create_poll(
                poll_id=pollID,
                question=old_poll.question,
                options=[opt.text for opt in old_poll.options],
                creator=user_name,
                channel_id=channel_id,
                creation_date=creation_date,
                max_option_count=old_poll.max_option_count,
                anonymous=old_poll.anonymous,
                can_add_choices=old_poll.can_add_choices,
            )
            client.chat_update(
                channel=channel_id,
                ts=response['ts'],
                text="Created MC Poll",
                blocks=render_multiple_choice(poll)
            )