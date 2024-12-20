# import cv2
# from src.utils.camera import GalaxyCamera

# # Initialize camera
# cap = GalaxyCamera(device_index=1)

# # Check if camera is opened successfully
# if not cap.isOpened():
#     print("Error: Could not open camera")
#     exit()

# try:
#     while True:
#         # Read frame
#         ret, frame = cap.read()
        
#         if ret:
#             # Process frame with OpenCV
#             cv2.imshow('Frame', frame)
            
#             # Break loop with 'q' key
#             if cv2.waitKey(1) & 0xFF == ord('q'):
#                 break
#         else:
#             print("Error: Couldn't read frame")
#             break

# finally:
#     # Release resources
#     cap.release()
#     cv2.destroyAllWindows()


import cv2
from typing import Dict, Any, Optional
from pyzbar.pyzbar import decode
import numpy as np
import time

class TaskAnalyzer:
    """
    Comprehensive task analyzer with methods for different inspection tasks
    """
    
    @staticmethod
    def _init_camera(camera_id: int = 0) -> Optional[cv2.VideoCapture]:
        """
        Initialize the camera
        
        :param camera_id: Camera device ID (default is 0 for primary camera)
        :return: VideoCapture object or None if camera initialization fails
        """
        camera = cv2.VideoCapture(camera_id)
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
        
        :param task_data: Optional task-specific data including:
            - camera_id: Optional camera device ID (default: 0)
            - timeout: Optional timeout in seconds (default: 30)
        :return: Analysis result dictionary
        """
        # Extract parameters from task_data
        camera_id = task_data.get('camera_id', 0) if task_data else 0
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

# Example usage:
if __name__ == "__main__":
    # Example with custom parameters
    task_data = {

    }
    
    analyzer = TaskAnalyzer()
    result = analyzer.case_task_analysis(task_data)
    print(result)