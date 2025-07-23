import json

def create_add_choices():
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