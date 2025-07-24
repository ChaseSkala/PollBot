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
                "text": "Select an option",
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