# BotMQ

This project is a Telegram bot that integrates with an MQTT-to-HTTP converter to manage and monitor topics. Users can add topics via a password, set limits on topic values, and receive notifications when limits are exceeded.

## Components

The project is structured into two main services: **BotMQ** and **Converter**.

### 1. **BotMQ**

The **BotMQ** service is the core of the Telegram bot functionality.

#### Commands:

- `/start` - Send a start message.
- `/password` - Enter the password for a topic to gain access to it.
- `/report` - Send a report about all topics and their values.
- `/check` - Choose a topic to display its value.
- `/list_limits` - List all user limits.
- `/limit` - Choose a topic, limit type, and value to get notifications when it is exceeded.
- `/list_renames` - List all user renames.
- `/rename` - Choose a topic and a new name to display it as desired.

### 2. **Converter**

The **Converter** service is responsible for interfacing with the MQTT broker and making topic data available to BotMQ.

#### HTTP Interface

Provides an HTTP server with endpoints to list topics and fetch individual topic values. This interface is used by BotMQ to get real-time data.

- **Endpoints**:
    1. **`/list_topics`**
        - **Method:** GET
        - **Description:** This endpoint returns a comma-separated list of all available topics from the MQTT broker.
        - **Response:** A plain text response containing the list of topics.
        - **Example Response:** `topic1,topic2,topic3`
    2. **`/get_value`**
        - **Method:** GET
        - **Parameters:** `topic` (query parameter) - The specific topic for which the value is requested.
        - **Description:** This endpoint returns the current value of the specified topic.
        - **Response:** A plain text response containing the value of the topic or an error message if the topic is not found.
        - **Example Response:** `123.45` for a valid topic, or `Topic "invalid_topic" not found` for an invalid topic.

## Dependencies

**[Docker](https://hub.docker.com/_/docker)** and **[Docker Compose](https://github.com/docker/compose)** for containerizing and managing multi-container applications.

## Build and Run

### Environment Variables

- **BOT_TOKEN:** Telegram bot token.
- **ADMIN_IDS:** Admin user IDs.
- **SERVER_ADDRESS:** Server providing MQTT data.
- **SERVER_PORT:** Port of the server.
- **SERVER_TIMEOUT:** Polling interval.
- **MQTT_ADDRESS:** MQTT broker address.
- **MQTT_PORT:** MQTT broker port.
- **MQTT_USERNAME:** MQTT username (optional).
- **MQTT_PASSWORD:** MQTT password (optional).
- **MQTT_TOPICS:** MQTT topics to read.

### Build and Run

1. **Configure the project:**
    - Edit the environment variables mentioned above in the `Makefile`.

2. **Build Services:**
    - Run the following command to build the Docker services:
        ```
        make build
        ```

3. **Start Containers:**
    - Run the following command to start the containers in detached mode:
        ```
        make up
        ```

4. **Manage Containers:**
    - Run the following command to check other commands:
        ```
        make help
        ```

## TODO

- [ ] Support media content via MQTT
- [ ] Keep topic values in a database to display statistics
- [ ] More databases
    - [ ] Redis
    - [ ] MySQL
- [ ] Better password distribution
- [ ] Manage topics via chat
    - [ ] Add topic
    - [ ] Delete topic
    - [ ] Edit topic

## Links

- [Aiogram](https://github.com/aiogram/aiogram)
- [PostgreSQL container](https://hub.docker.com/_/postgres)
- [paho.mqtt.python](https://github.com/eclipse/paho.mqtt.python)