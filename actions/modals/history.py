from generalservices import sort_polls

from models import Poll, PollOption

def show_poll_history(session, sort_by="newest"):
    modal_blocks = []

    polls = session.query(Poll).filter_by(is_template=False).all()

    if not polls:
        modal_blocks.append({
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": ":open_file_folder: There is currently no previous polls.",
                "emoji": True
            }
        })

    modal_blocks.append({
        "type": "actions",
        "block_id": "search_block",
        "elements": [
            {
                "type": "external_select",
                "action_id": "search_action",
                "placeholder": {"type": "plain_text", "text": ":mag_right: Type to search..."}
            },
            {
                "type": "static_select",
                "action_id": "sort_action",
                "placeholder": {"type": "plain_text", "text": "Sort by..."},
                "options": [
                    {
                        "text": {"type": "plain_text", "text": "Newest"},
                        "value": "newest"
                    },
                    {
                        "text": {"type": "plain_text", "text": "Oldest"},
                        "value": "oldest"
                    },
                    {
                        "text": {"type": "plain_text", "text": "Poll ID"},
                        "value": "poll_id"
                    },
                    {
                        "text": {"type": "plain_text", "text": "Most Votes"},
                        "value": "votes"
                    },
                    {
                        "text": {"type": "plain_text", "text": "Alphabetical"},
                        "value": "alphabetical"
                    }
                ]
            }
        ]
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
            "text": "History",
            "emoji": True
        },
        "close": {
            "type": "plain_text",
            "text": "Cancel",
            "emoji": True
        },
        "blocks": modal_blocks
    }
