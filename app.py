import os
import logging


from apiservices.creation import register_poll_command, register_open_ended, register_multiple_choice, \
    register_create_open_ended_poll, register_create_multiple_choice_poll, register_create_previous_poll
from apiservices.history import register_get_history, register_create_from_previous_poll, register_back_to_history
from apiservices.modifications import register_add_option, register_adding_option, register_votes, \
    register_dropdown_vote, register_edit_response, register_editing_response, register_submit_edit_response
from apiservices.services import register_poll_button, register_results, register_view_all_open_ended
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
register_get_history(app)
register_create_from_previous_poll(app)
register_open_ended(app)
register_multiple_choice(app)
register_add_option(app)
register_adding_option(app)
register_create_open_ended_poll(app)
register_create_multiple_choice_poll(app)
register_votes(app)
register_back_to_history(app)
register_poll_button(app)
register_create_previous_poll(app)
register_dropdown_vote(app)
register_results(app)
register_view_all_open_ended(app)
register_edit_response(app)
register_editing_response(app)
register_submit_edit_response(app)

if __name__ == "__main__":
    SocketModeHandler(app, SLACK_APP_TOKEN).start()