import datetime

def is_anonymous(parts, user_name):
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
    poll_id = str(hash(timestamp))
    return poll_id

def convert_unix_to_date(timestamp):
    return datetime.datetime.fromtimestamp(timestamp)

def change_response(response_num, new_response, poll):
    if new_response == 'REMOVE':
        del poll.options[response_num]
    else:
        poll.options[response_num].text = new_response
    return "error"

def can_add_more_options(poll, user_id):
    if user_id not in poll.user_option_count:
        poll.user_option_count[user_id] = 1
        return True
    if poll.user_option_count[user_id] >= int(poll.max_option_count) + 1:
        return False
    else:
        return True

def letter_match_score(search: str, question: str) -> int:
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
        return polls  # Default: no sorting