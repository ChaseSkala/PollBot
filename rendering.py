def render_results(poll):
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
                        "text": option.text,
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
                    "text": option.text,
                    "emoji": True
                },
                "value": f"option_{i}",
                "action_id": f"actionId-{i}"
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


def render_options(poll, user_id):
    blocks = render_results(poll)
    fields = []

    for i, option in enumerate(poll.options):
        if option.votes == 0:
            continue
        votes = option.votes
        percentage = poll.percentages[i]
        poll_percentage = round(percentage)
        filled = round(percentage / 5)
        empty = 20 - filled
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
					"action_id": "Results"
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