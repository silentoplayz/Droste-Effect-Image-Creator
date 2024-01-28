# Droste Effect Image Creator

This Python script can transform ordinary images into extraordinary works of art with the mesmerizing Droste Effect. The script applies a recursive mirror effect to a selected image, producing a unique and captivating visual pattern. It systematically reduces the image size in each iteration and overlays these smaller versions onto the original, creating a concentric, mirrored design. You can customize parameters such as the shrink factor and maximum iterations for varied artistic expressions. The script allows users to create a timelapse video of the transformation process, including reverse playback for a seamless looping effect. It is suitable for both artists and programmers and provides a straightforward yet powerful method to explore new dimensions in image processing.

## Features
- **Interactive GUI**: Easily select images and customize parameters through a user-friendly graphical interface.
- **Command-Line Support**: For advanced users, the script offers full command-line functionality. In the command-based arguments mode, if the user forgets to include the `--image_path` argument, the script automatically switches to the GUI mode and uses the provided command-line values to replace default GUI values.
- **Customizable Parameters**: Adjust the shrink factor, maximum iterations, rotation angle, and more to create unique effects.
- **Timelapse Video Creation**: Generate a video showing the transformation process, with options for reverse playback and FPS adjustment.
- **Image Resampling Methods**: Choose from various resampling methods for different image quality and processing speeds.
- **Format Flexibility**: Save the final image and videos in multiple formats.

## Prerequisites
Before using this script, please ensure you have the following installed:

- Python 3.x
- MoviePy library (`pip install moviepy`)
- Pillow library (`pip install Pillow`)

## Installation
**Clone the Repository:**
  ```bash
  git clone https://github.com/Silentoplayz/Droste-Effect-Image-Creator.git
  cd Droste-Effect-Image-creator
  ```

# **Install Dependencies**
  ```python
  pip install -r requirements.txt
  ```

# **Running the Script:**
## GUI-Based Usage:
  ```python
  python droste_image_effect.py
  ```
**Choose an image in the File Explorer pop-up, customize the default parameters to your liking, and then click on the Submit button.**

## Console-Based Usage:
  ```pythong
  python droste_image_effect.py --image_path <path_to_image> --shrink_factor <shrink_factor_value> --max_iterations <max_iterations_value> --save_timelapse <yes/no> --fps <fps_value> --include_reverse <yes/no> --save_reversed <yes/no> --resampling_method <resampling_method_value> --rotation_angle <rotation_angle_value> --output_format <output_format_value>
  ```
**Replace the placeholders (`<...>`) with the actual values you want to use for console-based execution. Feel free to use either the GUI or console-based command as per your preference.**

**For console-based usage, only the `--image_path` argument is required. Other parameters are optional and will use default values if not provided.**

# Parameters:

| Parameter                         | Description                                                                                                       | Console Command Example (if applicable)                           | Required Argument via Command-Line? | Default Argument Value (if not used) |
|-----------------------------------|-------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------|----------|--------------------------|
| Image Path (string)               | Path to the input image.                                                                                         | `--image_path path/to/your/image.jpg`                           | **Yes!**      | **N/A**                      |
| Shrink Factor (float)             | Enter a shrink factor to determine how much each iteration of the image is reduced in size.         | `--shrink_factor 0.99`                                           | No       | 0.95                     |
| Max Iterations (integer)          | Set the maximum number of iterations. Higher values result in more repetitions of the shrinking and pasting process. | `--max_iterations 200`                                           | No       | 100                      |
| Save Timelapse (boolean)           | Specify whether to save a timelapse video of the image processing. Respond with `yes` or `true` to save a video showing each iteration. | `--save_timelapse yes`                                           | No       | True                     |
| FPS for Timelapse (integer)       | Enter the Frames Per Second (FPS) for the timelapse video. Higher FPS results in a smoother video.                  | `--fps 30`                                                      | No       | 10                       |
| Include Reverse (boolean)          | Decide whether to include a reversed clip in the timelapse video, creating a seamless loop effect.                   | `--include_reverse no`                                           | No       | False                    |
| Save Reversed Clip (boolean)       | Choose whether to save the reversed clip separately. Respond with `yes` or `true` to save a reversed clip showing the image sequence in reverse. | `--save_reversed yes`                                      | No       | True                     |
| Image Resampling Method (string)  | Select the resampling method for image processing (e.g., `Nearest`, `Box`, `Bilinear`, `Hamming`, `Bicubic`, `Lanczos`). | `--resampling_method Bilinear`                                  | No      | Bilinear                 |
| Rotation Angle (float)            | Enter the rotation angle per iteration to apply a cumulative rotation effect to each image iteration. Use a negative number to rotate the image clockwise. | `--rotation_angle 60`                                           | No      | 0.0                      |
| Output Format (string)            | Choose the format for saving the final output image (e.g., `png`, `jpg`, `jpeg`, `bmp`, `webp`).                      | `--output_format bmp`                                           | No       | bmp                      |
| Output Path (string)              | Directory path for script's media output.                                                                                      | `--output_path path/to/save/output.bmp`                          | No       | output_image.bmp         |

# Output
- **The final processed image and timelapse videos are saved as `output_{output_base_path}.{output_format}` in the script's directory if ran in GUI mode, or as the `--output_path` directory if ran in console-based arguments mode.**
- If you choose to save a timelapse video, it will be saved as `time_lapse_{output_base_path}.mp4`. If you opt to save the reversed clip separately, it will be named `reversed_clip_{output_base_path}.mp4`.**

# Output Examples:
![output_photo-1607222337192-910fb1a5c661_20240124_160451](https://github.com/Silentoplayz/Droste-Effect-Image-Creator/assets/50341825/78788a25-9779-4a27-bfdd-0aae6694a6b7)

https://github.com/Silentoplayz/Droste-Effect-Image-Creator/assets/50341825/3e0e0105-2a3f-49f6-8243-81ea9a0d196b

https://github.com/Silentoplayz/Droste-Effect-Image-Creator/assets/50341825/06ef74e9-3ed1-44b6-9eb5-15eb2789d2f5

# Disclaimer
**Please note that while each image iteration is processed sequentially, the impact of certain parameters, like the shrink factor, may be predictable to an extent. For example, a shrink factor of 0.99 will reduce the image size by 1% in each iteration. However, the overall outcome, especially for complex parameter combinations, can be fully appreciated only after the process is complete (meaning the final outcome of your chosen parameters may not be immediately apparent). Therefore, I personally encourage experimentation with the parameters and learning from the results to fine-tune the effect(s) to your preference. This iterative process is part of the creative journey, offering a hands-on experience in digital art creation.**

# License
This project is licensed under the MIT License - see the ![LICENSE file](https://github.com/Silentoplayz/Droste-Effect-Image-Creator/blob/main/LICENSE) for details.

# Acknowledgments
This script uses the Pillow and MoviePy libraries.

Read this README again and again: ![README]([https://github.com/Silentoplayz/Droste-Effect-Image-Creator/blob/main/README.md)
