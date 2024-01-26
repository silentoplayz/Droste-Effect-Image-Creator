import argparse
import atexit
import datetime
import os
import shutil
import sys
import tempfile
import time
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

def process_image_for_droste_effect(image_path, temp_dir, shrink_factor, max_iterations, resampling_method, rotation_angle):
    frame_paths = []
    frame_format = 'bmp'
    try:
        # Load the original image
        original_image = Image.open(image_path)

        # Convert to 'RGBA' for transparency support
        if original_image.mode != 'RGBA':
            original_image = original_image.convert('RGBA')

        current_image = original_image.copy()
        current_size = original_image.size
        total_rotation = 0  # Initialize total rotation

        # Save the original image as the first frame
        frame_path = os.path.join(temp_dir, f"frame_0.{frame_format}")
        if not save_image_with_format(original_image, frame_path, frame_format):
            print("Failed to save the initial frame.")
            return [], None

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

        return frame_paths, original_image
    except Exception as e:
        print(f"Error in image processing: {e}")
        return [], None

def create_videos(frame_paths, timelapse_video_path, reversed_clip_path, fps, include_reverse, save_reversed_clip):
    start_time = time.time()
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

        end_time = time.time()  # End time measurement
        print(f"Video creation completed in {end_time - start_time:.2f} seconds.")

        return True
    except Exception as e:
        print(f"Error in video creation: {e}")
        return False

def create_droste_image_effect(image_path, output_path, shrink_factor, max_iterations, save_timelapse, fps, include_reverse, timelapse_video_path, reversed_clip_path, save_reversed_clip, unique_suffix, resampling_method, rotation_angle, output_format):
    start_time = time.time()

    temp_dir = None
    try:
        temp_dir = tempfile.mkdtemp()
        frame_paths, final_image = process_image_for_droste_effect(
            image_path, temp_dir, shrink_factor, max_iterations, resampling_method, rotation_angle
        )

        if not frame_paths or final_image is None:
            return

        if not save_image_with_format(final_image, output_path, output_format):
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
        print(f"Output Image Format: {output_format}")
        print(f"Rotation Angle: {rotation_angle}")

    except Exception as e:
        print(f"An error occurred during image processing: {e}")
    finally:
        # Cleanup the temporary directory
        if temp_dir:
            cleanup_temp_dir(temp_dir)
        
        end_time = time.time()
        print(f"Total time for creating Droste effect: {end_time - start_time:.2f} seconds.")

def save_image_with_format(image, path, format):
    try:
        # Check if the format is JPEG or JPG and the image mode is RGBA
        if format in ['jpeg', 'jpg'] and image.mode == 'RGBA':
            image = image.convert('RGB')
        # Save with high quality for JPEG
        if format in ['jpeg', 'jpg']:
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
    parser = argparse.ArgumentParser(description="Create Droste Image Effect")
    parser.add_argument("--image_path", help="Path to the input image")
    parser.add_argument("--shrink_factor", type=float, help="Shrink factor for the image")
    parser.add_argument("--max_iterations", type=int, help="Maximum number of iterations")
    parser.add_argument("--save_timelapse", type=lambda x: (str(x).lower() in ['yes', 'true']), help="Save timelapse video (yes/true or no/false)")
    parser.add_argument("--fps", type=int, help="Frames per second for timelapse video")
    parser.add_argument("--include_reverse", type=lambda x: (str(x).lower() in ['yes', 'true']), help="Include reversed clip in video (yes/true or no/false)")
    parser.add_argument("--save_reversed_clip", type=lambda x: (str(x).lower() in ['yes', 'true']), help="Save reversed clip by itself (yes/true or no/false)")
    parser.add_argument("--resampling_method", help="Image Resampling Method")
    parser.add_argument("--rotation_angle", type=float, help="Rotation angle per iteration")
    parser.add_argument("--output_format", help="Format for the output image", choices=['png', 'jpg', 'jpeg', 'bmp', 'webp'], default='bmp')
    parser.add_argument("--output_path", help="Path for the output image", default="output_image.bmp")

    args = parser.parse_args()

    if args.image_path:
        # Command-line mode
        # Validate the image path
        if args.image_path and not os.path.isfile(args.image_path):
            print(f"Error: The specified image path does not exist: {args.image_path}")
            sys.exit(1)

        # Validate other required arguments
        if args.shrink_factor is None or args.max_iterations is None or args.resampling_method is None or args.output_format is None or args.rotation_angle is None:
            parser.error("All arguments (shrink_factor, max_iterations, resampling_method, output_format, rotation_angle) are required for command-line mode.")

        # Validate numerical arguments
        if args.shrink_factor is not None and not (0 < args.shrink_factor <= 1):
            print("Error: Shrink factor must be greater than 0 and less than or equal to 1.")
            sys.exit(1)

        if args.max_iterations is not None and args.max_iterations <= 0:
            print("Error: Maximum iterations must be a positive integer.")
            sys.exit(1)

        if args.fps is not None and args.fps <= 0:
            print("Error: FPS must be a positive integer.")
            sys.exit(1)

        if args.rotation_angle is not None and not (-360 <= args.rotation_angle <= 360):
            print("Error: Rotation angle must be between -360 and 360 degrees.")
            sys.exit(1)

        # Validate resampling method
        valid_resampling_methods = ['NEAREST', 'BOX', 'BILINEAR', 'HAMMING', 'BICUBIC', 'LANCZOS']
        if args.resampling_method and args.resampling_method.upper() not in valid_resampling_methods:
            print(f"Error: Invalid resampling method. Choose from {', '.join(valid_resampling_methods)}.")
            sys.exit(1)

        # Set default values for optional arguments if not provided
        args.save_timelapse = args.save_timelapse if args.save_timelapse is not None else True
        args.fps = args.fps if args.fps is not None else 10
        args.include_reverse = args.include_reverse if args.include_reverse is not None else False
        args.save_reversed_clip = args.save_reversed_clip if args.save_reversed_clip is not None else True

        # Generate the unique suffix
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = os.path.splitext(os.path.basename(args.image_path))[0]
        unique_suffix = f"{base_filename}_{timestamp}"

        # Apply the unique suffix to the output paths
        output_image_path = f"output_{unique_suffix}.{args.output_format}"
        timelapse_video_path = f"time_lapse_{unique_suffix}.mp4" if args.save_timelapse else None
        reversed_clip_path = f"reversed_clip_{unique_suffix}.mp4" if args.save_reversed_clip else None

        # Call the image processing function with the updated paths
        create_droste_image_effect(
            args.image_path, output_image_path, args.shrink_factor, args.max_iterations,
            args.save_timelapse, args.fps, args.include_reverse, timelapse_video_path,
            reversed_clip_path, args.save_reversed_clip, unique_suffix,
            args.resampling_method, args.rotation_angle, args.output_format
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
            
            # Add a dialog for choosing the output image format
            output_format_options = ['png', 'jpg', 'jpeg', 'bmp', 'webp']
            output_format = get_input_from_options("Enter Output Image Format", output_format_options, root)

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
            output_image_path = f"output_{unique_suffix}.{output_format}"
            timelapse_video_path = f"time_lapse_{unique_suffix}.mp4" if save_timelapse else None
            reversed_clip_path = f"reversed_clip_{unique_suffix}.mp4" if save_reversed_clip else None

            # Create the recursive mirror effect
            create_droste_image_effect(
                file_path, output_image_path, shrink_factor, max_iterations,
                save_timelapse, fps, include_reverse, timelapse_video_path,
                reversed_clip_path, save_reversed_clip, unique_suffix,
                resampling_method, rotation_angle, output_format
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