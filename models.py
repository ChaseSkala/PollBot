from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, relationship

db_url = "sqlite:///C:/Users/chaseskala/Desktop/PollDatabase/pollDatabase.db"

engine = create_engine(db_url)

Base = declarative_base()


class PollOption(Base):
    __tablename__ = "poll_options"

    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(String, nullable=False)
    votes = Column(Integer, default=0)
    voters = Column(JSON, default=dict)
    response_user_ids = Column(JSON, default=dict)
    poll_id = Column(String, ForeignKey("polls.poll_id"))


    poll = relationship("Poll", back_populates="options")

    def add_vote(self, user_id: str, username: str) -> bool:
        if user_id not in self.voters:
            self.voters[user_id] = username
            self.votes += 1
            return True
        return False

    def remove_vote(self, user_id: str) -> bool:
        if user_id in self.voters:
            del self.voters[user_id]
            self.votes -= 1
            return True
        return False

    def add_user(self, user_id: int, response_num: int) -> None:
        if user_id not in self.response_user_ids.values():
            self.response_user_ids[response_num] = user_id

    def check_user(self, user_id: int, response_num: int) -> bool:
        return self.response_user_ids.get(response_num) == user_id

class Poll(Base):
    __tablename__ = "polls"

    poll_id = Column(String, primary_key=True)
    question = Column(String, nullable=False)
    creator = Column(String, nullable=False)
    channel_id = Column(String, nullable=False)
    creation_date = Column(String, nullable=False)
    max_option_count = Column(Integer, nullable=False)
    anonymous = Column(Boolean, default=False)
    can_add_choices = Column(Boolean, default=False)
    is_template = Column(Boolean, default=False)
    user_option_count = Column(JSON, default=dict)

    options = relationship("PollOption", back_populates="poll", cascade="all, delete-orphan")

    @property
    def winner(self):
        if not self.options:
            return None
        max_votes = max(opt.votes for opt in self.options)
        if max_votes == 0:
            return "Nobody voted"
        winners = [opt.text for opt in self.options if opt.votes == max_votes]
        return winners[0] if len(winners) == 1 else winners

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
    def is_active(self) -> bool:
        return self.total_votes > 0

Base.metadata.create_all(engine)