import re

from actions.modals.creation import create_home_menu, create_open_ended, create_multiple_choice, open_templates
from actions.rendering.rendering import render_open_ended, render_multiple_choice
from generalservices import create_id, convert_unix_to_date
from models import Poll, PollOption

def register_poll_command(app):
    """
    Handles the slack command "/poll"

    Opens a modal for the user, prompting the user with the home menu modal.

    :param app: The Slack app object.
    :type app: Slack app.
    :returns: A modal.
    """
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
    """
    Handles the slack action "open-ended"

    Opens a modal for the user, prompting the user with the open-ended poll creation modal.

    :param app: The Slack app object.
    :type app: Slack app.
    :returns: A modal.
    """
    @app.action("open-ended")
    def handle_open_ended(client, ack, body: dict):
        ack()
        modal = create_open_ended()
        modal["private_metadata"] = body["view"]["private_metadata"]
        client.views_update(
            view_id=body["view"]["id"],
            view=modal,
        )


def register_create_open_ended_poll(app, session):
    """
    Handles the slack view "open-ended"

    Creates a poll given information gathered from register_open_ended()

    :param app: The Slack app object.
    :type app: Slack app.
    :param session: The SQLAlchemy session object.
    :type session: sqlalchemy.orm.session.Session
    :returns: Posts a poll to the slack workspace.
    """
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
                for option in selected:
                    if option["value"] == "anonymous":
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
        poll = Poll(
            poll_id=pollID,
            question=question,
            creator=user_name,
            channel_id=channel_id,
            creation_date=creation_date,
            max_option_count=max_responses_count,
            anonymous=anon_enabled,
            can_add_choices=True,
            user_option_count={}
        )

        poll.options = [PollOption(text='Add your responses!')]

        session.add(poll)
        session.commit()

        client.chat_update(
            channel=channel_id,
            ts=response['ts'],
            text="Created OE Poll",
            blocks=render_open_ended(poll)
        )


def register_multiple_choice(app):
    """
    Handles the slack action "multiple-choice"

    Opens a modal for the user, prompting the user with the multiple choice poll creation modal.

    :param app: The Slack app object.
    :type app: Slack app.
    :returns: A modal.
    """
    @app.action("multiple-choice")
    def handle_multiple_choice(client, ack, body: dict):
        ack()
        modal = create_multiple_choice()
        modal["private_metadata"] = body["view"]["private_metadata"]
        client.views_update(
            view_id=body["view"]["id"],
            view=modal,
        )


def register_create_multiple_choice_poll(app, session):
    """
    Handles the slack view "multiple-choice"

    Creates a poll given information gathered from register_multiple_choice()

    :param app: The Slack app object.
    :type app: Slack app.
    :param session: The SQLAlchemy session object.
    :type session: sqlalchemy.orm.session.Session
    :returns: Posts a poll to the slack workspace.
    """
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
                for option in selected:
                    if option["value"] == "anonymous":
                        anon_enabled = True
                    elif option["value"] == "can-users-add-new-choices":
                        can_add_choices = True

        response = client.chat_postMessage(
            channel=channel_id,
            text="Creating poll..."
        )

        pollID = create_id(response['ts'])
        creation_date = convert_unix_to_date(float(response['ts']))
        poll = Poll(
            poll_id=pollID,
            question=question,
            creator=user_name,
            channel_id=channel_id,
            creation_date=creation_date,
            max_option_count=max_responses_count,
            anonymous=anon_enabled,
            can_add_choices=can_add_choices,
            user_option_count={}
        )

        poll.options = [PollOption(text=opt) for opt in options]

        session.add(poll)
        session.commit()

        client.chat_update(
            channel=channel_id,
            ts=response['ts'],
            text="Created MC Poll",
            blocks=render_multiple_choice(poll)
        )


def register_create_previous_poll(app, session):
    """
    Handles the slack regex action "previous-poll-\d+"

    Creates a poll given information gathered a past poll inside the Poll Database.

    :param app: The Slack app object.
    :type app: Slack app.
    :param session: The SQLAlchemy session object.
    :type session: sqlalchemy.orm.session.Session
    :returns: Posts a poll to the slack workspace.
    """
    @app.action(re.compile(r"previous-poll-\d+"))
    def create_previous_poll(client, ack, body, action):
        ack()
        channel_id = body['view']["private_metadata"]
        poll_id = str(action["value"])
        old_poll = session.query(Poll).filter_by(poll_id=poll_id).first()

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
            poll = Poll(
                poll_id=pollID,
                question=old_poll.question,
                creator=user_name,
                channel_id=channel_id,
                creation_date=creation_date,
                max_option_count=old_poll.max_option_count,
                anonymous=old_poll.anonymous,
                can_add_choices=True,
                user_option_count={}
            )

            poll.options = [PollOption(text='Add your responses!')]

            session.add(poll)
            session.commit()
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
            poll = Poll(
                poll_id=pollID,
                question=old_poll.question,
                creator=user_name,
                channel_id=channel_id,
                creation_date=creation_date,
                max_option_count=old_poll.max_option_count,
                anonymous=old_poll.anonymous,
                can_add_choices=old_poll.can_add_choices,
                user_option_count={}
            )

            poll.options = [PollOption(text=opt.text) for opt in old_poll.options]

            session.add(poll)
            session.commit()
            client.chat_update(
                channel=channel_id,
                ts=response['ts'],
                text="Created MC Poll",
                blocks=render_multiple_choice(poll)
            )

def register_open_templates(app):
    @app.action("create-from-template")
    def handle_open_template(client, ack, body):
        ack()
        modal = open_templates()
        modal["private_metadata"] = body["view"]["private_metadata"]
        client.views_update(
            view_id=body["view"]["id"],
            view=modal,
        )