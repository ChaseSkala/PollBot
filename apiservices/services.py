import re

from actions.modals.history import show_poll_history
from actions.modals.results import all_open_ended, all_results, render_poll_option_rating
from actions.modals.templatedetails import show_oe_template_details, show_mc_template_details
from generalservices import create_id

from models import Poll, Rating


def register_poll_button(app, session):
    """
    Handles the Slack regex action "poll_button-\d+"

    Creates a modal for a past poll based on whichever the button is attached to.

    :param app: The Slack App.
    :type app: Slack app.
    :param session: A SQLAlchemy session object.
    :type session: SQLAlchemy session.
    :returns: Creates a modal.
    """

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
    """
    Handles the Slack action "results"

    Opens a modal for the user that displays the results of the poll.
    :param app: The Slack app.
    :type app: Slack app.
    :param session: A SQLAlchemy session object.
    :type session: SQLAlchemy session.
    :returns: A modal.
    """
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
    """
    Handles the Slack action "view-all-open-ended"

    Opens a modal for the user that displays the results of an open-ended poll.

    :param app: The Slack app.
    :type app: Slack app.
    :param session: A SQLAlchemy session object.
    :type session: SQLAlchemy session.
    :returns: A modal.
    """
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
    """
    Handles the Slack option "search_action"

    Filters through the search bar inside of history.

    :param app: The Slack app.
    :type app: Slack app.
    :param session: A SQLAlchemy session object.
    :type session: SQLAlchemy session.
    :returns: An updated search.
    """
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
    """
    Handles the Slack action "search_action"

    Opens a modal for the user that displays the results of their selected poll.

    :param app: The Slack app.
    :type app: Slack app.
    :param session: A SQLAlchemy session object.
    :type session: SQLAlchemy session.
    :returns: A modal.
    """
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
    """
    Handles the Slack action "sort_action"

    Sorts through the history based on the user's choice.

    :param app: The Slack app.
    :type app: Slack app.
    :param session: A SQLAlchemy session object.
    :type session: SQLAlchemy session.
    :returns: An updated history modal
    """
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


def register_close_poll(app, session):
    """
    Handles the Slack action "close-poll"

    Closes the poll that the user selected.

    :param app: The Slack app.
    :type app: Slack app.
    :param session: A SQLAlchemy session object.
    :type session: SQLAlchemy session.
    :returns: A deleted poll.
    """
    @app.action("close-poll")
    def handle_close_poll(client, ack, body, logger):
        ack()

        poll_id = body["actions"][0]["value"]
        user_id = body["user"]["id"]
        result = client.conversations_open(users=[user_id])
        channel_id = result["channel"]["id"]
        poll = session.query(Poll).filter_by(poll_id=poll_id).first()

        if poll:
            poll.closed = True
            session.commit()
            logger.info(f"Poll {poll_id} closed.")
        else:
            logger.error(f"Poll {poll_id} not found.")

        client.chat_postMessage(
            channel=channel_id,
            text="The poll is now closed. If you want to rate any of the options in the poll, press the button below.",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "The poll is now closed. If you want to rate any of the options in the poll, press the button below."
                    },
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Start rating"},
                            "action_id": "rate-poll-options",
                            "value": f"{poll_id}"
                        }
                    ]
                }
            ]
        )


def register_begin_option_rating(app, session):
    """
    Handles the Slack action "rate-poll-options"

    Opens a modal for the user, prompting them to rate options inside the closed poll.

    :param app: The Slack app.
    :type app: Slack app.
    :param session: A SQLAlchemy session object.
    :type session: SQLAlchemy session.
    :returns: A modal.
    """
    @app.action("rate-poll-options")
    def handle_begin_option_rating(client, ack, body):
        ack()
        channel = body['channel']['id']
        poll_id = body["actions"][0]["value"]
        poll = session.query(Poll).filter_by(poll_id=poll_id).first()
        modal = render_poll_option_rating(poll)
        modal["private_metadata"] = channel
        client.views_open(
            trigger_id=body["trigger_id"],
            view=modal,
        )


def register_create_option_rating(app, session):
    """
    Handles the Slack regex action "option_rated[1-5]"

    Rates the options based on user input.

    :param app: The Slack app.
    :type app: Slack app.
    :param session: A SQLAlchemy session object.
    :type session: SQLAlchemy session.
    :returns: New ratings for options.
    """
    @app.action(re.compile("option_rated[1-5]"))
    def handle_create_option_rating(ack, body, action):
        ack()

        user_id = body["user"]["id"]
        action_id = action["action_id"]
        rating = action_id[-1]
        option = action["value"]

        rating = Rating(
            user_id=user_id,
            option_text=option,
            rating=int(rating)
        )
        session.add(rating)
        session.commit()
