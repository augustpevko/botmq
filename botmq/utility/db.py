from botmq.loader import data_base
from typing import Any, Dict, Optional

def set_limit(user_id: int, topic: str, limit: str, value: Any) -> None:
    user_config = data_base.get_config(user_id)
    if user_config is None:
        user_config = {}
    if 'limits' not in user_config:
        user_config['limits'] = {}
    limits_config = user_config['limits']
    if topic not in limits_config:
        limits_config[topic] = {}
    limits_config[topic][limit] = value
    user_config['limits'] = limits_config
    data_base.set_config(user_id, user_config)

def get_limit(user_id: int, topic: str, limit: str) -> Optional[Any]:
    user_config = data_base.get_config(user_id)
    if user_config is None:
        return None
    if 'limits' not in user_config:
        return None
    limits_config = user_config['limits']
    if topic not in limits_config:
        return None
    return limits_config[topic][limit]

def list_limits(user_id: int) -> Optional[Dict[str, Any]]:
    user_config = data_base.get_config(user_id)
    if user_config is None:
        return None
    if 'limits' not in user_config:
        return None
    return user_config['limits']

def set_rename(user_id: int, topic: str, new_name: str) -> None:
    user_config = data_base.get_config(user_id)
    if user_config is None:
        user_config = {}
    if 'renames' not in user_config:
        user_config['renames'] = {}
    renames_config = user_config['renames']
    renames_config[topic] = new_name
    user_config['renames'] = renames_config
    data_base.set_config(user_id, user_config)

def get_rename(user_id: int, topic: str) -> Optional[str]:
    user_config = data_base.get_config(user_id)
    if user_config is None:
        return None
    if 'renames' not in user_config:
        return None
    renames_config = user_config['renames']
    return renames_config.get(topic, None)

def list_renames(user_id: int) -> Optional[Dict[str, Any]]:
    user_config = data_base.get_config(user_id)
    if user_config is None:
        return None
    if 'renames' not in user_config:
        return None
    return user_config['renames']

def get_topic_name(user_id: int, topic: str) -> str:
    topic_name = get_rename(user_id, topic)
    if topic_name is None:
        return topic
    return topic_name
