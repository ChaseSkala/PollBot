import json

def create_add_choices():
    """
    Creates a menu for the user to add a choice to the poll.
    :returns: A modal.
    """
    modal = {
        "type": "modal",
        "callback_id": "adding-option",
        "title": {
            "type": "plain_text",
            "text": "Add choices",
            "emoji": True
        },
        "submit": {
            "type": "plain_text",
            "text": "Submit",
            "emoji": True
        },
        "close": {
            "type": "plain_text",
            "text": "Cancel",
            "emoji": True
        },
        "blocks": [
            {
                "type": "input",
                "block_id": "add_choice_block",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "choice-added"
                },
                "label": {
                    "type": "plain_text",
                    "text": "Add Choice to Poll",
                    "emoji": True
                }
            }
        ]
    }
    return modal


def which_response_to_edit(ts, channel):
    """
    Creates a menu that prompts the user which response within the poll that they want to edit.

    :param ts: The current timestamp
    :type ts: int
    :param channel: The channel id where the command takes place.
    :type channel: str
    :returns: A modal.
    """
    modal = {
        "type": "modal",
        "callback_id": "editing-response",
        "title": {
            "type": "plain_text",
            "text": "Editing Response",
            "emoji": True
        },
        "submit": {
            "type": "plain_text",
            "text": "Submit",
            "emoji": True
        },
        "close": {
            "type": "plain_text",
            "text": "Cancel",
            "emoji": True
        },
        "private_metadata": json.dumps({
            "ts": ts,
            "channel": channel
        }),
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "Which response do you want to edit/remove?",
                    "emoji": True
                }
            },
            {
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "which-response-to-edit"
                },
                "label": {
                    "type": "plain_text",
                    "text": "Please input the response #",
                    "emoji": True
                }
            }
        ]
    }
    return modal


def editing_response(allowed: bool, ts, channel, response_num):
    """
    Asks the user what they want to edit the response to.

    Creates either a modal that asks the user what they want to change the response to,
    or prompts them that they cannot edit the response that they have chosen.

    :param allowed: Checks if the user is allowed to edi the response.
    :type allowed: bool
    :param ts: The current timestamp.
    :type ts: int
    :param channel: The channel id where the command takes place.
    :type channel: str
    :param response_num: The key that identifies what response the user wants to edit.
    :returns: A modal.
    """

    if allowed:
        modal = {
        "type": "modal",
        "callback_id": "submit-edit-response",
        "title": {
            "type": "plain_text",
            "text": "Editing Response",
            "emoji": True
        },
        "submit": {
            "type": "plain_text",
            "text": "Submit",
            "emoji": True
        },
        "close": {
            "type": "plain_text",
            "text": "Cancel",
            "emoji": True
        },
        "private_metadata": json.dumps({
            "ts": ts,
            "channel": channel,
            "response_num": response_num
        }),
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "What would you like to change the response to?",
                    "emoji": True
                }
            },
            {
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "new-response"
                },
                "label": {
                    "type": "plain_text",
                    "text": "Type REMOVE to remove the response.",
                    "emoji": True
                }
            }
        ]
    }
    else:
        modal = {
            "type": "modal",
            "callback_id": "submit-edit-response",
            "title": {
                "type": "plain_text",
                "text": "Editing Response",
                "emoji": True
            },
            "close": {
                "type": "plain_text",
                "text": "Close",
                "emoji": True
            },
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "You are not allowed to edit this response, due to you not being the creator.",
                        "emoji": True
                    }
                }
            ]
        }
    return modal


def option_warning(rating, user_input, channel, ts):
    """
    Warns the user if they inputted an often rated badly option.

    :param rating: The average rating of the warned option.
    :type rating: float
    :param user_input: The option that the user inputted.
    :type user_input: str
    :param channel: The channel id where the command takes place.
    :type channel: str
    :param ts: The current timestamp.
    :type ts: int
    :returns: A modal.
    """
    modal = {
        "type": "modal",
        "callback_id": "submit-bad-option",
        "private_metadata": json.dumps({
        "channel": channel,
        "ts": ts,
        "option_text": user_input
        }),
        "title": {
            "type": "plain_text",
            "text": "Option Warning",
            "emoji": True
        },
        "submit": {
            "type": "plain_text",
            "text": "Submit",
            "emoji": True
        },
        "close": {
            "type": "plain_text",
            "text": "Cancel",
            "emoji": True
        },
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"Your option is often rated poorly ({rating} :star:), do you still want to add it?",
                    "emoji": True
                }
            }
        ]
    }
    return modal