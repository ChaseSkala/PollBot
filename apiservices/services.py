import re

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