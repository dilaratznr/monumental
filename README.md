# Monumental Project

## Overview
The Monumental Project is designed to estimate the 3D pose of bricks using RGB-D images. The project involves a Django application that processes the images, calculates the 3D pose, and visualizes the results.

## Features
- **3D Pose Estimation**: Computes the position and orientation of bricks.
- **Image Processing**: Uses OpenCV for detecting and analyzing bricks in images.
- **Visualization**: Provides visual representation of the 3D pose.

## Technologies and Libraries Used
- **Django**: Web application framework.
- **OpenCV**: Image processing library.
- **Numpy**: For numerical computations.
- **SciPy (Rotation)**: For 3D rotation calculations.
- **Matplotlib**: For generating visualizations.
- **Git**: Version control, repository can be accessed [here](https://github.com/dilaratznr/monumental).

## Installation and Usage
1. Clone the repository:
git clone https://github.com/dilaratznr/monumental.git
cd monumental

2. Set up the virtual environment and install dependencies:

python -m venv env
source env/bin/activate
pip install -r requirements.txt

3. Run the Django server:
python manage.py runserver

## Docker Instructions
1. **Load the Docker Image**:
docker load -i brick_pose_estimation.tar


2. **Run the Docker Container**:
docker run [OPTIONS] dilaratznr/brick_pose_estimation

## License

## Contact
dilaratuezuner@gmail.com




