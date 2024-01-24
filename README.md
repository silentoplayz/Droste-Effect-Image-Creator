# Recursive Mirror Effect Generator For Images
This is a Python script that applies a recursive mirror effect to an input image, creating an artistic and visually interesting result. It shrinks and pastes iterations of the image onto itself, producing a mirrored and progressively smaller pattern.

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

| Parameter                | Description                                                                                                       |
|--------------------------|-------------------------------------------------------------------------------------------------------------------|
| Shrink Factor (float)    | Enter a shrink factor (e.g., 0.99) to determine how much each iteration of the image is reduced in size.         |
| Max Iterations (integer) | Set the maximum number of iterations. Higher values result in more repetitions of the shrinking and pasting process. |
| Save Timelapse (yes/no)  | Specify whether to save a timelapse video of the image processing. Respond 'yes' to save a video showing each iteration. |
| FPS for Timelapse (integer) | Enter the Frames Per Second (FPS) for the timelapse video. Higher FPS results in a smoother video.                  |


# Output
The final processed image is saved as output_image.png in the script's directory. If you choose to save a timelapse video, it will be saved as time_lapse.mp4.

# License
This project is licensed under the MIT License - see the LICENSE.txt file for details.

# Acknowledgments
This script uses the Pillow and MoviePy libraries.
