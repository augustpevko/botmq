import logging
from typing import Dict, List, Optional
import paho.mqtt.client as mqtt

class Mqtt:
    def __init__(self, address: str, port: int, username: str, password: str, topic: List[str]):
        """
        Initialize MQTT client.

        Args:
            address (str): MQTT broker address.
            port (int): MQTT broker port.
            username (str): Username for authentication.
            password (str): Password for authentication.
            topic (List[str]): List of topics to subscribe to.
        """
        self.address: str = address
        self.port: int = port
        self.username: str = username
        self.password: str = password
        self.topic: List[str] = topic
        self.data_dict: Dict[str, str] = {}
        self.client: mqtt.Client = mqtt.Client()

    def on_message(self, client: mqtt.Client, userdata: str, msg: mqtt.MQTTMessage) -> None:
        """
        Callback function for message reception.

        Args:
            client (mqtt.Client): MQTT client instance.
            userdata (str): User data.
            msg (mqtt.MQTTMessage): Received message.
        """
        self.data_dict[msg.topic] = msg.payload.decode('utf-8')
        logging.info(self.data_dict)

    def on_connect(self, client: mqtt.Client, userdata: str, flags: dict, rc: int) -> None:
        """
        Callback function for connection establishment.

        Args:
            client (mqtt.Client): MQTT client instance.
            userdata (str): User data.
            flags (dict): Flags indicating session state.
            rc (int): Result code from connection attempt.
        """
        logging.info(f'Connected with result code {rc}')
        self.client.subscribe([(topic, 0) for topic in self.topic])

    def username_pw_set(self) -> None:
        """Set username and password for MQTT client."""
        self.client.username_pw_set(self.username, self.password)

    def connect(self) -> None:
        """Connect to MQTT broker."""
        self.client.on_message = self.on_message
        self.client.on_connect = self.on_connect
        self.username_pw_set()
        self.client.connect(self.address, self.port, 60)

    def start_loop(self) -> None:
        """Start MQTT client loop."""
        self.client.loop_start()

    def run(self) -> None:
        """Connect to broker and start client loop."""
        self.connect()
        self.start_loop()

    def get_value(self, topic: str) -> Optional[str]:
        """
        Get the latest value for a given topic.

        Args:
            topic (str): Topic for which to retrieve the value.

        Returns:
            Optional[str]: Latest value for the specified topic, or None if topic not found.
        """
        return self.data_dict.get(topic, None)

    def list_topics(self) -> List[str]:
        """
        Get the list of subscribed topics.

        Returns:
            List[str]: List of subscribed topics.
        """
        return list(self.data_dict.keys())
