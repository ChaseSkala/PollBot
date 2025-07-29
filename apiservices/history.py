from actions.modals.history import show_poll_history
from models import Poll, PollOption


def register_get_history(app, session):
    @app.command("/history")
    def get_history(client, ack, command: dict):
        ack()
        modal = show_poll_history(session)
        channel = command["channel_id"]
        modal["private_metadata"] = channel
        client.views_open(
            trigger_id=command["trigger_id"],
            view=modal,
        )

def register_create_from_previous_poll(app, session):
    @app.action("create-from-previous-poll")
    def create_from_previous_poll(client, ack, body: dict):
        ack()
        modal = show_poll_history(session)
        channel = body['view']["private_metadata"]
        modal["private_metadata"] = channel
        client.views_update(
            view_id=body["view"]["id"],
            view=modal,
        )

def register_back_to_history(app, session):
    @app.action("back_to_history")
    def handle_back_to_history(client, ack, body, logger):
        ack()
        channel = body['view']["private_metadata"]
        modal = show_poll_history(session)
        modal["private_metadata"] = channel
        try:
            client.views_update(
                view_id=body['view']['id'],
                view=modal
            )
        except Exception as e:
            logger.error(f"Error updating modal: {e}")