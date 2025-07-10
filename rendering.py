from typing import Optional


def render_results(poll, viewing_results: Optional[bool] = False, editing_reactions: Optional[bool] = False or str) -> str:
    lines = []
    emojis = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
    truncated_options = []
    for option in poll.options:
        if len(option.text) > 25:
            truncated_options.append(option.text[:22] + "...")
        else:
            truncated_options.append(option.text)
    max_option_length = max(len(opt) for opt in truncated_options)
    for i, option in enumerate(poll.options):
        emoji = emojis[i] if i < len(emojis) else "🔸"
        votes = option.votes
        percentage = poll.percentages[i]
        filled = round(percentage / 10)
        empty = 10 - filled
        bar = "⬜" * filled + "⬛" * empty
        voter_names = ", ".join(option.voters.values())
        if len(option.text) > 25:
            truncated_option = option.text[:22] + "..."
        else:
            truncated_option = option.text
        votes_word = "vote" if votes == 1 else "votes"
        lines.append(
            f"{emoji} {truncated_option:<{max_option_length}} {bar} ({percentage:.0f}%, {votes} {votes_word}, {voter_names})"
        )
    poll_lines = "\n".join(lines)
    if viewing_results:
        reaction = ""
        interactable = "*YOU ARE VIEWING A PAST POLL.*"
    else:
        reaction = "Vote by reacting below!"
        interactable = ""
    return (
        f"{interactable}\n\n"
        f"*{poll.question}* (created by {poll.creator})\n"
        f"*Poll ID:* {poll.poll_id}\n"
        f"```\n{poll_lines}\n```\n"
        f"{reaction}"
    )