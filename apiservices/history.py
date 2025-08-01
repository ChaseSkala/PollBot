from actions.modals.history import show_poll_history
import json

def register_get_history(app, session):
    @app.command("/history")
    def get_history(client, ack, command: dict):
        ack()
        modal = show_poll_history(session, page=0)
        channel = command["channel_id"]
        modal["private_metadata"] = json.dumps({"channel": channel, "page": 0})
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

def register_handle_next_page(app, session):
    @app.action("next_page")
    def handle_next_page(ack, body, client):
        ack()
        metadata = json.loads(body["view"]["private_metadata"])
        page = metadata.get("page", 0) + 1
        channel = metadata.get("channel")
        modal = show_poll_history(session, page=page)
        modal["private_metadata"] = json.dumps({"channel": channel, "page": page})
        client.views_update(
            view_id=body["view"]["id"],
            view=modal
        )

def register_handle_previous_page(app, session):
    @app.action("prev_page")
    def handle_prev_page(ack, body, client):
        ack()
        metadata = json.loads(body["view"]["private_metadata"])
        page = max(metadata.get("page", 0) - 1, 0)
        channel = metadata.get("channel")
        modal = show_poll_history(session, page=page)
        modal["private_metadata"] = json.dumps({"channel": channel, "page": page})
        client.views_update(
            view_id=body["view"]["id"],
            view=modal
        )