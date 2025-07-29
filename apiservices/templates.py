import datetime

from actions.modals.templates import open_template_types, create_mc_template, create_oe_template, show_all_templates
from generalservices import create_id
from models import Poll, PollOption


def register_open_template_types(app):
    @app.action("create-template")
    def handle_open_template_types(client, ack, body):
        ack()
        modal = open_template_types()
        modal["private_metadata"] = body["view"]["private_metadata"]
        client.views_update(
            view_id=body["view"]["id"],
            view=modal,
        )

def register_view_all_templates(app, session):
    @app.action("view-templates")
    def handle_view_all_templates(client, ack, body):
        ack()
        modal = show_all_templates(session, sort_by="newest")
        modal["private_metadata"] = body["view"]["private_metadata"]
        client.views_update(
            view_id=body["view"]["id"],
            view=modal,
        )

def register_create_mc_template(app):
    @app.action("multiple-choice-template")
    def handle_create_mc_template(client, ack, body):
        ack()
        modal = create_mc_template()
        modal["private_metadata"] = body["view"]["private_metadata"]
        client.views_update(
            view_id=body["view"]["id"],
            view=modal,
        )

def register_store_mc_template(app, session):
    @app.view("mc-template-created")
    def handle_store_template(client, ack, body, view, logger):
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

        current_time = float(datetime.datetime.now().timestamp())
        template_id = create_id(current_time)
        pollID = create_id(template_id)
        poll = Poll(
            poll_id=pollID,
            question=question,
            creator=user_name,
            channel_id=channel_id,
            creation_date=current_time,
            max_option_count=max_responses_count,
            anonymous=anon_enabled,
            can_add_choices=can_add_choices,
            user_option_count={},
            is_template=True
        )
        session.add(poll)

        for choice in options:
            option = PollOption(text=choice, votes=0, voters={}, response_user_ids={})
            poll.options.append(option)

        session.commit()

def register_create_oe_template(app):
    @app.action("open-ended-template")
    def handle_create_oe_template(client, ack, body):
        ack()
        modal = create_oe_template()
        modal["private_metadata"] = body["view"]["private_metadata"]
        client.views_update(
            view_id=body["view"]["id"],
            view=modal,
        )

def register_store_oe_template(app, session):
    @app.view("oe-template-created")
    def handle_store_oe_template(client, ack, body, view, logger):
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
        current_time = float(datetime.datetime.now().timestamp())
        template_id = create_id(current_time)
        pollID = create_id(template_id)
        poll = Poll(
            poll_id=pollID,
            question=question,
            creator=user_name,
            channel_id=channel_id,
            creation_date=current_time,
            max_option_count=max_responses_count,
            anonymous=anon_enabled,
            can_add_choices=True,
            user_option_count={},
            is_template=True
        )
        session.add(poll)

        option = PollOption(text='Add your responses!', votes=0, voters={}, response_user_ids={})
        poll.options.append(option)

        session.commit()
