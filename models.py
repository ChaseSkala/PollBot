from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class PollOption:
    text: str
    votes: int = 0
    voters: dict[str, str] = field(default_factory=dict)

    def add_vote(self, user_id: str, username: str) -> bool:
        if user_id not in self.voters:
            self.voters[user_id] = username
            self.votes += 1
            return True
        return False

    def remove_vote(self, user_id: str, username: str) -> bool:
        if user_id in self.voters:
            del self.voters[user_id]
            self.votes -= 1
            return True
        return False


class Poll:
    def __init__(self, poll_id: str, question: str, options: list[str],
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
    def percentages(self) -> list[float]:
        total = self.total_votes
        if total == 0:
            return [0.0] * len(self.options)
        return [(option.votes / total) * 100 for option in self.options]

    @property
    def results_summary(self) -> dict:
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

    def add_vote(self, option_index: int, user_id: str, username: str) -> bool:
        if 0 <= option_index < len(self.options):
            return self.options[option_index].add_vote(user_id, username)
        return False

    def remove_vote(self, option_index: int, user_id: str, username: str) -> bool:
        if 0 <= option_index < len(self.options):
            return self.options[option_index].remove_vote(user_id, username)
        return False

    def get_user_vote(self, user_id: str) -> Optional[int]:
        for i, option in enumerate(self.options):
            if user_id in option.voters:
                return i
        return None


class PollManager:
    def __init__(self):
        self.polls: dict[str, Poll] = {}

    @property
    def active_polls(self) -> list[Poll]:
        return [poll for poll in self.polls.values() if poll.is_active]

    @property
    def total_polls(self) -> int:
        return len(self.polls)

    def create_poll(self, poll_id: float or int, question: str, options: list[str],
                    creator: str, channel_id: str, anonymous: bool = False) -> Poll:
        poll = Poll(poll_id, question, options, creator, channel_id, anonymous)
        self.polls[poll_id] = poll
        return poll

    def get_poll(self, poll_id: str) -> Optional[Poll]:
        return self.polls.get(poll_id)