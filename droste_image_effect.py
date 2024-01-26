import argparse
import atexit
import datetime
import os
import shutil
import sys
import tempfile
import tkinter as tk
import traceback
from tkinter import filedialog, simpledialog

from PIL import Image
from moviepy.editor import ImageSequenceClip, concatenate_videoclips, vfx

def cleanup_temp_dir(temp_dir):
    try:
        shutil.rmtree(temp_dir)
        print(f"Temporary files cleaned up: {temp_dir}")
    except Exception as e:
        print(f"Error cleaning up temporary files: {e}")

def process_image_for_droste_effect(image_path, temp_dir, shrink_factor, max_iterations, resampling_method, frame_format, rotation_angle):
    frame_paths = []
    try:
        # Load the original image
        original_image = Image.open(image_path)

        # Convert to 'RGBA' for transparency support
        if original_image.mode != 'RGBA':
            original_image = original_image.convert('RGBA')

        current_image = original_image.copy()
        current_size = original_image.size
        total_rotation = 0  # Initialize total rotation
        frame_paths = []

        # Save the original image as the first frame
        frame_path = os.path.join(temp_dir, f"frame_0.{frame_format}")
        if not save_image_with_format(original_image, frame_path, frame_format):
            print("Failed to save the initial frame.")
            return

        frame_paths.append(frame_path)

        for iteration in range(1, max_iterations):
            print(f"Processing iteration {iteration}...")

            # Calculate the new size
            new_width = int(current_size[0] * shrink_factor)
            new_height = int(current_size[1] * shrink_factor)

            # Break the loop if the new size is too small
            if new_width <= 0 or new_height <= 0:
                print("Image has become too small to process further.")
                break

            # Resize the image with user-specified resampling method
            resized_image = current_image.resize((new_width, new_height), getattr(Image.Resampling, resampling_method))

            # Update total rotation
            total_rotation += rotation_angle
            # Rotate the image by the accumulated angle with a transparent background
            rotated_image = resized_image.rotate(total_rotation, expand=True, fillcolor=(0,0,0,0))

            print("Rotated image size:", rotated_image.size)
            print("Original image size:", original_image.size)

            # Calculate the position to paste the resized image
            paste_x = (original_image.size[0] - rotated_image.size[0]) // 2
            paste_y = (original_image.size[1] - rotated_image.size[1]) // 2

            # Create a new transparent image to paste the rotated image
            transparent_image = Image.new('RGBA', original_image.size, (0, 0, 0, 0))
            transparent_image.paste(rotated_image, (paste_x, paste_y), rotated_image)

            # Paste the transparent image onto the original image
            original_image.paste(transparent_image, (0, 0), transparent_image)

            # Update the current size for the next iteration
            current_size = (new_width, new_height)

            # Save the frame with user-specified frame format
            frame_path = os.path.join(temp_dir, f"frame_{iteration}.{frame_format}")
            if not save_image_with_format(original_image, frame_path, frame_format):
                print(f"Failed to save frame {iteration}.")
                return [], None

            frame_paths.append(frame_path)
            current_size = (new_width, new_height)

        return frame_paths, original_image
    except Exception as e:
        print(f"Error in image processing: {e}")
        return [], None

def create_videos(frame_paths, timelapse_video_path, reversed_clip_path, fps, include_reverse, save_reversed_clip):
    if not frame_paths:
        return False

    try:
        if not create_timelapse_video(frame_paths, timelapse_video_path, fps, include_reverse):
            print("Failed to create the time-lapse video.")
            return False

        if save_reversed_clip:
            if not create_timelapse_video(frame_paths[::-1], reversed_clip_path, fps, False):
                print("Failed to create the reversed clip.")
                return False

        return True
    except Exception as e:
        print(f"Error in video creation: {e}")
        return False

def create_droste_image_effect(image_path, output_path, shrink_factor, max_iterations, save_timelapse, fps, include_reverse, timelapse_video_path, reversed_clip_path, save_reversed_clip, unique_suffix, resampling_method, frame_format, rotation_angle):
    temp_dir = None
    try:
        temp_dir = tempfile.mkdtemp()
        frame_paths, final_image = process_image_for_droste_effect(
            image_path, temp_dir, shrink_factor, max_iterations, resampling_method, frame_format, rotation_angle
        )

        if not frame_paths or final_image is None:
            return

        if not save_image_with_format(final_image, output_path, frame_format):
            print("Failed to save the final image.")
            return

        print("Image processing complete.")

        # Create the time-lapse video and/or reversed clip if required
        if save_timelapse or save_reversed_clip:
            if not create_videos(frame_paths, timelapse_video_path, reversed_clip_path, fps, include_reverse, save_reversed_clip):
                print("Failed to create videos.")
            else:
                if save_timelapse:
                    print(f"Time-lapse video saved as {timelapse_video_path}")
                if save_reversed_clip:
                    print(f"Reversed clip saved as {reversed_clip_path}")

        # Display the chosen parameters
        print("\nChosen Parameters:")
        print(f"Shrink Factor: {shrink_factor}")
        print(f"Max Iterations: {max_iterations}")
        print(f"Save Timelapse: {save_timelapse}")
        if save_timelapse:
            print(f"FPS for Timelapse: {fps}")
            print(f"Include Reverse: {include_reverse}")
            print(f"Save Reversed Clip: {save_reversed_clip}")
        print(f"Image Resampling Method: {resampling_method}")
        print(f"Frame Format: {frame_format}")
        print(f"Rotation Angle: {rotation_angle}")

    except Exception as e:
        print(f"An error occurred during image processing: {e}")
    finally:
        # Cleanup the temporary directory
        if temp_dir:
            cleanup_temp_dir(temp_dir)

def save_image_with_format(image, path, format):
    try:
        # Check if the frame format is JPEG or JPG and the image mode is RGBA
        if format in ['jpeg', 'jpg']:
            # Convert to RGB before saving if necessary
            if image.mode == 'RGBA':
                image = image.convert('RGB')
            # Save with high quality
            image.save(path, quality=100)
        else:
            # Save in the current mode for other formats
            image.save(path)
        return True
    except Exception as e:
        print(f"An error occurred while saving the image: {e}")
        return False

def create_timelapse_video(frame_paths, output_filename, fps, include_reverse):
    try:
        # Create a clip from the frames
        clip = ImageSequenceClip(frame_paths, fps=fps)
        clip.duration = len(frame_paths) / float(fps)

        if include_reverse:
            # Manually create a reversed clip
            reversed_frame_paths = frame_paths[::-1]
            reversed_clip = ImageSequenceClip(reversed_frame_paths, fps=fps)
            reversed_clip.duration = clip.duration

            # Concatenate the original clip with the manually created reversed clip
            final_clip = concatenate_videoclips([clip, reversed_clip])
        else:
            final_clip = clip

        # Write the final clip to a file
        final_clip.write_videofile(output_filename, codec='libx264')
        return True
    except Exception as e:
        print(f"An error occurred during video creation: {e}")
        traceback.print_exc()
        return False

def get_yes_no_input(prompt, parent=None):
    while True:
        response = simpledialog.askstring("Input", prompt, parent=parent)
        if response is None:  # User pressed cancel
            print("Operation cancelled by user.")
            sys.exit(0)  # Exit the script
        elif response.lower() in ['yes', 'no', 'true', 'false']:
            return response.lower() in ['yes', 'true']
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")

def get_input_from_options(prompt, options, parent=None):
    while True:
        response = simpledialog.askstring("Input", f"{prompt} (choose from {', '.join(options)}):", parent=parent)
        if response is None:  # User pressed cancel
            print("Operation cancelled by user.")
            sys.exit(0)  # Exit the script
        elif response.lower() in [option.lower() for option in options]:
            return response.lower()
        else:
            print(f"Invalid input. Please choose from {', '.join(options)}.")

def main():
    # Command-line argument parsing
    parser = argparse.ArgumentParser(description="Create Dostre Image Effect")
    parser.add_argument("--image_path", help="Path to the input image")
    parser.add_argument("--shrink_factor", type=float, help="Shrink factor for the image")
    parser.add_argument("--max_iterations", type=int, help="Maximum number of iterations")
    parser.add_argument("--save_timelapse", type=lambda x: (str(x).lower() in ['yes', 'true']), help="Save timelapse video (yes/true or no/false)")
    parser.add_argument("--fps", type=int, help="Frames per second for timelapse video")
    parser.add_argument("--include_reverse", type=lambda x: (str(x).lower() in ['yes', 'true']), help="Include reversed clip in video (yes/true or no/false)")
    parser.add_argument("--save_reversed_clip", type=lambda x: (str(x).lower() in ['yes', 'true']), help="Save reversed clip by itself (yes/true or no/false)")
    parser.add_argument("--resampling_method", help="Image Resampling Method")
    parser.add_argument("--frame_format", help="Frame Format")
    parser.add_argument("--rotation_angle", type=float, help="Rotation angle per iteration")
    parser.add_argument("--output_path", help="Path for the output image", default="output_image.bmp")

    args = parser.parse_args()

    if args.image_path:
        # Command-line mode
        # Ensure all required arguments are provided
        required_args = [args.shrink_factor, args.max_iterations, args.resampling_method, args.frame_format, args.rotation_angle]
        if any(arg is None for arg in required_args):
            parser.error("All arguments are required for command-line mode.")
        
        # Set default values for optional arguments if not provided
        args.save_timelapse = args.save_timelapse if args.save_timelapse is not None else True
        args.fps = args.fps if args.fps is not None else 10
        args.include_reverse = args.include_reverse if args.include_reverse is not None else False
        args.save_reversed_clip = args.save_reversed_clip if args.save_reversed_clip is not None else True

        # Generate output paths based on input image path
        base_filename = os.path.splitext(os.path.basename(args.image_path))[0]
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_suffix = f"{base_filename}_{timestamp}"
        output_image_path = args.output_path
        timelapse_video_path = f"time_lapse_{os.path.splitext(os.path.basename(output_image_path))[0]}.mp4" if args.save_timelapse else None
        reversed_clip_path = f"reversed_clip_{os.path.splitext(os.path.basename(output_image_path))[0]}.mp4" if args.save_reversed_clip else None

        # Call the image processing function
        create_droste_image_effect(
            args.image_path, output_image_path, args.shrink_factor, args.max_iterations,
            args.save_timelapse, args.fps, args.include_reverse, timelapse_video_path,
            reversed_clip_path, args.save_reversed_clip, unique_suffix,
            args.resampling_method, args.frame_format, args.rotation_angle
        )
    else:
        # GUI mode
        try:
            # Set up a root window for the file dialog (but don't display it)
            root = tk.Tk()
            root.withdraw()

            # Notify user to be patient
            print("Please select an image file. This may take a few moments...")

            # Open a file dialog to select an image
            file_path = filedialog.askopenfilename(title="Select an Image", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.webp")])
            if not file_path:
                raise ValueError("No file selected. Exiting the program.")

            # Get parameters from the user

            # Shrink Factor: Determines the reduction in size for each iteration.
            # A lower shrink factor results in a more significant reduction per iteration.
            shrink_factor = simpledialog.askfloat("Input", "Enter shrink factor (e.g., 0.99):", parent=root, minvalue=0.01, maxvalue=1.00)
            if shrink_factor is None:
                print("Operation cancelled by user.")
                sys.exit(0)

            # Max Iterations: Specifies the total number of shrinking and pasting iterations.
            # More iterations result in a more complex final image.
            max_iterations = simpledialog.askinteger("Input", "Enter maximum iterations (e.g., 100):", parent=root, minvalue=1)
            if max_iterations is None:
                print("Operation cancelled by user.")
                sys.exit(0)

            # Save Timelapse: Option to save a video showing the image processing over each iteration.
            save_timelapse = get_yes_no_input("Save timelapse video? (yes/no):", root)

            # FPS for Timelapse: Sets the frame rate for the timelapse video. Higher FPS for smoother playback.
            fps = None

            # Include Reverse: Determines if a reversed clip is added to the timelapse for a looping effect.
            include_reverse = False
            save_reversed_clip = False

            if save_timelapse:
                fps = simpledialog.askinteger("Input", "Enter FPS for timelapse (e.g., 10):", parent=root, minvalue=1)
                if fps is None:
                    print("Operation cancelled by user.")
                    sys.exit(0)
                include_reverse = get_yes_no_input("Include reversed clip in video? (yes/no):", root)
                save_reversed_clip = get_yes_no_input("Save reversed clip by itself? (yes/no):", root)

            # Image Resampling Method: Choose the method for resizing images during processing.
            resampling_options = ['NEAREST', 'BOX', 'BILINEAR', 'HAMMING', 'BICUBIC', 'LANCZOS']
            resampling_method_input = get_input_from_options("Enter Image Resampling Method", resampling_options, root)
            resampling_method = resampling_method_input.upper()

            # Frame Format: Select the format for saving frames (supports PNG, JPG, JPEG, BMP).
            frame_format_options = ['png', 'jpg', 'jpeg', 'bmp', 'webp']
            frame_format = get_input_from_options("Enter Frame Format", frame_format_options, root)

            # Rotation Angle: Define the angle of rotation applied to each image iteration.
            while True:
                rotation_angle = simpledialog.askfloat("Input", "Enter rotation angle per iteration (e.g., 10):", parent=root)
                if rotation_angle is None:  # User pressed cancel
                    print("Operation cancelled by user.")
                    sys.exit(0)  # Exit the script
                elif -360 <= rotation_angle <= 360:
                    break  # Valid input, exit the loop
                else:
                    print("Invalid input. Please enter a value between -360 and 360 degrees.")

            # Get the base filename without extension
            base_filename = os.path.splitext(os.path.basename(file_path))[0]
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_suffix = f"{base_filename}_{timestamp}"
            output_image_path = f"output_{unique_suffix}.{frame_format}"
            timelapse_video_path = f"time_lapse_{unique_suffix}.mp4" if save_timelapse else None
            reversed_clip_path = f"reversed_clip_{unique_suffix}.mp4" if save_reversed_clip else None

            # Create the recursive mirror effect
            create_droste_image_effect(
                file_path, output_image_path, shrink_factor, max_iterations,
                save_timelapse, fps, include_reverse, timelapse_video_path,
                reversed_clip_path, save_reversed_clip, unique_suffix,
                resampling_method, frame_format, rotation_angle
            )
            print(f"Image saved as {output_image_path}")

            if save_timelapse:
                print(f"Time-lapse video saved as {timelapse_video_path}")

            if save_reversed_clip:
                print(f"Reversed clip saved as {reversed_clip_path}")

        except tk.TclError as te:
            print(f"An error occurred during image selection: {te}")
        except ValueError as ve:
            print(f"Input validation error: {ve}")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()