import cv2
from src.utils.camera import GalaxyCamera

# Initialize camera
cap = GalaxyCamera(device_index=1)

# Check if camera is opened successfully
if not cap.isOpened():
    print("Error: Could not open camera")
    exit()

try:
    while True:
        # Read frame
        ret, frame = cap.read()
        
        if ret:
            # Process frame with OpenCV
            cv2.imshow('Frame', frame)
            
            # Break loop with 'q' key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            print("Error: Couldn't read frame")
            break

finally:
    # Release resources
    cap.release()
    cv2.destroyAllWindows()