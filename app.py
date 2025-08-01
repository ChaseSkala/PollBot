import os
import logging


from apiservices.creation import register_poll_command, register_open_ended, register_multiple_choice, \
    register_create_open_ended_poll, register_create_multiple_choice_poll, register_create_previous_poll, \
    register_open_templates
from apiservices.history import register_get_history, register_create_from_previous_poll, register_back_to_history
from apiservices.modifications import register_add_option, register_adding_option, register_votes, \
    register_dropdown_vote, register_edit_response, register_editing_response, register_submit_edit_response, \
    register_submit_bad_option
from apiservices.services import register_poll_button, register_results, register_view_all_open_ended, \
    register_search_action, register_show_search_action, register_sort_action, register_close_poll, \
    register_begin_option_rating, register_create_option_rating
from apiservices.templates import register_open_template_types, register_create_mc_template, \
    register_create_oe_template, register_store_mc_template, register_view_all_templates, register_store_oe_template
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient
from sqlalchemy.orm import sessionmaker

from models import *

Session = sessionmaker(bind=engine)
session = Session()


logger = logging.getLogger(__name__)

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
register_get_history(app, session)
register_create_from_previous_poll(app, session)
register_open_ended(app)
register_multiple_choice(app)
register_add_option(app)
register_adding_option(app, session)
register_create_open_ended_poll(app, session)
register_create_multiple_choice_poll(app, session)
register_votes(app, session)
register_back_to_history(app, session)
register_poll_button(app, session)
register_create_previous_poll(app, session)
register_dropdown_vote(app, session)
register_results(app, session)
register_view_all_open_ended(app, session)
register_edit_response(app)
register_editing_response(app, session)
register_submit_edit_response(app, session)
register_search_action(app, session)
register_show_search_action(app, session)
register_sort_action(app, session)
register_open_templates(app)
register_open_template_types(app)
register_create_mc_template(app)
register_create_oe_template(app)
register_store_mc_template(app, session)
register_store_oe_template(app, session)
register_view_all_templates(app, session)
register_close_poll(app, session)
register_begin_option_rating(app, session)
register_create_option_rating(app, session)
register_submit_bad_option(app, session)

if __name__ == "__main__":
    SocketModeHandler(app, SLACK_APP_TOKEN).start()