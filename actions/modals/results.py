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
        filled = round(percentage * 30 / 100)
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
    modal_blocks.append({
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "View Poll History",
                    "emoji": True
                },
                "action_id": "back_to_history"
            }
        ]
    })
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
    modal_blocks.append({
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "View Poll History",
                    "emoji": True
                },
                "action_id": "back_to_history"
            }
        ]
    })
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