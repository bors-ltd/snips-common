import traceback

from . import configs


class ActionWrapper:
    """Common skeleton for actions"""
    # Class to load the configuration file
    config_parser = configs.SnipsConfigParser
    # Messages to send on the given errors
    reactions = {}

    def __init__(self, hermes, intent_message, config):
        self.hermes = hermes
        self.intent_message = intent_message
        self.config = config

    @classmethod
    def callback(cls, hermes, intent_message):
        print(
            "Starting action",
            cls.__name__,
            "for intent",
            intent_message.intent.intent_name,
            "for site",
            intent_message.site_id
        )
        config = cls.config_parser.read_configuration_file()

        if not cls.message_for_this_site(config, intent_message):
            return

        action_wrapper = cls(hermes, intent_message, config)
        try:
            action_wrapper.action()
        except Exception as exc:
            traceback.print_exc()
            action_wrapper.react_to_exception(exc)
        else:
            print("Action finished without error")

    @staticmethod
    def message_for_this_site(config, intent_message):
        site_id = config.get('secret', {}).get('site_id')
        if site_id:
            deliver_to = intent_message.site_id
            if deliver_to != site_id:
                print("This message is for", deliver_to, ", ignoring.")
                return False
        # We are the recipient or the app is not designed for multiroom
        return True

    def action(self):
        raise NotImplementedError

    def react_to_exception(self, exc):
        reaction = self.reactions.get(
            exc.__class__, "Désolée, il y a eu une erreur."
        )
        reaction = reaction.format(exc)
        self.end_session(reaction)

    def end_session(self, message, *args):
        current_session_id = self.intent_message.session_id
        message = message + " " + " ".join(str(arg) for arg in args)
        print('Ending session with message "%s"' % message)
        self.hermes.publish_end_session(current_session_id, message)
