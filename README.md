# Recursive Mirror Effect Generator For Images
This Python script implements a recursive mirror effect on a selected image, producing a unique and captivating visual pattern. It methodically reduces the size of the image in each iteration and overlays these smaller versions onto the original, creating a concentric, mirrored design. The script offers customizable parameters such as shrink factor and maximum iterations, allowing for varied artistic expressions. Additionally, it features an option to generate a timelapse video of the transformation process, which can include a reverse playback segment for a seamless looping effect.

## Prerequisites
Before using this script, make sure you have the following installed:

- Python 3.x
- MoviePy library (`pip install moviepy`)
- Pillow library (`pip install Pillow`)

## Usage
1. **Clone the Repository:**
   ```bash
   git clone https://github.com/Silentoplayz/Recursive-Mirror-Effect-Generator-For-Images.git
   cd recursive-mirror-effect
   ```

# **Install Dependencies**
  ```python
  pip install -r requirements.txt
  ```

# **Run the Script:**
  ```python
  python recursive_mirror_effect.py
  ```
**Follow the on-screen prompts to select an image and input parameters.**

# Parameters

| Parameter                     | Description                                                                                                       |
|-------------------------------|-------------------------------------------------------------------------------------------------------------------|
| Shrink Factor (float)         | Enter a shrink factor (e.g., 0.99) to determine how much each iteration of the image is reduced in size.         |
| Max Iterations (integer)      | Set the maximum number of iterations. Higher values result in more repetitions of the shrinking and pasting process. |
| Save Timelapse (yes/no)       | Specify whether to save a timelapse video of the image processing. Respond 'yes' to save a video showing each iteration. |
| FPS for Timelapse (integer)   | Enter the Frames Per Second (FPS) for the timelapse video. Higher FPS results in a smoother video.                  |
| Include Reverse (yes/no)      | Decide whether to include a reversed clip in the timelapse video, creating a seamless loop effect.                   |

# Output
The final processed image is saved as output_image.png in the script's directory. If you choose to save a timelapse video, it will be saved as time_lapse.mp4.

# License
This project is licensed under the MIT License - see the LICENSE.txt file for details.

# Acknowledgments
This script uses the Pillow and MoviePy libraries.
