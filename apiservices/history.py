from actions.modals.history import show_poll_history


def register_get_history(app, manager):
    @app.command("/history")
    def get_history(client, ack, command: dict):
        ack()
        modal = show_poll_history(manager)
        channel = command["channel_id"]
        modal["private_metadata"] = channel
        client.views_open(
            trigger_id=command["trigger_id"],
            view=modal,
        )

def register_create_from_previous_poll(app, manager):
    @app.action("create-from-previous-poll")
    def create_from_previous_poll(client, ack, body: dict):
        ack()
        modal = show_poll_history(manager)
        channel = body['view']["private_metadata"]
        modal["private_metadata"] = channel
        client.views_update(
            view_id=body["view"]["id"],
            view=modal,
        )

def register_back_to_history(app, manager):
    @app.action("back_to_history")
    def handle_back_to_history(client, ack, body, logger):
        ack()
        channel = body['view']["private_metadata"]
        modal = show_poll_history(manager)
        modal["private_metadata"] = channel
        try:
            client.views_update(
                view_id=body['view']['id'],
                view=modal
            )
        except Exception as e:
            logger.error(f"Error updating modal: {e}")