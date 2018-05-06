# Description
This is a simple opencv-based line follower written in python.  
I made this for fun and there is a lot of work to do, there will be several updates/improvments in future.
currently this software drives an RC car (toy) with an ESP32 onboard, but this is another project and I will release it later.

## DEMO
You can check full demo here: [media/demo.mp4](https://github.com/ShellAddicted/IceBreaker/blob/master/media/demo.mp4?raw=true) 
  
![DemoFrame](https://github.com/ShellAddicted/IceBreaker/blob/master/media/frame_46.jpg)

Demo Details:  
- RPI 3B + Picamera -> provides video feed to the PC over WiFi (running [videoStreamer.py](https://github.com/ShellAddicted/IceBreaker/blob/master/src/videoStreamer.py))
- RC Car (toy) with an ESP32 onboard controlled over WiFi
- PC (software tested under Arch Linux, but it should under windows & other distros)

# Requirements
- Python (>=3.6)  
- OpenCV (>=3.4)

# Do you want to use this on your own robot? DO IT!
just override the ```CvThread._drive(data)``` method with real controls of your robot  
```data``` is a numpy array of int that contains the distance between the center of the frame (and the robot) and the most externalTop point of the line.  
 - data[0] X axis distance  
 - data[1] Y axis distance  
 
use this data to feed you PID controller and Enjoy!
 
 

but remember to respect the [License](https://github.com/ShellAddicted/IceBreaker/blob/master/LICENSE)!  

# FAQ
## Why did you named it 'IceBreaker'?
Because I have not (yet) decided an official name so I will keep temporary the codename that i used in development
