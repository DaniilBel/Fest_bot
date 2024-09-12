from strings import stories


message_mapping = {}
user_points = {}
restricted_users = {}
message_reactions = {}
user_selected_task = {}

available_shortcut_tasks = [
    stories.get("task1_short"),
    stories.get("task2_short"),
    stories.get("task3_short"),
]

available_text_tasks = [
    stories.get("task1_short"),
    stories.get("task3_short"),
]

available_media_tasks = [
    stories.get("task2_short")
]
