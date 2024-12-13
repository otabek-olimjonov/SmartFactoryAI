from src.core.ai_control_system import AIControlSystem
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def main():
    try:
        ai_system = AIControlSystem()
        ai_system.run()
    except Exception as e:
        logger.error(f"Main execution failed: {e}")
        raise

if __name__ == "__main__":
    main()