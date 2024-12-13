# src/core/ai_control_system.py
import json
import pika
import requests
from typing import Dict, Any
from src.utils.logger import setup_logger
from src.config.settings import RABBITMQ_CONFIG, NODERED_ENDPOINT, QUEUE_CONFIG
from .task_analyzer import TaskAnalyzer

# Global variable for order data
current_order_data: Dict[str, Any] = {}

class AIControlSystem:
    def __init__(self):
        """Initialize AI Control System"""
        self.logger = setup_logger(__name__)
        
        # RabbitMQ connection parameters
        self.connection_params = pika.ConnectionParameters(
            host=RABBITMQ_CONFIG['host'],
            port=RABBITMQ_CONFIG['port'],
            credentials=pika.PlainCredentials(
                RABBITMQ_CONFIG['username'],
                RABBITMQ_CONFIG['password']
            )
        )
        
        self.nodered_endpoint = NODERED_ENDPOINT
        self.queues = QUEUE_CONFIG['queues']
        
        # Task analysis mapping
        self.task_analysis_map = {
            'case_task': TaskAnalyzer.case_task_analysis,
            'box_task': TaskAnalyzer.box_task_analysis,
            'cover_task': TaskAnalyzer.cover_task_analysis,
            'folding_task': TaskAnalyzer.folding_task_analysis,
            'final_check_task': TaskAnalyzer.final_check_task_analysis
        }
        
        # Reference to global order data
        global current_order_data
        self.order_data = current_order_data

    def connect_to_rabbitmq(self):
        """
        Establish connection to RabbitMQ server
        """
        try:
            self.connection = pika.BlockingConnection(self.connection_params)
            self.channel = self.connection.channel()
            
            # Declare exchanges and queues
            self.channel.exchange_declare(exchange='NSU', exchange_type='direct')
            
            for queue_name in self.queues.values():
                self.channel.queue_declare(queue=queue_name)
                self.channel.queue_bind(
                    exchange='NSU', 
                    queue=queue_name, 
                    routing_key=f'{queue_name}_KEY'
                )
            
            self.logger.info("Connected to RabbitMQ successfully")
        except Exception as e:
            self.logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise

    def process_web_message(self, message_data: Dict[str, Any]):
        """
        Process and store messages from WEB_TO_AI queue
        
        :param message_data: JSON data received from web
        """
        try:
            # Validate required fields
            required_fields = ['ORDER_NO', 'ITEM_CD', 'ITEM_NM', 'ITEM_CLASS', 'BOM', 'RECIPE']
            for field in required_fields:
                if field not in message_data:
                    raise ValueError(f"Missing required field: {field}")

            # Update global order data
            global current_order_data
            current_order_data = message_data
            self.order_data = current_order_data
            
            self.logger.info(f"Updated order data: {message_data['ORDER_NO']}")
            
            # Log detailed information
            self.logger.info(f"Order details - Item: {message_data['ITEM_NM']}, "
                           f"Class: {message_data['ITEM_CLASS']}, "
                           f"BOM Count: {len(message_data['BOM'])}, "
                           f"Recipe Count: {len(message_data['RECIPE'])}")
            
        except Exception as e:
            self.logger.error(f"Error processing web message: {e}")
            raise

    def get_current_order_data(self) -> Dict[str, Any]:
        """
        Get the current order data
        
        :return: Current order data dictionary
        """
        return self.order_data

    def process_task_analysis(self, task_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process specific task analysis based on task name
        
        :param task_request: Task analysis request dictionary
        :return: Processing results
        """
        try:
            # Extract the task name from the request
            task_name = task_request.get('START', 'UNKNOWN_TASK')
            
            # Get the appropriate analysis method
            analysis_method = self.task_analysis_map.get(
                task_name, 
                lambda: {'error': 'Unknown task'}
            )
            
            # Include current order data in analysis if available
            task_data = {
                'order_data': self.order_data,
                'task_request': task_request
            }
            
            # Perform the specific task analysis
            analysis_result = analysis_method(task_data)
            
            result = {
                'NAME': task_name,
                'RESULT': analysis_result.get('status', 'ERROR'),
                'ORDER_NO': self.order_data.get('ORDER_NO', 'UNKNOWN'),
                'CONFIDENCE': analysis_result.get('confidence', '0%'),
                'DETAILS': analysis_result.get('details', 'No details available')
            }
            
            self.logger.info(f"Task analysis completed: {result}")
            return result
        
        except Exception as e:
            self.logger.error(f"Error processing task analysis: {e}")
            return {
                'NAME': task_name,
                'RESULT': 'ERROR',
                'ORDER_NO': self.order_data.get('ORDER_NO', 'UNKNOWN'),
                'CONFIDENCE': '0%',
                'DETAILS': f'Error: {str(e)}'
            }

    def send_result_to_node_red(self, result: Dict[str, Any]):
        """
        Send processing results to Node-RED via REST API
        
        :param result: Processing result dictionary
        """
        try:
            # Use the stored Node-RED endpoint
            response = requests.post(
                self.nodered_endpoint, 
                json=result,
                timeout=5
            )
            response.raise_for_status()
            self.logger.info(f"Results sent to Node-RED successfully: {result}")
        
        except requests.RequestException as e:
            self.logger.error(f"Failed to send results to Node-RED: {e}")
            raise

    def consume_messages(self):
        """
        Consume messages from RabbitMQ queues
        """
        try:
            # Callback for WEB_TO_AI queue
            def web_to_ai_callback(ch, method, properties, body):
                try:
                    # Parse the incoming JSON message
                    web_data = json.loads(body)
                    self.logger.info(f"Received web data: {web_data['ORDER_NO']}")
                    
                    # Process and store the web data
                    self.process_web_message(web_data)
                    
                    # Acknowledge message
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                
                except Exception as e:
                    self.logger.error(f"Error processing web message: {e}")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

            # Callback for NODERED_TO_AI queue
            def nodered_to_ai_callback(ch, method, properties, body):
                try:
                    # Parse the incoming JSON message
                    task_request = json.loads(body)
                    self.logger.info(f"Received task analysis request: {task_request}")
                    
                    # Process the task analysis request
                    result = self.process_task_analysis(task_request)
                    
                    # Send result to Node-RED via REST API
                    self.send_result_to_node_red(result)
                    
                    # Acknowledge message
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                
                except Exception as e:
                    self.logger.error(f"Error processing task analysis request: {e}")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

            # Set up consumer for WEB_TO_AI queue
            self.channel.basic_consume(
                queue='WEB_TO_AI',
                on_message_callback=web_to_ai_callback
            )

            # Set up consumer for NODERED_TO_AI queue
            self.channel.basic_consume(
                queue='NODERED_TO_AI',
                on_message_callback=nodered_to_ai_callback
            )

            self.logger.info("Waiting for messages. To exit press CTRL+C")
            self.channel.start_consuming()
        
        except KeyboardInterrupt:
            self.channel.stop_consuming()
            self.connection.close()
            self.logger.info("Message consuming stopped")

    def run(self):
        """
        Main method to run the AI control system
        """
        try:
            self.connect_to_rabbitmq()
            self.consume_messages()
        except Exception as e:
            self.logger.error(f"AI Control System failed: {e}")
            raise