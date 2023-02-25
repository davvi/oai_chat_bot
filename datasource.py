import time
import logging

# Dictionary of all active users
# TODO move that dictionary to some kind of database with "in memory" caching
# user object example:
# {
#   't_id': 'telegram id'
#   'username': 'some_user_name',
#   'first_name': 'Name',
#   'last_name': 'Lastname',
#   'language_code': 'AM',
#   'oai_chat_context': 'list of all messages user send',
#   'last_messages_timestamp': '2346789',
#   'total_messages_send': '23',
#   'oai_token': 'openai token string'
# }
active_users = {}


def user_not_exists(t_id):
    return t_id not in active_users


def user_exists(t_id):
    return t_id in active_users


def get_user(t_id):
    return active_users[t_id]


def save_user(user):
    active_users[user.t_id] = user
    logging.debug("User $s updated: %s", user.t_id, active_users[user.t_id])


class User:

    def __init__(self, t_id, first_name, last_name=None, username=None, language_code=None, **kwargs):
        self.t_id: int = t_id
        self.first_name: str = first_name
        self.username: str = username
        self.last_name: str = last_name
        self.language_code: str = language_code
        self.model: str = "text-davinci-003"
        self.total_messages_send: int = 0
        self.last_messages_timestamp: int = 0
        self.oai_token: str = ""
        self.oai_chat_conversation_history: list = []

    def set_oai_token(self, oai_token):
        self.oai_token: str = oai_token

    def new_message(self, message):
        self.last_messages_timestamp = time.time()
        self.total_messages_send = self.total_messages_send + 1
        self.oai_chat_conversation_history.append(message)

    def clean_context(self):
        self.oai_chat_conversation_history = []

    def get_context(self):
        return "\n".join(self.oai_chat_conversation_history)

    def set_last_messages_timestamp(self, last_messages_timestamp):
        self.last_messages_timestamp: int = last_messages_timestamp
