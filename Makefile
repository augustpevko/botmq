#Your telegram bot token
export BOT_TOKEN := 1234567890:abcdefghijklmnopqrstuvwxyzABCDEFGHI
#Your ID
export ADMIN_IDS := 123456789
#Address of server that provides mqtt data(should be converter if you use docker one)
export SERVER_ADDRESS := converter
#Port of server that provides mqtt data
export SERVER_PORT := 12345
#How often polling loop will execute
export SERVER_TIMEOUT := 30
#Broker address
export MQTT_ADDRESS := 0.0.0.0
#Broker port
export MQTT_PORT := 12345
#Broker username
export MQTT_USERNAME := username
#Broker password
export MQTT_PASSWORD := password
#Topics of the broker you want to read separated by comma and space(', ') 
export MQTT_TOPICS := topic1, topic2

COMPOSE_FILE = docker-compose.yml
DOCKER_COMPOSE = docker-compose -f $(COMPOSE_FILE)

.PHONY: up down build build-no-cache start stop restart logs ps exec shell help

up:
	$(DOCKER_COMPOSE) up -d

up-output:
	$(DOCKER_COMPOSE) up

down:
	$(DOCKER_COMPOSE) down

build:
	$(DOCKER_COMPOSE) build

build-no-cache:
	$(DOCKER_COMPOSE) build --no-cache

start:
	$(DOCKER_COMPOSE) start

stop:
	$(DOCKER_COMPOSE) stop

restart:
	$(DOCKER_COMPOSE) restart

logs:
	$(DOCKER_COMPOSE) logs -f

ps:
	$(DOCKER_COMPOSE) ps

exec:
	$(DOCKER_COMPOSE) exec $(SERVICE) $(COMMAND)

shell:
	$(DOCKER_COMPOSE) exec $(SERVICE) /bin/sh

help:
	@echo "Makefile commands for docker-compose:"
	@echo "  make up             - Start the containers in detached mode"
	@echo "  make down           - Stop and remove the containers"
	@echo "  make build          - Build or rebuild services"
	@echo "  make build-no-cache - Build services without using cache"
	@echo "  make start          - Start existing containers"
	@echo "  make stop           - Stop running containers"
	@echo "  make restart        - Restart running containers"
	@echo "  make logs           - View output from containers"
	@echo "  make ps             - List containers"
	@echo "  make exec           - Execute a command in a running container (requires SERVICE and COMMAND)"
	@echo "  make shell          - Start a shell in a running container (requires SERVICE)"
	@echo "  make help           - Show this help message"
