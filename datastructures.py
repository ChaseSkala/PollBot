from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime


@dataclass
class PollOption:
    text: str
    votes: int = 0
    voters: List[str] = None

    def __post_init__(self):
        if self.voters is None:
            self.voters = []

    def add_vote(self, user_id: str) -> bool:
        if user_id not in self.voters:
            self.voters.append(user_id)
            self.votes += 1
            return True
        return False

    def remove_vote(self, user_id: str) -> bool:
        if user_id in self.voters:
            self.voters.remove(user_id)
            self.votes -= 1
            return True
        return False


class Poll:
    def __init__(self, poll_id: str, question: str, options: List[str],
                 creator: str, channel_id: str, anonymous: bool = False):
        self.poll_id = poll_id
        self.question = question
        self.creator = creator
        self.channel_id = channel_id
        self.anonymous = anonymous
        self.created_at = datetime.now()

        self.options = [PollOption(text=opt) for opt in options]

    @property
    def total_votes(self) -> int:
        return sum(option.votes for option in self.options)

    @property
    def percentages(self) -> List[float]:
        total = self.total_votes
        if total == 0:
            return [0.0] * len(self.options)
        return [(option.votes / total) * 100 for option in self.options]

    @property
    def results_summary(self) -> Dict:
        return {
            'poll_id': self.poll_id,
            'question': self.question,
            'total_votes': self.total_votes,
            'options': [
                {
                    'text': opt.text,
                    'votes': opt.votes,
                    'percentage': pct,
                    'voters': opt.voters if not self.anonymous else []
                }
                for opt, pct in zip(self.options, self.percentages)
            ]
        }

    @property
    def is_active(self) -> bool:
        return self.total_votes > 0

    @property
    def formatted_results(self) -> str:
        lines = []
        emojis = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
        truncated_options = []
        for option in self.options:
            if len(option.text) > 25:
                truncated_options.append(option.text[:22] + "...")
            else:
                truncated_options.append(option.text)
        max_option_length = max(len(opt) for opt in truncated_options)
        for i, option in enumerate(self.options):
            emoji = emojis[i] if i < len(emojis) else "🔸"
            votes = option.votes
            percentage = self.percentages[i]
            filled = round(percentage / 10)
            empty = 10 - filled
            bar = "⬜" * filled + "⬛" * empty
            if len(option.text) > 25:
                truncated_option = option.text[:22] + "..."
            else:
                truncated_option = option.text
            votes_word = "vote" if votes == 1 else "votes"
            lines.append(
                f"{emoji} {truncated_option:<{max_option_length}} {bar} ({percentage:.0f}%, {votes} {votes_word})"
            )
        poll_lines = "\n".join(lines)
        return (
            f"*{self.question}* (created by {self.creator})\n"
            f"*Poll ID:* {self.poll_id}\n"
            f"```\n{poll_lines}\n```\n"
            f"Vote by reacting below!"
        )
    def add_vote(self, option_index: int, user_id: str) -> bool:
        if 0 <= option_index < len(self.options):
            return self.options[option_index].add_vote(user_id)
        return False

    def remove_vote(self, option_index: int, user_id: str) -> bool:
        if 0 <= option_index < len(self.options):
            return self.options[option_index].remove_vote(user_id)
        return False

    def get_user_vote(self, user_id: str) -> Optional[int]:
        for i, option in enumerate(self.options):
            if user_id in option.voters:
                return i
        return None


class PollManager:
    def __init__(self):
        self.polls: Dict[str, Poll] = {}

    @property
    def active_polls(self) -> List[Poll]:
        return [poll for poll in self.polls.values() if poll.is_active]

    @property
    def total_polls(self) -> int:
        return len(self.polls)

    def create_poll(self, poll_id: float or int, question: str, options: List[str],
                    creator: str, channel_id: str, anonymous: bool = False) -> Poll:
        poll = Poll(poll_id, question, options, creator, channel_id, anonymous)
        self.polls[poll_id] = poll
        return poll

    def get_poll(self, poll_id: str) -> Optional[Poll]:
        return self.polls.get(poll_id)