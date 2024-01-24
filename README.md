# Dostre Effect Image Creator
Transform ordinary images into extraordinary works of art with the mesmerizing Dostre Effect using this Python script. The script applies a recursive mirror effect to a selected image, producing a unique and captivating visual pattern. It systematically reduces the image size in each iteration and overlays these smaller versions onto the original, creating a concentric, mirrored design. Customize parameters like the shrink factor and maximum iterations for varied artistic expressions. The script even allows you to generate a timelapse video of the transformation process, complete with reverse playback for a seamless looping effect. Ideal for artists and programmers alike, this script is a simple yet powerful way to explore new dimensions in image processing.

## Prerequisites
Before using this script, please ensure you have the following installed:

- Python 3.x
- MoviePy library (`pip install moviepy`)
- Pillow library (`pip install Pillow`)

## Usage
1. **Clone the Repository:**
   ```bash
   git clone https://github.com/Silentoplayz/Dostre-Effect-Image-Creator.git
   cd dostre-image-effect-creator
   ```

# **Install Dependencies**
  ```python
  pip install -r requirements.txt
  ```

# **Run the Script:**
  ```python
  python dostre_image_effect.py
  ```
**Follow the on-screen prompts to select an image and input parameters.**

# Parameters

| Parameter                         | Description                                                                                                       |
|-----------------------------------|-------------------------------------------------------------------------------------------------------------------|
| Shrink Factor (float, required)   | Enter a shrink factor (e.g., 0.99) to determine how much each iteration of the image is reduced in size.         |
| Max Iterations (integer, required)| Set the maximum number of iterations. Higher values result in more repetitions of the shrinking and pasting process. |
| Save Timelapse (yes/no)           | Specify whether to save a timelapse video of the image processing. Respond 'yes' to save a video showing each iteration. |
| FPS for Timelapse (integer)       | Enter the Frames Per Second (FPS) for the timelapse video. Higher FPS results in a smoother video.                  |
| Include Reverse (yes/no)          | Decide whether to include a reversed clip in the timelapse video, creating a seamless loop effect.                   |
| Save Reversed Clip (yes/no)       | Choose whether to save the reversed clip separately. Respond 'yes' to save a reversed clip showing the image sequence in reverse. |
| Image Resampling Method (string)  | Select the resampling method for image processing (e.g., 'NEAREST', 'BOX', 'BILINEAR', 'HAMMING', 'BICUBIC', 'LANCZOS').                                    |
| Frame Format (string)             | Choose the format for saving frames during image processing (e.g., 'png', 'jpg', 'jpeg', 'bmp').                                   |
| Rotation Angle (float)            | Enter the rotation angle per iteration (e.g., 10 degrees) to apply a cumulative rotation effect to each image iteration. |

# Output
The final processed image is saved as `output_{unique_suffix}.png` in the script's directory. If you choose to save a timelapse video, it will be saved as `time_lapse_{unique_suffix}.mp4`. If you opt to save the reversed clip separately, it will be named `reversed_clip_{unique_suffix}.mp4`.

# Disclaimer
**Each iteration of the image is processed sequentially, meaning the final outcome of your chosen parameters may not be immediately apparent. Therefore, I personally encourage experimentation with the parameters and and learning from the results to fine-tune the effect(s) to your preference. This iterative process is part of the creative journey, offering a hands-on experience in digital art creation.**

# License
This project is licensed under the MIT License - see the LICENSE.txt file for details.

# Acknowledgments
This script uses the Pillow and MoviePy libraries.

Read this README again and again: [README](https://github.com/Silentoplayz/Recursive-Mirror-Effect-Generator-For-Images/blob/main/README.md)
