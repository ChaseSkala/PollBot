def create_home_menu():
    blocks = {
	"type": "modal",
    "callback_id": "home-menu",
	"title": {
		"type": "plain_text",
		"text": "Create a poll",
		"emoji": True
	},
	"close": {
		"type": "plain_text",
		"text": "Cancel",
		"emoji": True
	},
	"blocks": [
		{
			"type": "actions",
			"elements": [
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "Multiple Choice",
						"emoji": True
					},
					"value": "multiple-choice",
					"action_id": "multiple-choice"
				},
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "Open Ended",
						"emoji": True
					},
					"value": "open-ended",
					"action_id": "open-ended"
				},
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Create from previous poll",
                        "emoji": True
                    },
                    "value": "create-from-previous-poll",
                    "action_id": "create-from-previous-poll"
                }
			]
		}
	]
}
    return blocks

def create_multiple_choice():
    blocks = {
        "type": "modal",
        "callback_id": "multiple-choice",
        "title": {
            "type": "plain_text",
            "text": "Rodger",
            "emoji": True
        },
        "submit": {
            "type": "plain_text",
            "text": "Submit",
            "emoji": True
        },
        "close": {
            "type": "plain_text",
            "text": "Cancel",
            "emoji": True
        },
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "Create A Poll",
                    "emoji": True
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "question_input"
                },
                "label": {
                    "type": "plain_text",
                    "text": "Create question",
                    "emoji": True
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "multiline": True,
                    "action_id": "choices_input"
                },
                "label": {
                    "type": "plain_text",
                    "text": "Create options (Separate with new lines)",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Settings*"
                },
                "accessory": {
                    "type": "checkboxes",
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Anonymous",
                                "emoji": True
                            },
                            "value": "anonymous"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Can users add new choices?",
                                "emoji": True
                            },
                            "value": "can-users-add-new-choices"
                        }
                    ],
                    "action_id": "checkboxes-action"
                }
            }
        ]
    }
    return blocks

def create_open_ended():
    blocks = {
	"type": "modal",
	"callback_id": "open-ended",
	"title": {
		"type": "plain_text",
		"text": "Create a poll",
		"emoji": True
	},
	"submit": {
		"type": "plain_text",
		"text": "Submit",
		"emoji": True
	},
	"close": {
		"type": "plain_text",
		"text": "Cancel",
		"emoji": True
	},
	"blocks": [
		{
			"type": "divider"
		},
		{
			"type": "input",
			"element": {
				"type": "plain_text_input",
				"action_id": "question_input"
			},
			"label": {
				"type": "plain_text",
				"text": "Create question",
				"emoji": True
			}
		},
		{
			"type": "divider"
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*Settings*"
			},
			"accessory": {
				"type": "checkboxes",
				"options": [
					{
						"text": {
							"type": "plain_text",
							"text": "Anonymous",
							"emoji": True
						},
						"value": "anonymous"
					}
				],
				"action_id": "checkboxes-action"
			},
        },
        {
            "type": "input",
            "element": {
                "type": "plain_text_input",
                "action_id": "max-options"
            },
            "label": {
                "type": "plain_text",
                "text": "Max amount of options per person. (Put 999 for no limit.)",
                "emoji": True
            }
		}
	]
}
    return blocks