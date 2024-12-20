from typing import Dict, Any, Optional
from src.utils.logger import setup_logger
from pyzbar.pyzbar import decode
from src.utils.camera import GalaxyCamera
import cv2
import time
import numpy as np

logger = setup_logger(__name__)

class TaskAnalyzer:
    """
    Comprehensive task analyzer with methods for different inspection tasks
    """
    
    @staticmethod
    def _init_camera(camera_id: int = 1) -> Optional[cv2.VideoCapture]:
        """
        Initialize the camera
        
        :param camera_id: Camera device ID (default is 0 for primary camera)
        :return: VideoCapture object or None if camera initialization fails
        """
        camera = GalaxyCamera(device_index=camera_id)
        if not camera.isOpened():
            return None
        return camera
    
    @staticmethod
    def _read_qr_code(frame: np.ndarray) -> Optional[str]:
        """
        Read QR code from a frame
        
        :param frame: Image frame from camera
        :return: Decoded QR code text or None if no QR code found
        """
        # Convert frame to grayscale for better QR code detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Decode QR codes in the frame
        qr_codes = decode(gray)
        
        if qr_codes:
            # Return the text from the first detected QR code
            return qr_codes[0].data.decode('utf-8')
        return None

    @staticmethod
    def case_task_analysis(task_data: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """
        Analysis for case task - reads QR code from camera

        :return: Analysis result dictionary
        """
        # Extract parameters from task_data
        camera_id = task_data.get('camera_id', 1) if task_data else 1
        timeout = task_data.get('timeout', 30) if task_data else 30
        
        # Initialize result dictionary
        result = {
            'task_name': 'case_task',
            'status': 'NG',
            'confidence': '0%',
            'details': 'QR code detection not started'
        }
        
        # Initialize camera
        camera = TaskAnalyzer._init_camera(camera_id)
        if not camera:
            result['details'] = f'Failed to initialize camera {camera_id}'
            return result
        
        try:
            start_time = time.time()
            while (time.time() - start_time) < timeout:
                # Read frame from camera
                ret, frame = camera.read()
                if not ret:
                    continue
                
                # Try to read QR code
                qr_text = TaskAnalyzer._read_qr_code(frame)
                if qr_text:
                    result['status'] = 'OK'
                    result['confidence'] = '95%'
                    result['details'] = f'QR Code detected: {qr_text}'
                    break
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.1)
            
            if result['status'] == 'NG':
                result['details'] = 'No QR code detected within timeout period'
                
        except Exception as e:
            result['details'] = f'Error during QR code detection: {str(e)}'
            
        finally:
            # Always release the camera
            camera.release()
        
        return result

    @staticmethod
    def box_task_analysis(task_data: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """
        Analysis for box task
        
        :param task_data: Optional task-specific data
        :return: Analysis result
        """
        # Placeholder for box task specific analysis
        # TODO: Implement actual box task analysis logic
        return {
            'task_name': 'box_task',
            'status': 'OK',  # or 'NG'
            'confidence': '92%',
            'details': 'Box inspection and measurement completed'
        }

    @staticmethod
    def cover_task_analysis(task_data: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """
        Analysis for cover task
        
        :param task_data: Optional task-specific data
        :return: Analysis result
        """
        # Placeholder for cover task specific analysis
        # TODO: Implement actual cover task analysis logic
        return {
            'task_name': 'cover_task',
            'status': 'OK',  # or 'NG'
            'confidence': '93%',
            'details': 'Cover inspection and fitting analysis completed'
        }

    @staticmethod
    def folding_task_analysis(task_data: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """
        Analysis for folding task
        
        :param task_data: Optional task-specific data
        :return: Analysis result
        """
        # Placeholder for folding task specific analysis
        # TODO: Implement actual folding task analysis logic
        return {
            'task_name': 'folding_task',
            'status': 'OK',  # or 'NG'
            'confidence': '94%',
            'details': 'Folding precision and quality inspection completed'
        }

    @staticmethod
    def final_check_task_analysis(task_data: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """
        Final comprehensive task analysis
        
        :param task_data: Optional task-specific data
        :return: Final analysis result
        """
        # Placeholder for final comprehensive check
        # TODO: Implement actual final check logic
        return {
            'task_name': 'final_check_task',
            'status': 'OK',  # or 'NG'
            'confidence': '96%',
            'details': 'Comprehensive final inspection completed'
        }
