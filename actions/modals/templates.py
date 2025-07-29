from generalservices import sort_polls
from models import Poll, PollOption


def open_template_types():
    blocks = {
        "title": {
            "type": "plain_text",
            "text": "What kind of poll?",
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
                            "text": ":capital_abcd: Multiple Choice",
                            "emoji": True
                        },
                        "value": "multiple-choice",
                        "action_id": "multiple-choice-template"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": ":speech_balloon: Open Ended",
                            "emoji": True
                        },
                        "value": "open-ended",
                        "action_id": "open-ended-template"
                    }
                ]
            }
        ]
    }
    return blocks

def create_mc_template():
    blocks = {
        "title": {
            "type": "plain_text",
            "text": "Create A Template",
            "emoji": True
        },
        "submit": {
            "type": "plain_text",
            "text": "Save"
        },
        "type": "modal",
        "callback_id": "mc-template-created",
        "close": {
            "type": "plain_text",
            "text": "Cancel",
            "emoji": True
        },
        "blocks": [
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

def create_oe_template():
    blocks = {
        "type": "modal",
        "callback_id": "oe-template-created",
        "title": {
            "type": "plain_text",
            "text": "Create a poll",
            "emoji": True
        },
        "submit": {
            "type": "plain_text",
            "text": "Save",
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

def show_all_templates(session, sort_by="newest"):
    modal_blocks = []

    polls = session.query(Poll).filter_by(is_template=True).all()

    if not polls:
        modal_blocks.append({
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": ":open_file_folder: You have not created any templates.",
                "emoji": True
            }
        })

    sorted_polls = sort_polls(polls, sort_by)

    for i, poll in enumerate(sorted_polls):

        if poll.options[0].text == 'Add your responses!':
            modal_blocks.append({
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "text": f"{poll.question}",
                    "emoji": True
                }
            })
            modal_blocks.append({
                "type": "context",
                "elements": [
                    {
                        "type": "plain_text",
                        "text": f"This is an open ended template.",
                        "emoji": True
                    }
                ]
            })
            modal_blocks.append({
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Use this template",
                            "emoji": True
                        },
                        "value": f"{poll.poll_id}",
                        "action_id": f"poll_button-{i}"
                    }
                ]
            })
            modal_blocks.append({"type": "divider"})
        else:
            modal_blocks.append({
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "text": f"{poll.question}",
                    "emoji": True
                }
            })
            modal_blocks.append({
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Use this template",
                            "emoji": True
                        },
                        "value": f"{poll.poll_id}",
                        "action_id": f"poll_button-{i}"
                    }
                ]
            })
            modal_blocks.append({"type": "divider"})
    return {
        "type": "modal",
        "title": {
            "type": "plain_text",
            "text": "Templates",
            "emoji": True
        },
        "close": {
            "type": "plain_text",
            "text": "Cancel",
            "emoji": True
        },
        "blocks": modal_blocks
    }
