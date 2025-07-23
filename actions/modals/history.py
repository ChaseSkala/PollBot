def show_poll_history(manager):
    modal_blocks = []

    if not manager.history:
        modal_blocks.append({
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "There is currently no previous polls.",
                "emoji": True
            }
        })

    for i, poll in enumerate(manager.history):

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
                        "text": f"This was an open ended question, you can view the responses with the button below.",
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
                            "text": "View Full Poll",
                            "emoji": True
                        },
                        "value": f"{poll.poll_id}",
                        "action_id": f"poll_button-{i}"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Recreate Poll",
                            "emoji": True
                        },
                        "value": f"{poll.poll_id}",
                        "action_id": f"previous-poll-{i}"
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
                "type": "context",
                "elements": [
                    {
                        "type": "plain_text",
                        "text": f"The winner was: {poll.winner}",
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
                            "text": "View Full Poll",
                            "emoji": True
                        },
                        "value": f"{poll.poll_id}",
                        "action_id": f"poll_button-{i}"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Recreate Poll",
                            "emoji": True
                        },
                        "value": f"{poll.poll_id}",
                        "action_id": f"previous-poll-{i}"
                    }
                ]
            })
            modal_blocks.append({"type": "divider"})
    return {
        "type": "modal",
        "title": {
            "type": "plain_text",
            "text": "Poll History",
            "emoji": True
        },
        "close": {
            "type": "plain_text",
            "text": "Cancel",
            "emoji": True
        },
        "blocks": modal_blocks
    }
