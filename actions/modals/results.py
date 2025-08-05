def all_results(poll, channel_id):
    """
    Renders the results of all options in a multiple-choice poll.

    :param poll: The poll to be rendered.
    :type poll: Poll
    :param channel_id: The channel id where the command has taken place.
    :type channel_id: str
    :returns: A modal
    """
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
                    "text": "View History",
                    "emoji": True
                },
                "action_id": "back_to_history"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Recreate Poll",
                    "emoji": True
                },
                "value": f"{poll.poll_id}",
                "action_id": f"previous-poll-998"
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
                    "text": "Close Poll",
                    "emoji": True
                },
                "action_id": "close-poll",
                "value": f"{poll.poll_id}"
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
    """
    Renders the results of all options in an open-ended poll.
    :param poll: The poll to be rendered.
    :type poll: Poll
    :param channel_id: The channel id where the command has taken place.
    :type channel_id: str
    :returns: A modal.
    """
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
                    "text": "View History",
                    "emoji": True
                },
                "action_id": "back_to_history"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Recreate Poll",
                    "emoji": True
                },
                "value": f"{poll.poll_id}",
                "action_id": f"previous-poll-999"
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
                    "text": "Close Poll",
                    "emoji": True
                },
                "action_id": "close-poll",
                "value": f"{poll.poll_id}"
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


def render_poll_option_rating(poll):
    """
    Renders the ratings of options in a past poll.

    :param poll: The poll to be rendered.
    :type poll: Poll
    :returns: A modal.
    """
    modal_blocks = [
        {
			"type": "header",
			"text": {
				"type": "plain_text",
				"text": f"Rating options from poll: {poll.question}",
				"emoji": True
			}
		},
		{
			"type": "divider"
		}
    ]

    for i, option in enumerate(poll.options):
        if option.text == 'Add your responses!':
            continue
        modal_blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{option.text}"
                }
            }
        )
        modal_blocks.append({
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "1",
                        "emoji": True
                    },
                    "action_id": "option_rated1",
                    "value": f"{option.text}"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "2",
                        "emoji": True
                    },
                    "action_id": "option_rated2",
                    "value": f"{option.text}"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "3",
                        "emoji": True
                    },
                    "action_id": "option_rated3",
                    "value": f"{option.text}"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "4",
                        "emoji": True
                    },
                    "action_id": "option_rated4",
                    "value": f"{option.text}"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "5",
                        "emoji": True
                    },
                    "action_id": "option_rated5",
                    "value": f"{option.text}"
                },
            ]
        })
        modal_blocks.append({"type": "divider"})
    return {
        "type": "modal",
        "title": {
            "type": "plain_text",
            "text": "Option Rating",
            "emoji": True
        },
        "close": {
            "type": "plain_text",
            "text": "Cancel",
            "emoji": True
        },
        "blocks": modal_blocks
    }