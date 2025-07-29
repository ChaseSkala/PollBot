import re

from actions.modals.history import show_poll_history
from actions.modals.results import all_open_ended, all_results
from actions.modals.templatedetails import show_oe_template_details, show_mc_template_details
from generalservices import create_id

from models import Poll

def register_poll_button(app, session):
    @app.action(re.compile(r"poll_button-\d+"))
    def handle_poll_button(client, ack, body, action, logger):
        ack()
        channel = body['view']["private_metadata"]
        poll_id = str(action["value"])
        poll = session.query(Poll).filter_by(poll_id=poll_id).first()

        is_open_ended = poll.options[0].text == 'Add your responses!'

        if poll.is_template:
            if is_open_ended:
                modal = show_oe_template_details(poll)
                logger.info("view-all-open-ended")
            else:
                modal = show_mc_template_details(poll)
                logger.info("results")
        else:
            if is_open_ended:
                modal = all_open_ended(poll, channel)
                logger.info("view-all-open-ended")
            else:
                modal = all_results(poll, channel)
                logger.info("results")

        modal["private_metadata"] = channel
        client.views_update(
            view_id=body['view']['id'],
            view=modal,
        )

def register_results(app, session):
    @app.action("results")
    def handle_results(client, ack, body, logger):
        ack()
        ts = body['message']['ts']
        channel = body['channel']['id']
        poll_id = create_id(ts)
        poll = session.query(Poll).filter_by(poll_id=poll_id).first()
        modal = all_results(poll, channel)
        modal["private_metadata"] = channel
        client.views_open(
            trigger_id=body["trigger_id"],
            view=modal,
        )
        logger.info("results")

def register_view_all_open_ended(app, session):
    @app.action("view-all-open-ended")
    def handle_view_all_open_ended(client, ack, body, logger):
        ack()
        ts = body['message']['ts']
        channel = body['channel']['id']
        poll_id = create_id(ts)
        poll = session.query(Poll).filter_by(poll_id=poll_id).first()
        modal = all_open_ended(poll, channel)
        modal["private_metadata"] = channel
        client.views_open(
            trigger_id=body["trigger_id"],
            view=modal,
        )
        logger.info("view-all-open-ended")

def register_search_action(app, session):
    @app.options("search_action")
    def handle_search_action(ack, body):
        user_input = body.get("value", "")
        if user_input:
            polls = session.query(Poll).filter(
                Poll.question.ilike(f"%{user_input}%"),
                Poll.is_template == False
            ).all()
        else:
            polls = session.query(Poll).filter_by(is_template=False).limit(10).all()
        options = [
            {
                "text": {"type": "plain_text", "text": poll.question},
                "value": poll.poll_id
            }
            for poll in polls
        ]
        ack(options=options)

def register_show_search_action(app, session):
    @app.action("search_action")
    def handle_show_search_action(client, ack, body, logger):
        ack()
        poll_id = body["actions"][0]["selected_option"]["value"]

        poll = session.query(Poll).filter_by(poll_id=poll_id).first()

        channel = body["view"]["private_metadata"]

        if poll.options[0].text == 'Add your responses!':
            modal = all_open_ended(poll, channel)
        else:
            modal = all_results(poll, channel)
        modal["private_metadata"] = channel
        client.views_update(
            view_id=body['view']['id'],
            view=modal,
        )
        logger.info("view-all-results")


def register_sort_action(app, session):
    @app.action("sort_action")
    def handle_sort_action(ack, body, client):
        ack()

        sort_by = body["actions"][0]["selected_option"]["value"]

        channel_id = body["view"]["private_metadata"]

        updated_modal = show_poll_history(session, sort_by=sort_by)
        updated_modal["private_metadata"] = channel_id

        client.views_update(
            view_id=body["view"]["id"],
            view=updated_modal
        )