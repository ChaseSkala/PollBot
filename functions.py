def isAnonymous(parts, user_name):
    if parts[0] == "Anonymous":
        anonEnabled = True
    else:
        anonEnabled = False
    if anonEnabled:
        user_name = "Anonymous"
        question = parts[1]
        options = parts[2:]
    else:
        user_name = user_name
        anonEnabled = False
        question = parts[0]
        options = parts[1:]
    return question, options, anonEnabled, user_name