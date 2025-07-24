import re

from actions.modals.history import show_poll_history
from actions.modals.results import all_open_ended, all_results
from generalservices import create_id


def register_poll_button(app, manager):
    @app.action(re.compile(r"poll_button-\d+"))
    def handle_poll_button(client, ack, body, action, logger):
        ack()
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

def register_results(app, manager):
    @app.action("results")
    def handle_results(client, ack, body, logger):
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

def register_view_all_open_ended(app, manager):
    @app.action("view-all-open-ended")
    def handle_view_all_open_ended(client, ack, body, logger):
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

def register_search_action(app, manager):
    @app.options("search_action")
    def handle_search_action(ack, body):
        user_input = body.get("value", "")
        filter_options = manager.get_filter_options(user_input)
        options = [
            {
                "text": {"type": "plain_text", "text": question},
                "value": poll_id
            }
            for question, poll_id in filter_options
        ]
        ack(options=options)

def register_show_search_action(app, manager):
    @app.action("search_action")
    def handle_show_search_action(client, ack, body, logger):
        ack()
        poll_id = body["actions"][0]["selected_option"]["value"]

        poll = manager.get_poll(poll_id)

        channel = body["view"]["private_metadata"]

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


def register_sort_action(app, manager):
    @app.action("sort_action")
    def handle_sort_action(ack, body, client):
        ack()

        sort_by = body["actions"][0]["selected_option"]["value"]

        channel_id = body["view"]["private_metadata"]

        updated_modal = show_poll_history(manager, sort_by=sort_by)
        updated_modal["private_metadata"] = channel_id

        client.views_update(
            view_id=body["view"]["id"],
            view=updated_modal
        )