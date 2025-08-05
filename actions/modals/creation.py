def create_home_menu():
    """
    Creates the home menu.
    :returns: A Modal.
    """
    blocks = {
        "type": "modal",
        "callback_id": "home-menu",
        "title": {
            "type": "plain_text",
            "text": "Create a poll",
            "emoji": True
        },
        "close": {
            "type": "plain_text",
            "text": "Cancel",
            "emoji": True
        },
        "blocks": [
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": ":capital_abcd: Multiple Choice",
                            "emoji": True
                        },
                        "value": "multiple-choice",
                        "action_id": "multiple-choice"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": ":speech_balloon: Open Ended",
                            "emoji": True
                        },
                        "value": "open-ended",
                        "action_id": "open-ended"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": ":card_index_dividers: Create from previous poll",
                            "emoji": True
                        },
                        "value": "create-from-previous-poll",
                        "action_id": "create-from-previous-poll"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": ":card_file_box: Use A Template",
                            "emoji": True
                        },
                        "value": "create-from-template",
                        "action_id": "create-from-template"
                    }
                ]
            }
        ]
    }
    return blocks


def create_multiple_choice():
    """
    Creates the multiple choice menu.
    :returns: A Modal.
    """
    blocks = {
        "type": "modal",
        "callback_id": "multiple-choice",
        "title": {
            "type": "plain_text",
            "text": "Rodger",
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
                    "text": "Create A Poll",
                    "emoji": True
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "question_input"
                },
                "label": {
                    "type": "plain_text",
                    "text": "Create question",
                    "emoji": True
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "multiline": True,
                    "action_id": "choices_input"
                },
                "label": {
                    "type": "plain_text",
                    "text": "Create options (Separate with new lines)",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Settings*"
                },
                "accessory": {
                    "type": "checkboxes",
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Anonymous",
                                "emoji": True
                            },
                            "value": "anonymous"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Can users add new choices?",
                                "emoji": True
                            },
                            "value": "can-users-add-new-choices"
                        }
                    ],
                    "action_id": "checkboxes-action"
                }
            }
        ]
    }
    return blocks


def create_open_ended():
    """
    Creates the open-ended menu.
    :returns: A modal.
    """
    blocks = {
        "type": "modal",
        "callback_id": "open-ended",
        "title": {
            "type": "plain_text",
            "text": "Create a poll",
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
                "type": "divider"
            },
            {
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "question_input"
                },
                "label": {
                    "type": "plain_text",
                    "text": "Create question",
                    "emoji": True
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Settings*"
                },
                "accessory": {
                    "type": "checkboxes",
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Anonymous",
                                "emoji": True
                            },
                            "value": "anonymous"
                        }
                    ],
                    "action_id": "checkboxes-action"
                },
            },
            {
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "max-options"
                },
                "label": {
                    "type": "plain_text",
                    "text": "Max amount of options per person. (Put 999 for no limit.)",
                    "emoji": True
                }
            }
        ]
    }
    return blocks


def open_templates():
    """
    Creates the template menu.
    :returns: A modal.
    """
    blocks = {
        "title": {
            "type": "plain_text",
            "text": "Templates",
            "emoji": True
        },
        "type": "modal",
        "callback_id": "open-ended",
        "close": {
            "type": "plain_text",
            "text": "Cancel",
            "emoji": True
        },
        "blocks": [
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": ":pencil2: Create a template",
                            "emoji": True
                        },
                        "value": "create-template",
                        "action_id": "create-template"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": ":file_folder: View Templates",
                            "emoji": True
                        },
                        "value": "view-templates",
                        "action_id": "view-templates"
                    }
                ]
            }
        ]
    }
    return blocks
