import os
import logging


from apiservices.creation import register_poll_command, register_open_ended, register_multiple_choice, \
    register_create_open_ended_poll, register_create_multiple_choice_poll, register_create_previous_poll
from apiservices.history import register_get_history, register_create_from_previous_poll, register_back_to_history
from apiservices.modifications import register_add_option, register_adding_option, register_votes, \
    register_dropdown_vote, register_edit_response, register_editing_response, register_submit_edit_response
from apiservices.services import register_poll_button, register_results, register_view_all_open_ended, \
    register_search_action, register_show_search_action, register_sort_action
from models import *
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient

logger = logging.getLogger(__name__)

manager = PollManager()

load_dotenv("tokens.env")

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"].strip()
SLACK_APP_TOKEN = os.environ["SLACK_APP_TOKEN"].strip()

if not SLACK_BOT_TOKEN:
    raise ValueError("SLACK_BOT_TOKEN not found in environment")
if not SLACK_APP_TOKEN:
    raise ValueError("SLACK_APP_TOKEN not found in environment")

app = App(token=SLACK_BOT_TOKEN)
client = WebClient(token=SLACK_BOT_TOKEN)

register_poll_command(app)
register_get_history(app, manager)
register_create_from_previous_poll(app, manager)
register_open_ended(app)
register_multiple_choice(app)
register_add_option(app)
register_adding_option(app, manager)
register_create_open_ended_poll(app, manager)
register_create_multiple_choice_poll(app, manager)
register_votes(app, manager)
register_back_to_history(app, manager)
register_poll_button(app, manager)
register_create_previous_poll(app, manager)
register_dropdown_vote(app, manager)
register_results(app, manager)
register_view_all_open_ended(app, manager)
register_edit_response(app)
register_editing_response(app, manager)
register_submit_edit_response(app, manager)
register_search_action(app, manager)
register_show_search_action(app, manager)
register_sort_action(app, manager)

if __name__ == "__main__":
    SocketModeHandler(app, SLACK_APP_TOKEN).start()