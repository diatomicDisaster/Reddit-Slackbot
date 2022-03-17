import json
from pathlib import Path
from typing import(
    Union
)

from reddack.exceptions import ConfigError
from reddack.core import (
    Channels,
    ReddackSubmission,
    Rule,
    PrawAuth,
    SlackAuth,
    Reddack
)


def reddack_from_json(configpath):
    with configpath.open() as f:
        masterconfig = json.load(f)
    try:
        configs = masterconfig['configs']
    except AttributeError as error:
        raise ConfigError(
            f"{error.obj!r} object is missing field {error.name!r}.",
            afterword = "Individual configurations must appear in a global 'configs' attribute."
        )
    else:
        reddacks = []
        for name, config in configs.items():
            # Create auth objects using credentials
            praw_auth = PrawAuth(
                config['praw']['auth']['client']['id'],
                config['praw']['auth']['client']['secret'],
                config['praw']['auth']['user']['name'],
                config['praw']['auth']['user']['password']
            )
            slack_auth = SlackAuth(
                config['slack']['auth']['bot_token'],
                config['slack']['auth']['user_token']
            )
            # Create channel objects for each moderation item type
            channels = {
                ReddackSubmission : Channels(
                  queue = config['slack']['channels']['submissions']['queue'],
                  archive = config['slack']['channels']['submissions']['archive']
                )
            }
            # Create rule objects and store in dictionary
            rules = {}
            for rule in config['moderation']['rules']:
                rules[rule['name']] = Rule(
                    title = rule['title'], 
                    text = rule['text'], 
                    link = rule['link'],
                    applyto = rule['applyto']
                )
            # Must have at least one type of object to moderate
            if any(c in channels for c in [ReddackSubmission]):
                pass
            else:
               raise ConfigError(
                   "Moderation requires modqueue and archive channels to be " 
                   "defined for either comments or submissions."
               )
            # Determine if non-default paths are present
            paths = {'known_items': None, 'post_dir': None}
            if ('paths' in config) and ('known_items' in config['paths']):
                paths['known_items'] = Path(config['paths']['known_items'])
            if ('paths' in config) and ('post_directory' in config['paths']):
                paths['post_dir'] = Path(config['paths']['post_directory'])
            
            reddacks.append(
                Reddack(
                    config['praw']['subreddit'],
                    praw_auth,
                    slack_auth,
                    channels,
                    rules,
                    removal_template=config['moderation']['removal_message'],
                    known_items_path=paths['known_items'],
                    post_requests_path=paths['post_dir']
                )
            )
        return reddacks

def reddack(config_path: Union[str, Path]) -> Reddack:
    if config_path is str:
        config_path = Path(config_path)
    if config_path.suffix == '.json':
        return reddack_from_json(config_path)
    elif config_path.suffix == '.conf':
        raise ConfigError("'.conf' file type not yet supported.")
    else:
        raise ConfigError("Configuration filetype not recognised.")