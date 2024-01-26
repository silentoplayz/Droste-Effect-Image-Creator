import argparse
import atexit
import datetime
import os
import shutil
import sys
import tempfile
import time
import tkinter as tk
import tkinter.ttk as ttk
import traceback
from tkinter import filedialog, messagebox
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

        # Mapping string input to PIL resampling methods
        resampling_methods = {
            "nearest": Image.Resampling.NEAREST,
            "box": Image.Resampling.BOX,
            "bilinear": Image.Resampling.BILINEAR,
            "hamming": Image.Resampling.HAMMING,
            "bicubic": Image.Resampling.BICUBIC,
            "lanczos": Image.Resampling.LANCZOS,
        }

        pil_resampling_method = resampling_methods.get(resampling_method.lower(), Image.Resampling.BILINEAR)

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
            resized_image = current_image.resize((new_width, new_height), pil_resampling_method)

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

class CustomDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Droste Effect Parameters")

        # Shrink Factor
        tk.Label(self, text="Shrink Factor (0.01 to 1.00):").pack()
        self.shrink_factor_entry = tk.Entry(self)
        self.shrink_factor_entry.insert(0, "0.95")
        self.shrink_factor_entry.pack()

        # Max Iterations
        tk.Label(self, text="Max Iterations:").pack()
        self.max_iterations_entry = tk.Entry(self)
        self.max_iterations_entry.insert(0, "100")
        self.max_iterations_entry.pack()

        # Save Timelapse with combobox
        tk.Label(self, text="Save Timelapse:").pack()
        self.save_timelapse_var = tk.StringVar()
        self.save_timelapse_entry = ttk.Combobox(self, textvariable=self.save_timelapse_var, values=["yes", "no"], state="readonly")
        self.save_timelapse_entry.set("yes")  # Default value
        self.save_timelapse_entry.pack()

        # FPS
        tk.Label(self, text="FPS for Timelapse:").pack()
        self.fps_entry = tk.Entry(self)
        self.fps_entry.insert(0, "20")
        self.fps_entry.pack()
        
        # Include Reverse with combobox
        tk.Label(self, text="Include Reverse in Video:").pack()
        self.include_reverse_var = tk.StringVar()
        self.include_reverse_entry = ttk.Combobox(self, textvariable=self.include_reverse_var, values=["yes", "no"], state="readonly")
        self.include_reverse_entry.set("no")  # Default value
        self.include_reverse_entry.pack()

        # Save Reversed Clip with combobox
        tk.Label(self, text="Save Reversed Clip:").pack()
        self.save_reversed_clip_var = tk.StringVar()
        self.save_reversed_clip_entry = ttk.Combobox(self, textvariable=self.save_reversed_clip_var, values=["yes", "no"], state="readonly")
        self.save_reversed_clip_entry.set("yes")  # Default value
        self.save_reversed_clip_entry.pack()

        # Resampling Method with combobox
        tk.Label(self, text="Resampling Method:").pack()
        resampling_methods = ["Nearest", "Box", "Bilinear", "Hamming", "Bicubic", "Lanczos"]
        self.resampling_method_var = tk.StringVar()
        self.resampling_method_entry = ttk.Combobox(self, textvariable=self.resampling_method_var, values=resampling_methods, state="readonly")
        self.resampling_method_entry.set("Bilinear")  # Default value
        self.resampling_method_entry.pack()

        # Rotation Angle
        tk.Label(self, text="Rotation Angle:").pack()
        self.rotation_angle_entry = tk.Entry(self)
        self.rotation_angle_entry.insert(0, "5")
        self.rotation_angle_entry.pack()

        # Output Format with combobox
        tk.Label(self, text="Output Format:").pack()
        formats = ["png", "jpg", "jpeg", "bmp", "webp"]
        self.output_format_var = tk.StringVar()
        self.output_format_entry = ttk.Combobox(self, textvariable=self.output_format_var, values=formats, state="readonly")
        self.output_format_entry.set("png")  # Default value
        self.output_format_entry.pack()

        # Submit Button
        self.submit_button = tk.Button(self, text="Submit", command=self.on_submit)
        self.submit_button.pack()

        self.result = None

    def on_submit(self):
        try:
            # Shrink Factor Validation
            shrink_factor_str = self.shrink_factor_entry.get()
            if not shrink_factor_str:
                raise ValueError("Shrink factor is required.")
            shrink_factor = float(shrink_factor_str)
            if not (0 < shrink_factor <= 1):
                raise ValueError("Shrink factor must be between 0.01 and 1.00")

            # Max Iterations Validation
            max_iterations_str = self.max_iterations_entry.get()
            if not max_iterations_str:
                raise ValueError("Max iterations is required.")
            max_iterations = int(max_iterations_str)
            if max_iterations <= 0:
                raise ValueError("Max iterations must be a positive integer")

            # Save Timelapse Validation
            save_timelapse_str = self.save_timelapse_entry.get().lower()
            if save_timelapse_str not in ['yes', 'no', 'true', 'false']:
                raise ValueError("Invalid input for save timelapse. Please enter 'yes' or 'no'.")
            save_timelapse = save_timelapse_str in ['yes', 'true']

            # FPS Validation
            fps_str = self.fps_entry.get()
            if save_timelapse and not fps_str:
                raise ValueError("FPS is required for timelapse.")
            fps = int(fps_str) if fps_str else 10  # Default to 10 if not provided
            if fps <= 0:
                raise ValueError("FPS must be a positive integer.")

            # Include Reverse Validation
            include_reverse_str = self.include_reverse_entry.get().lower()
            if include_reverse_str not in ['yes', 'no', 'true', 'false']:
                raise ValueError("Invalid input for include reverse. Please enter 'yes' or 'no'.")
            include_reverse = include_reverse_str in ['yes', 'true']
            if not save_timelapse and include_reverse:
                raise ValueError("Cannot include reverse in video without saving timelapse.")

            # Save Reversed Clip Validation
            save_reversed_clip_str = self.save_reversed_clip_entry.get().lower()
            if save_reversed_clip_str not in ['yes', 'no', 'true', 'false']:
                raise ValueError("Invalid input for save reversed clip. Please enter 'yes' or 'no'.")
            save_reversed_clip = save_reversed_clip_str in ['yes', 'true']
            if not save_timelapse and save_reversed_clip:
                raise ValueError("Cannot save reversed clip without saving timelapse.")

            # Resampling Method Validation
            resampling_method = self.resampling_method_entry.get().lower()
            valid_resampling_methods = ['Nearest', 'Box', 'Bilinear', 'Hamming', 'Bicubic', 'Lanczos']
            if resampling_method not in valid_resampling_methods:
                raise ValueError(f"Invalid resampling method. Choose from {', '.join(valid_resampling_methods)}.")

            # Rotation Angle Validation
            rotation_angle_str = self.rotation_angle_entry.get()
            if not rotation_angle_str:
                raise ValueError("Rotation angle is required.")
            rotation_angle = float(rotation_angle_str)
            if not (-360 <= rotation_angle <= 360):
                raise ValueError("Rotation angle must be between -360 and 360 degrees")

            # Output Format Validation
            output_format = self.output_format_entry.get().lower()
            valid_formats = ['png', 'jpg', 'jpeg', 'bmp', 'webp']
            if output_format not in valid_formats:
                raise ValueError(f"Invalid output format. Choose from {', '.join(valid_formats)}.")

            self.result = {
                'shrink_factor': shrink_factor,
                'max_iterations': max_iterations,
                'save_timelapse': save_timelapse,
                'fps': fps,
                'include_reverse': include_reverse,
                'save_reversed_clip': save_reversed_clip,
                'resampling_method': resampling_method,
                'rotation_angle': rotation_angle,
                'output_format': output_format
            }
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))

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
                print("No file selected. Exiting the program.")
                sys.exit(0)

            dialog = CustomDialog(root)
            root.wait_window(dialog)

            if dialog.result:
                # Unpack the result and call the processing function
                result = dialog.result
                shrink_factor = result['shrink_factor']
                max_iterations = result['max_iterations']
                save_timelapse = result['save_timelapse']
                fps = result['fps']
                include_reverse = result['include_reverse']
                save_reversed_clip = result['save_reversed_clip']
                resampling_method = result['resampling_method']
                rotation_angle = result['rotation_angle']
                output_format = result['output_format']

                # Generate the unique suffix and output paths
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                base_filename = os.path.splitext(os.path.basename(file_path))[0]
                unique_suffix = f"{base_filename}_{timestamp}"
                output_image_path = f"output_{unique_suffix}.{output_format}"
                timelapse_video_path = f"time_lapse_{unique_suffix}.mp4" if save_timelapse else None
                reversed_clip_path = f"reversed_clip_{unique_suffix}.mp4" if save_reversed_clip else None

                # Call the image processing function with the updated paths
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
            else:
                print("Operation cancelled by the user. Exiting the program.")

        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
