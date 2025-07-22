def render_multiple_choice(poll):
    button_elements = []
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"{poll.question}",
                "emoji": True
            }
        }
    ]

    if len(poll.options) > 5:
        blocks.append({
            "type": "input",
            "element": {
                "type": "static_select",
				"placeholder": {
					"type": "plain_text",
					"text": "Select options",
					"emoji": True
            },
            "options": [
                {
                    "text": {
                        "type": "plain_text",
                        "text": option.text if hasattr(option, 'text') else str(option),
                        "emoji": True
                    },
                    "value": str(i)
                }
                for i, option in enumerate(poll.options)
            ],
            "action_id": "poll_option_select"
            },
            "label": {
                "type": "plain_text",
                "text": "Label",
                "emoji": True
            }
        })
    else:
        for i, option in enumerate(poll.options):
            button_elements.append({
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": option.text if hasattr(option, 'text') else str(option),
                    "emoji": True
                },
                "value": f"option_{i}",
                "action_id": f"actionId-{i}"
            })
        if poll.can_add_choices:
            button_elements.append({
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "+ Add Option",
                    "emoji": True
                },
                "value": "add-option",
                "action_id": "add-option"
            })
        blocks.append({
            "type": "actions",
            "elements": button_elements
        })
    if poll.anonymous:
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "plain_text",
                    "text": f"Sender: {poll.creator} | Responses: Anonymous",
                    "emoji": True
                }
            ]
        })
    else:
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "plain_text",
                    "text": f"Sender: {poll.creator} | Responses: Non-Anonymous",
                    "emoji": True
                }
            ]
        })
    blocks.append({
        "type": "context",
        "elements": [
            {
                "type": "plain_text",
                "text": f"PollID: {poll.poll_id}",
                "emoji": True
            }
        ]
    })

    return blocks

def render_open_ended(poll):
    button_elements = []
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"{poll.question}",
                "emoji": True
            }
        }
    ]

    button_elements.append({
        "type": "button",
        "text": {
            "type": "plain_text",
            "text": "Add Response",
            "emoji": True
        },
        "value": "add-option",
        "action_id": "add-option"
    })
    blocks.append({
        "type": "actions",
        "elements": button_elements
    })
    if poll.anonymous:
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "plain_text",
                    "text": f"Sender: {poll.creator} | Responses: Anonymous",
                    "emoji": True
                }
            ]
        })
    else:
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "plain_text",
                    "text": f"Sender: {poll.creator} | Responses: Non-Anonymous",
                    "emoji": True
                }
            ]
        })
    blocks.append({
        "type": "context",
        "elements": [
            {
                "type": "plain_text",
                "text": f"PollID: {poll.poll_id}",
                "emoji": True
            }
        ]
    })
    return blocks

def render_multiple_choice_options(poll):
    blocks = render_multiple_choice(poll)
    fields = []

    for i, option in enumerate(poll.options):
        if option.votes == 0:
            continue
        votes = option.votes
        percentage = poll.percentages[i]
        poll_percentage = round(percentage)
        filled = round(percentage / 5)
        empty = 30 - filled
        bar = "█" * filled + " " * empty
        label = f"*{option.text}*"
        bar_text = f"`{bar}` |  {poll_percentage}% ({option.votes})"

        field_text = f"{label}\n{bar_text}"
        if not poll.anonymous and votes > 0:
            voter_mentions = ", ".join(f"<@{uid}>" for uid in option.voters.keys())
            field_text += f"\n_{voter_mentions}_"


        fields.append({
            "type": "mrkdwn",
            "text": field_text
        })
    if fields:
        blocks.append({
            "type": "section",
            "fields": fields
        })

        blocks.append({"type": "divider"})
        blocks.append({
			"type": "actions",
			"elements": [
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "View Results",
						"emoji": True
					},
					"value": "click_me_123",
					"action_id": "results"
				}
			]
		})
    return blocks


def render_open_ended_options(poll):
    button_elements = []
    response_total = 0
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"{poll.question}",
                "emoji": True
            }
        }
    ]

    fields = []

    for i, option in enumerate(poll.options):

        if option.text == 'Add your responses!':
            continue
        if response_total >= 8:
            response_total = response_total + 1
            continue

        user_id = str(next(iter(option.voters.keys())))

        if i not in option.response_user_ids:
            poll.options[i].add_user(user_id, i)

        if not poll.anonymous:
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

        response_total = response_total + 1

    blocks.append({
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": f"Responses({response_total})",
            "emoji": True
        }
    })

    if fields:
        blocks.append({
            "type": "section",
            "fields": fields
        })

        blocks.append({"type": "divider"})

    button_elements.append({
        "type": "button",
        "text": {
            "type": "plain_text",
            "text": "Add Response",
            "emoji": True
        },
        "value": "add-option",
        "action_id": "add-option"
    })
    button_elements.append({
        "type": "button",
        "text": {
            "type": "plain_text",
            "text": "Edit/Remove Response",
            "emoji": True
        },
        "value": "edit-response",
        "action_id": "edit-response"
    })
    button_elements.append({
        "type": "button",
        "text": {
            "type": "plain_text",
            "text": "View All Responses",
            "emoji": True
        },
        "value": "view-all-open-ended",
        "action_id": "view-all-open-ended"
    })
    blocks.append({
        "type": "actions",
        "elements": button_elements
    })
    if poll.anonymous:
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "plain_text",
                    "text": f"Sender: {poll.creator} | Responses: Anonymous",
                    "emoji": True
                }
            ]
        })
    else:
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "plain_text",
                    "text": f"Sender: {poll.creator} | Responses: Non-Anonymous",
                    "emoji": True
                }
            ]
        })
    blocks.append({
        "type": "context",
        "elements": [
            {
                "type": "plain_text",
                "text": f"PollID: {poll.poll_id}",
                "emoji": True
            }
        ]
    })
    return blocks

def render_history(history):
    lines = []
    for poll in history:
        lines.append(
            f"```Created: {poll.creation_date} \nPoll ID: {poll.poll_id} \nPoll Question:  {poll.question}\nThe winner of the poll was: {poll.winner}```"
        )
    poll_lines = "\n".join(lines)
    return (
        f"*You are currently viewing the Poll History*\n"
        f"{poll_lines}"
    )