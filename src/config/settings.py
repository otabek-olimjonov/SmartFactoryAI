import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# RabbitMQ Configuration
RABBITMQ_CONFIG = {
    'host': os.getenv('RABBITMQ_HOST', 'localhost'),
    'port': int(os.getenv('RABBITMQ_PORT', 5672)),
    'username': os.getenv('RABBITMQ_USER', 'admin_user'),
    'password': os.getenv('RABBITMQ_PASS', '123456#'),
}

# Node-RED Configuration
NODERED_ENDPOINT = os.getenv('NODERED_ENDPOINT', 'http://localhost:1880/ai-result')

# Queue Configuration
QUEUE_CONFIG = {
    'exchange': 'NSU',
    'exchange_type': 'direct',
    'queues': {
        'web_to_ai': 'WEB_TO_AI',
        'nodered_to_ai': 'NODERED_TO_AI'
    }
}

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')