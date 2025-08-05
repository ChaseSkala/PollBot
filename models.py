from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, relationship

db_url = "mysql+pymysql://admin:bZl4BhmBhQtaz6PHDkRq@rodgerdata.chy2cwwqqm77.us-east-2.rds.amazonaws.com:3306/pollbot"
engine = create_engine(db_url)
Base = declarative_base()


class PollOption(Base):
    """
    Represents an option within a poll.

    Each PollOption is linked to a Poll and tracks votes, voters, and
    user responses.

    :ivar id: Unique identifier for the poll option.
    :vartype id: int
    :ivar text: The text of the poll option.
    :vartype text: str
    :ivar votes: The number of votes this option has received.
    :vartype votes: int
    :ivar voters: A dictionary mapping user IDs to usernames of voters.
    :vartype voters: dict
    :ivar response_user_ids: A dictionary mapping response numbers to user IDs.
    :vartype response_user_ids: dict
    :ivar poll_id: The ID of the poll this option belongs to.
    :vartype poll_id: str
    :ivar poll: The Poll object this option is related to.
    :vartype poll: Poll
    """

    __tablename__ = "poll_options"

    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(String(255), nullable=False)
    votes = Column(Integer, default=0)
    voters = Column(JSON, default=dict)
    response_user_ids = Column(JSON, default=dict)
    poll_id = Column(String(255), ForeignKey("polls.poll_id"))

    poll = relationship("Poll", back_populates="options")

    def add_vote(self, user_id: str, username: str) -> bool:
        """
        Adds a vote for this option by a user.

        :param user_id: The unique ID of the user voting.
        :type user_id: str
        :param username: The username of the voter.
        :type username: str
        :returns: True if the vote was added, False if the user already voted.
        :rtype: bool
        """
        if user_id not in self.voters:
            self.voters[user_id] = username
            self.votes += 1
            return True
        return False

    def remove_vote(self, user_id: str) -> bool:
        """
        Removes a user's vote from this option.

        :param user_id: The unique ID of the user whose vote is to be removed.
        :type user_id: str
        :returns: True if the vote was removed, False if the user had not voted.
        :rtype: bool
        """
        if user_id in self.voters:
            del self.voters[user_id]
            self.votes -= 1
            return True
        return False

    def add_user(self, user_id: int, response_num: int) -> None:
        """
        Associates a user with a specific response number.

        :param user_id: The user's unique ID.
        :type user_id: int
        :param response_num: The response number to associate with the user.
        :type response_num: int
        :returns: None
        """
        if user_id not in self.response_user_ids.values():
            self.response_user_ids[response_num] = user_id

    def check_user(self, user_id: int, response_num: int) -> bool:
        """
        Checks if a user is associated with a specific response number.

        :param user_id: The user's unique ID.
        :type user_id: int
        :param response_num: The response number to check.
        :type response_num: int
        :returns: True if the user is associated, False otherwise.
        :rtype: bool
        """
        return self.response_user_ids.get(response_num) == user_id


class Poll(Base):
    """
    Represents a poll with multiple options.

    Tracks poll metadata, options, and provides properties for
    determining the winner, total votes, and vote percentages.

    :ivar poll_id: Unique identifier for the poll.
    :vartype poll_id: str
    :ivar question: The poll question.
    :vartype question: str
    :ivar creator: The username or ID of the poll creator.
    :vartype creator: str
    :ivar channel_id: The channel where the poll was created.
    :vartype channel_id: str
    :ivar creation_date: The date the poll was created.
    :vartype creation_date: str
    :ivar max_option_count: The maximum number of options allowed.
    :vartype max_option_count: int
    :ivar anonymous: Whether the poll is anonymous.
    :vartype anonymous: bool
    :ivar can_add_choices: Whether users can add choices.
    :vartype can_add_choices: bool
    :ivar is_template: Whether this poll is a template.
    :vartype is_template: bool
    :ivar user_option_count: A dictionary tracking user option counts.
    :vartype user_option_count: dict
    :ivar closed: Whether the poll is closed.
    :vartype closed: bool
    :ivar options: List of PollOption objects for this poll.
    :vartype options: list[PollOption]
    """

    __tablename__ = "polls"

    poll_id = Column(String(255), primary_key=True)
    question = Column(String(255), nullable=False)
    creator = Column(String(255), nullable=False)
    channel_id = Column(String(255), nullable=False)
    creation_date = Column(String(255), nullable=False)
    max_option_count = Column(Integer, nullable=False)
    anonymous = Column(Boolean, default=False)
    can_add_choices = Column(Boolean, default=False)
    is_template = Column(Boolean, default=False)
    user_option_count = Column(JSON, default=dict)
    closed = Column(Boolean, default=False)

    options = relationship("PollOption", back_populates="poll", cascade="all, delete-orphan")

    @property
    def winner(self):
        """
        Returns the winning option(s) for the poll.

        :returns: The text of the winning option, a list of texts if tied, or "Nobody voted" if no votes.
        :rtype: str or list[str]
        """
        if not self.options:
            return None
        max_votes = max(opt.votes for opt in self.options)
        if max_votes == 0:
            return "Nobody voted"
        winners = [opt.text for opt in self.options if opt.votes == max_votes]
        return winners[0] if len(winners) == 1 else winners

    @property
    def total_votes(self) -> int:
        """
        Returns the total number of votes across all options.

        :returns: The total vote count.
        :rtype: int
        """
        return sum(option.votes for option in self.options)

    @property
    def percentages(self) -> list[float]:
        """
        Returns the percentage of votes for each option.

        :returns: A list of percentages corresponding to each option.
        :rtype: list[float]
        """
        total = self.total_votes
        if total == 0:
            return [0.0] * len(self.options)
        return [(option.votes / total) * 100 for option in self.options]

    @property
    def is_active(self) -> bool:
        """
        Indicates whether the poll has received any votes.

        :returns: True if there are votes, False otherwise.
        :rtype: bool
        """
        return self.total_votes > 0


class Rating(Base):
    """
    Represents a user rating for a poll option.

    :ivar id: Unique identifier for the rating.
    :vartype id: int
    :ivar user_id: The ID of the user who rated.
    :vartype user_id: str
    :ivar option_text: The text of the option being rated.
    :vartype option_text: str
    :ivar rating: The rating value.
    :vartype rating: int
    """

    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=False)
    option_text = Column(String(255), nullable=False)
    rating = Column(Integer, nullable=False)

Base.metadata.create_all(engine)