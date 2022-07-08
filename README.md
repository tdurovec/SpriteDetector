# SpriteDetector

Simple tool for automatic generation of meta-data from spritesheet (set of images that are used in the audiovisual layer inside the game) is based on the algorithm of object detection and in the case of jpeg, jpg images it is possible to delete the background. The tool is implemented on the network using the bank. The algorithm is programmed in python with opencv.

https://user-images.githubusercontent.com/37587096/178046861-6fcffd4b-e3b8-47e5-aa70-b0d80093db47.mp4

## Settings

###### Distance
Width and height of the structuring rectangular element. It is mainly used to connect several objects into one.

<img width="548" alt="Screenshot 2022-07-08 at 20 21 32" src="https://user-images.githubusercontent.com/37587096/178049071-277cd9c9-a170-4eb6-8d01-92ea442a08b0.png">

###### Toleranci
The program takes an image in png or jpg format for input from the user. If the image is very large, the user can reduce it to make the detection faster.
If it is a jpg image, the user can select the background color tolerance. This means that the background color does not always have to be monochromatic as it seems to us at first glance. For that the user can choose the color range of the rgb format, e.g. background-color (255, 255, 255) but
somewhere in the jpg image we can find a pixel with the color (255, 254, 255) that the program evaluates as an object. To prevent this, we set the tolerance to a reasonable value

<img width="569" alt="Screenshot 2022-07-08 at 20 28 19" src="https://user-images.githubusercontent.com/37587096/178049975-4977c5a8-bb70-4462-9104-ea3a3cbeade9.png">

## Run
Easy instalation with docker.

###### Build image
```
docker build --tag sprite_detection .
```

###### Run container
```
docker run -d -p 5000:5000 sprite_detection
```
###### ENJOY
