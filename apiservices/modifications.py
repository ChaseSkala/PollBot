import json
import re

from actions.modals.modification import create_add_choices, which_response_to_edit, editing_response, option_warning
from actions.rendering.options import render_open_ended_options, render_multiple_choice_options
from generalservices import create_id, can_add_more_options, change_response
from sqlalchemy import func
from sqlalchemy.orm.attributes import flag_modified
from models import Poll, PollOption, Rating


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

def register_adding_option(app, session):
    @app.view("adding-option")
    def handle_add_option_added(client, ack, body: dict):
        ack()

        channel, ts = body['view']['private_metadata'].split('|')
        poll_id = create_id(ts)
        poll = session.query(Poll).filter_by(poll_id=poll_id).first()
        user_input = body['view']['state']['values']['add_choice_block']['choice-added']['value']
        user_id = body['user']['id']
        user_info = client.users_info(user=user_id)
        user_name = user_info["user"]["name"]
        option_text = session.query(Rating).filter_by(option_text=user_input).first()

        if option_text:
            rating_avg = session.query(
                Rating.option_text,
                func.avg(Rating.rating).label('average_rating')
            ).filter(
                Rating.option_text == user_input
            ).group_by(Rating.option_text).first()

            if rating_avg:
                avg_rating = float(rating_avg.average_rating)
                if avg_rating <=3:
                    client.views_open(
                        trigger_id=body["trigger_id"],
                        view=option_warning(avg_rating, user_input, channel, ts),
                    )
                    return

        if poll.closed:
            client.chat_postEphemeral(
                channel=channel,
                user=user_id,
                text="This poll is closed.",
            )

        if can_add_more_options(poll, user_id):
            new_option = PollOption(
                text=user_input,
                votes=1,
                voters={user_id: user_name},
                response_user_ids={}
            )
            poll.options.append(new_option)
            response_num = len(poll.options)
            new_option.add_user(user_id, response_num)

            if not hasattr(poll, 'user_option_count') or poll.user_option_count is None:
                poll.user_option_count = {}

            if user_id in poll.user_option_count:
                poll.user_option_count[user_id] += 1
            else:
                poll.user_option_count[user_id] = 1
            flag_modified(poll, 'user_option_count')
            session.commit()

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
        else:
            client.chat_postEphemeral(
                channel=channel,
                user=user_id,
                text=f"You cannot add any more options!",
            )

def register_submit_bad_option(app, session):
    @app.view("submit-bad-option")
    def handle_submit_bad_option(client, ack, body, view):
        ack()

        private_metadata = body["view"]["private_metadata"]
        data = json.loads(private_metadata)
        option_text = data["option_text"]
        channel= data['channel']
        ts = data['ts']
        user_id = body['user']['id']
        user_info = client.users_info(user=user_id)
        user_name = user_info["user"]["name"]
        new_option = PollOption(
            text=option_text,
            votes=1,
            voters={user_id: user_name},
            response_user_ids={}
        )
        poll_id = create_id(ts)
        poll = session.query(Poll).filter_by(poll_id=poll_id).first()
        poll.options.append(new_option)

        if not can_add_more_options(poll, user_id):
            client.chat_postEphemeral(
                channel=channel,
                user=user_id,
                text=f"You cannot add any more options!",
            )
            return

        response_num = len(poll.options)
        new_option.add_user(user_id, response_num)

        if not hasattr(poll, 'user_option_count') or poll.user_option_count is None:
            poll.user_option_count = {}

        if user_id in poll.user_option_count:
            poll.user_option_count[user_id] += 1
        else:
            poll.user_option_count[user_id] = 1
        flag_modified(poll, 'user_option_count')
        session.commit()

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

def register_votes(app, session):
    @app.action(re.compile(r"actionId-\d+"))
    def handle_vote(client, ack, body, action):
        ack()
        action_id = action["action_id"]
        index = int(action_id.split('-')[1])
        ts = body['message']['ts']
        channel = body['channel']['id']
        poll_id = create_id(ts)
        poll = session.query(Poll).filter_by(poll_id=poll_id).first()
        if index < 0 or index >= len(poll.options):
            client.chat_postEphemeral(
                channel=channel,
                user=body["user"]["id"],
                text="Invalid option selected!"
            )
            return

        user_id = body["user"]["id"]
        user_info = client.users_info(user=user_id)
        username = (user_info["user"]["profile"].get("display_name") or
                    user_info["user"].get("real_name") or
                    user_info["user"]["name"])
        if poll.closed:
            client.chat_postEphemeral(
                channel=channel,
                user=user_id,
                text="This poll is closed.",
            )
        option = poll.options[index]

        if user_id in option.voters:
            option.remove_vote(user_id)
        else:
            option.add_vote(user_id, username)

        session.commit()

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

def register_dropdown_vote(app, session):
    @app.action("poll_option_select")
    def handle_dropdown_vote(client, ack, body, action):
        ack()
        index = int(action["selected_option"]["value"])
        ts = body['message']['ts']
        channel = body['channel']['id']
        poll_id = create_id(ts)
        poll = session.query(Poll).filter_by(poll_id=poll_id).first()
        if index < 0 or index >= len(poll.options):
            client.chat_postEphemeral(
                channel=channel,
                user=body["user"]["id"],
                text="Invalid option selected!"
            )
            return

        user_id = body["user"]["id"]
        user_info = client.users_info(user=user_id)
        username = (user_info["user"]["profile"].get("display_name") or
                    user_info["user"].get("real_name") or
                    user_info["user"]["name"])
        if poll.closed:
            client.chat_postEphemeral(
                channel=channel,
                user=user_id,
                text="This poll is closed.",
            )
        option = poll.options[index]

        if user_id in option.voters:
            option.remove_vote(user_id)
        else:
            option.add_vote(user_id, username)

        session.commit()

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

def register_editing_response(app, session):
    @app.view("editing-response")
    def handle_editing_response(client, ack, body, view, logger):
        ack()
        private_metadata = view.get("private_metadata", "")
        metadata = json.loads(private_metadata) if private_metadata else {}
        ts = metadata.get("ts")
        channel = metadata.get("channel")
        values = view["state"]["values"]
        poll_id = create_id(ts)
        poll = session.query(Poll).filter_by(poll_id=poll_id).first()
        user_id = body["user"]["id"]
        if poll.closed:
            client.chat_postEphemeral(
                channel=channel,
                user=user_id,
                text="This poll is closed.",
            )
        response_num = None
        for block_id, block_data in values.items():
            if "which-response-to-edit" in block_data:
                response_num = block_data["which-response-to-edit"]["value"]
            else:
                print("No response num to edit")

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

def register_submit_edit_response(app, session):
    @app.view("submit-edit-response")
    def handle_response_change(client, ack, body, view):
        ack()
        private_metadata = view.get("private_metadata", "")
        metadata = json.loads(private_metadata) if private_metadata else {}
        ts = metadata.get("ts")
        channel = metadata.get("channel")
        response_num = metadata.get("response_num")
        values = view["state"]["values"]
        poll_id = create_id(ts)
        poll = session.query(Poll).filter_by(poll_id=poll_id).first()
        user_id = body["user"]["id"]
        if poll.closed:
            client.chat_postEphemeral(
                channel=channel,
                user=user_id,
                text="This poll is closed.",
            )

        new_response = None
        for block_id, block_data in values.items():
            if "new-response" in block_data:
                new_response = block_data["new-response"]["value"]
            else:
                print("No response num to edit")

        change_response(response_num, new_response, poll)

        session.commit()

        blocks = render_open_ended_options(poll)
        client.chat_update(
            channel=channel,
            ts=ts,
            text="Poll update",
            blocks=blocks
        )
