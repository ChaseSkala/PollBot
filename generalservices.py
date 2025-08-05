import datetime


def is_anonymous(parts, user_name):
    """
    Checks if the user has selected anonymous or not.

    :param parts: The parts of the question.
    :type parts: list
    :param user_name: The name of the user.
    :type user_name: str
    :returns: Different data depending on  if the user has selected anonymous.
    :rtype: str, bool
    """
    if parts[0] == "Anonymous":
        anon_enabled = True
    else:
        anon_enabled = False
    if anon_enabled:
        user_name = "Anonymous"
        question = parts[1]
        options = parts[2:]
    else:
        user_name = user_name
        anon_enabled = False
        question = parts[0]
        options = parts[1:]
    return question, options, anon_enabled, user_name


def create_id(timestamp):
    """
    Creates a poll id given a timestamp.

    :param timestamp: The timestamp for the poll id.
    :type timestamp: str or float
    :returns: The poll id.
    :rtype: str
    """
    poll_id = str(hash(timestamp))
    return poll_id


def convert_unix_to_date(timestamp):
    """
    Converts a unix timestamp to a date.

    :param timestamp: The unix timestamp.
    :type timestamp: float
    :returns: The date of the poll.
    :rtype: str
    """
    return datetime.datetime.fromtimestamp(timestamp)


def change_response(response_num, new_response, poll):
    """
    Changes a response within a poll

    :param response_num: Which response to change.
    :type response_num: int
    :param new_response: What they want to change the response to.
    :type new_response: str
    :param poll: The poll that contains the response.
    :type poll: Poll
    :returns: A changed response.
    :rtype: str
    """
    if new_response == 'REMOVE':
        option_to_remove = poll.options[response_num]
        poll.options.remove(option_to_remove)
    else:
        poll.options[response_num].text = new_response
    return "error"


def can_add_more_options(poll, user_id):
    """
    Checks if the user can add more options.

    :param poll: The poll.
    :type poll: Poll
    :param user_id: The user who is being checked.
    :type user_id: str
    :returns: Whether the user can add more options.
    :rtype: bool
    """
    current_count = poll.user_option_count.get(user_id, 0)
    return current_count < int(poll.max_option_count)


def letter_match_score(search: str, question: str) -> int:
    """
    Matches the question against the search string.

    :param search: What the user is searching up.
    :type search: str
    :param question: The question to match to the search.
    :type question: str
    :return: The letter match score.
    :rtype: int
    """
    search = search.lower()
    question = question.lower()
    score = 0
    q_idx = 0
    for s in search:
        found = False
        while q_idx < len(question):
            if question[q_idx] == s:
                score += 1
                q_idx += 1
                found = True
                break
            q_idx += 1
        if not found:
            break
    return score


def sort_polls(polls, sort_by):
    """
    Sorts through the polls inside the database.

    :param polls: The different polls in the database.
    :type polls: multiple Polls
    :param sort_by: What the user wants to sort the polls by.
    :type sort_by: str
    :returns: A sorted version of Polls.
    :rtype: multiple Polls
    """
    if sort_by == "newest":
        return sorted(polls, key=lambda p: p.creation_date, reverse=True)
    elif sort_by == "oldest":
        return sorted(polls, key=lambda p: p.creation_date)
    elif sort_by == "poll_id":
        return sorted(polls, key=lambda p: p.poll_id)
    elif sort_by == "votes":
        return sorted(polls, key=lambda p: p.total_votes, reverse=True)
    elif sort_by == "alphabetical":
        return sorted(polls, key=lambda p: p.question.lower())
    else:
        return polls
