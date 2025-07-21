def create_home_menu():
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
						"text": "Multiple Choice",
						"emoji": True
					},
					"value": "multiple-choice",
					"action_id": "multiple-choice"
				},
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "Open Ended",
						"emoji": True
					},
					"value": "open-ended",
					"action_id": "open-ended"
				}
			]
		}
	]
}
    return blocks

def create_multiple_choice():
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
			}
		}
	]
}
    return blocks


def all_results(poll, channel_id):
    fields = []

    modal_blocks = [
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"<@{poll.creator}> has a question for the members of <#{channel_id}>",
                }
            ]
        },
        {
            "type": "section",
            "text": {
                "type": "plain_text",
                "text": "Results",
                "emoji": True
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "plain_text",
                "text": f"{poll.question}",
                "emoji": True
            }
        }
    ]

    for i, option in enumerate(poll.options):
        if option.text == 'Add your responses!':
            continue
        votes = option.votes
        percentage = poll.percentages[i]
        poll_percentage = round(percentage)
        filled = round(percentage / 5)
        empty = 30 - filled
        if filled == 0:
            bar = " ⁢" * 30
        else:
            bar = "█" * filled + " ⁢" * empty
        label = f"*{option.text}*"
        bar_text = f"`{bar}` |  {poll_percentage}% ({option.votes})"

        field_text = f"{label}\n{bar_text}"
        if not poll.anonymous and votes > 0:
            voter_mentions = ", ".join(f"<@{uid}>" for uid in option.voters.keys())
            field_text += f"\n_{voter_mentions}_"
        modal_blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": field_text
            }
        })
        modal_blocks.append({"type": "divider"})

    return {
        "type": "modal",
        "title": {
            "type": "plain_text",
            "text": "Poll Results",
            "emoji": True
        },
        "close": {
            "type": "plain_text",
            "text": "Cancel",
            "emoji": True
        },
        "blocks": modal_blocks
    }
def all_open_ended(poll, channel_id):
    fields = []

    modal_blocks = [
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"<@{poll.creator}> has a question for the members of <#{channel_id}>",
                }
            ]
        },
        {
            "type": "section",
            "text": {
                "type": "plain_text",
                "text": "Responses",
                "emoji": True
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "plain_text",
                "text": f"{poll.question}",
                "emoji": True
            }
        }
    ]

    for i, option in enumerate(poll.options):
        if option.text == 'Add your responses!':
            continue

        if not poll.anonymous:
            user_id = str(next(iter(option.voters.keys())))
            response_creator = f"<@{user_id}>"
        else:
            response_creator = f"Anonymous"
        label = f"*Response {i}*"
        response_text = f":speech_balloon: {response_creator}: _{option.text}_"

        field_text = f"{label}\n{response_text}"

        fields.append({
            "type": "mrkdwn",
            "text": field_text
        })
        modal_blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": field_text
            }
        })
        modal_blocks.append({"type": "divider"})

    return {
        "type": "modal",
        "title": {
            "type": "plain_text",
            "text": "Poll Responses",
            "emoji": True
        },
        "close": {
            "type": "plain_text",
            "text": "Cancel",
            "emoji": True
        },
        "blocks": modal_blocks
    }
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