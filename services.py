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