import argparse
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
        traceback.print_exc()

def process_image_for_droste_effect(image_path, temp_dir, shrink_factor, max_iterations, resampling_method, rotation_angle):
    frame_paths = []
    frame_format = 'bmp'
    try:
        # Load the original image
        original_image = Image.open(image_path).convert('RGBA')

        current_image = original_image.copy()
        current_size = original_image.size
        total_rotation = 0

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

        for iteration in range(max_iterations):
            print(f"Processing iteration {iteration}...")

            # Break the loop if the new size is too small
            if current_size[0] <= 1 or current_size[1] <= 1:
                print("Terminating process: Image has become too small to process any further.")
                break

            # Resize and rotate the image
            resized_image = current_image.resize((int(current_size[0] * shrink_factor), int(current_size[1] * shrink_factor)), pil_resampling_method)
            total_rotation = (total_rotation + rotation_angle) % 360
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
            current_size = (int(current_size[0] * shrink_factor), int(current_size[1] * shrink_factor))

            # Save the frame
            frame_path = os.path.join(temp_dir, f"frame_{iteration}.{frame_format}")
            if not save_image_with_format(original_image, frame_path, frame_format):
                print(f"Failed to save frame {iteration}.")
                return [], None
            frame_paths.append(frame_path)

        return frame_paths, original_image
    except Exception as e:
        print(f"Error in processing image for Droste effect: {e}")
        traceback.print_exc()
        return [], None

def create_videos(frame_paths, timelapse_video_path, reversed_clip_path, fps, include_reverse, save_reversed):
    start_time = time.time()
    if not frame_paths:
        return False

    try:
        if not create_timelapse_video(frame_paths, timelapse_video_path, fps, include_reverse):
            print("Failed to create the time-lapse video.")
            return False

        if save_reversed and not create_timelapse_video(frame_paths[::-1], reversed_clip_path, fps, False):
            print("Failed to create the reversed clip.")
            return False

        end_time = time.time()
        print(f"Video creation completed in {end_time - start_time:.2f} seconds.")
        return True
    except Exception as e:
        print(f"Error in video creation: {e}")
        traceback.print_exc()
        return False

def create_droste_image_effect(image_path, output_path, shrink_factor, max_iterations, save_timelapse, fps, include_reverse, timelapse_video_path, reversed_clip_path, save_reversed, resampling_method, rotation_angle, output_format):
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
        if save_timelapse or save_reversed:
            if not create_videos(frame_paths, timelapse_video_path, reversed_clip_path, fps, include_reverse, save_reversed):
                print("Failed to create videos.")
            else:
                if save_timelapse:
                    print(f"Time-lapse video saved as {timelapse_video_path}")
                if save_reversed:
                    print(f"Reversed clip saved as {reversed_clip_path}")

        # Display the chosen parameters
        print("\nChosen Parameters:")
        print(f"Shrink Factor: {shrink_factor}")
        print(f"Max Iterations: {max_iterations}")
        print(f"Save Timelapse: {save_timelapse}")
        if save_timelapse:
            print(f"FPS for Timelapse: {fps}")
            print(f"Include Reverse: {include_reverse}")
            print(f"Save Reversed Clip: {save_reversed}")
        print(f"Image Resampling Method: {resampling_method}")
        print(f"Rotation Angle: {rotation_angle}")

    except Exception as e:
        print(f"An error occurred during image processing: {e}")
        traceback.print_exc()
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
        traceback.print_exc()
        return False

def create_timelapse_video(frame_paths, output_filename, fps, include_reverse):
    try:
        # Create a clip from the frames
        clip = ImageSequenceClip(frame_paths, fps=fps)

        # If reverse video is included, create and concatenate it
        if include_reverse:
            reversed_clip = clip.fx(vfx.time_mirror)
            final_clip = concatenate_videoclips([clip, reversed_clip])
        else:
            final_clip = clip

        # Write the final clip to a file
        final_clip.write_videofile(output_filename, codec='libx264', threads=4)
    except Exception as e:
        print(f"An error occurred during video creation: {e}")
        traceback.print_exc()
        return False
    finally:
        # Close the clip to release resources
        clip.close()
        if include_reverse:
            reversed_clip.close()
        final_clip.close()

    return True

def validate_parameters(image_path, shrink_factor_str, max_iterations_str, save_timelapse_str, fps_str, include_reverse_str, save_reversed_str, resampling_method, rotation_angle_str, output_format, output_path, is_output_format_provided):
    # Helper function to parse boolean strings
    def parse_bool(value):
        if value.lower() not in ['yes', 'no', 'true', 'false']:
            raise ValueError(f"Invalid input for boolean value. Please enter 'yes', 'no', 'true', or 'false'. Received: {value}")
        return value.lower() in ['yes', 'true']

    # Check for None values in required parameters
    required_params = {
        'shrink_factor': shrink_factor_str, 
        'max_iterations': max_iterations_str, 
        'resampling_method': resampling_method, 
        'rotation_angle': rotation_angle_str, 
        'output_format': output_format
    }
    for param_name, param_value in required_params.items():
        if param_value is None:
            raise ValueError(f"{param_name} is a required parameter and cannot be None.")

    # Image Path Validation
    valid_image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.webp']
    if not os.path.isfile(image_path):
        raise ValueError(f"The specified image path does not exist or is not a file: {image_path}")
    _, image_ext = os.path.splitext(image_path)
    if image_ext.lower() not in valid_image_extensions:
        raise ValueError(f"The file extension of the image is not supported. Supported extensions are: {', '.join(valid_image_extensions)}.")

    # Shrink Factor Validation
    shrink_factor = parse_float(shrink_factor_str, "Shrink factor")
    if not (0 < shrink_factor <= 0.99):
        raise ValueError("Shrink factor must be between 0.01 and 0.99")

    # Max Iterations Validation
    max_iterations = parse_int(max_iterations_str, "Max iterations")
    if max_iterations <= 0:
        raise ValueError("Max iterations must be a positive integer")

    # Timelapse, FPS, Include Reverse, and Save Reversed Validation
    save_timelapse = parse_bool(save_timelapse_str)
    include_reverse = parse_bool(include_reverse_str)
    save_reversed = parse_bool(save_reversed_str)

    if save_timelapse:
        fps = parse_int(fps_str, "FPS")
        if fps <= 0:
            raise ValueError("FPS must be a positive integer.")
    else:
        fps = 10

    if not save_timelapse and (include_reverse or save_reversed):
        raise ValueError("Cannot include reverse or save reversed clip in video without saving timelapse.")

    # Resampling Method Validation
    valid_resampling_methods = ['nearest', 'box', 'bilinear', 'hamming', 'bicubic', 'lanczos']
    if resampling_method.lower() not in valid_resampling_methods:
        raise ValueError(f"Invalid resampling method. Choose from {', '.join(valid_resampling_methods)}.")

    # Rotation Angle Validation
    rotation_angle = parse_float(rotation_angle_str, "Rotation angle")
    if not (-360 <= rotation_angle <= 360):
        raise ValueError("Rotation angle must be between -360 and 360 degrees")

    # Output Format Validation
    valid_formats = ['png', 'jpg', 'jpeg', 'bmp', 'webp']
    if output_format.lower() not in valid_formats:
        raise ValueError(f"Invalid output format. Choose from {', '.join(valid_formats)}.")

    # Output Path Validation
    if output_path and not os.path.isdir(output_path):
        raise ValueError(f"The specified output path is not a directory: {output_path}")

    return {
        'shrink_factor': shrink_factor,
        'max_iterations': max_iterations,
        'save_timelapse': save_timelapse,
        'fps': fps,
        'include_reverse': include_reverse,
        'save_reversed': save_reversed,
        'resampling_method': resampling_method.lower(),
        'rotation_angle': rotation_angle,
        'output_format': output_format
    }

# Helper functions for parsing float and int values
def parse_float(value_str, param_name):
    try:
        return float(value_str)
    except ValueError:
        raise ValueError(f"{param_name} must be a valid floating-point number.")

def parse_int(value_str, param_name):
    try:
        return int(value_str)
    except ValueError:
        raise ValueError(f"{param_name} must be a valid integer.")

class CustomDialog(tk.Toplevel):
    def __init__(self, parent, file_path):
        super().__init__(parent)
        self.file_path = file_path
        self.title("Droste Effect Parameters")
        self.create_widgets()
        self.result = None

    def create_widgets(self):
        # Grid layout for better alignment and spacing
        self.grid_columnconfigure(1, weight=1)
        row = 0

        # Helper function to create labeled entry or combobox
        def create_labeled_input(label, input_type, options=None, default=None):
            nonlocal row
            tk.Label(self, text=label).grid(row=row, column=0, sticky='w', padx=5, pady=5)
            if input_type == 'entry':
                widget = tk.Entry(self)
                if default is not None:
                    widget.insert(0, default)
            elif input_type == 'combobox':
                var = tk.StringVar()
                widget = ttk.Combobox(self, textvariable=var, values=options, state="readonly")
                if default is not None:
                    widget.set(default)
            widget.grid(row=row, column=1, sticky='ew', padx=5, pady=5)
            row += 1
            return widget

        self.shrink_factor_entry = create_labeled_input("Shrink Factor (0.01 to 1.00):", 'entry', default="0.95")
        self.max_iterations_entry = create_labeled_input("Max Iterations:", 'entry', default="100")
        self.save_timelapse_entry = create_labeled_input("Save Timelapse:", 'combobox', options=["yes", "no"], default="yes")
        self.fps_entry = create_labeled_input("FPS for Timelapse:", 'entry', default="20")
        self.include_reverse_entry = create_labeled_input("Include Reverse in Video:", 'combobox', options=["yes", "no"], default="no")
        self.save_reversed_entry = create_labeled_input("Save Reversed Clip:", 'combobox', options=["yes", "no"], default="yes")
        self.resampling_method_entry = create_labeled_input("Resampling Method:", 'combobox', options=["Nearest", "Box", "Bilinear", "Hamming", "Bicubic", "Lanczos"], default="Bilinear")
        self.rotation_angle_entry = create_labeled_input("Rotation Angle:", 'entry', default="5")
        self.output_format_entry = create_labeled_input("Output Format:", 'combobox', options=["png", "jpg", "jpeg", "bmp", "webp"], default="png")
        # Creating a frame to hold the output path entry and browse button
        output_path_frame = tk.Frame(self)
        output_path_frame.grid(row=row, column=1, sticky='ew', padx=5, pady=5)
        self.output_path_entry = tk.Entry(output_path_frame)
        self.output_path_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Browse button placed inside the frame, next to the output path entry
        self.browse_button = tk.Button(output_path_frame, text="...", command=self.browse_output_path, width=3)
        self.browse_button.pack(side=tk.LEFT, padx=(0, 5))

        # Label for the output path
        tk.Label(self, text="Output Path: (Leave Empty for Script's Directory)").grid(row=row, column=0, sticky='w', padx=5, pady=5)

        row += 1

        self.submit_button = tk.Button(self, text="Submit", command=self.on_submit)
        self.submit_button.grid(row=row, column=0, columnspan=2, padx=5, pady=5)

    def browse_output_path(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_path_entry.delete(0, tk.END)
            self.output_path_entry.insert(0, directory)

    def update_gui_defaults(self, command_line_args):
        self.shrink_factor_entry.delete(0, tk.END)
        self.shrink_factor_entry.insert(0, str(command_line_args.shrink_factor))

        self.max_iterations_entry.delete(0, tk.END)
        self.max_iterations_entry.insert(0, str(command_line_args.max_iterations))

        self.save_timelapse_entry.set("yes" if command_line_args.save_timelapse else "no")
        self.fps_entry.delete(0, tk.END)
        self.fps_entry.insert(0, str(command_line_args.fps))

        self.include_reverse_entry.set("yes" if command_line_args.include_reverse else "no")
        self.save_reversed_entry.set("yes" if command_line_args.save_reversed else "no")

        self.resampling_method_entry.set(command_line_args.resampling_method.capitalize())
        self.rotation_angle_entry.delete(0, tk.END)
        self.rotation_angle_entry.insert(0, str(command_line_args.rotation_angle))

        self.output_format_entry.set(command_line_args.output_format.lower())

        if command_line_args.output_path:
            self.output_path_entry.delete(0, tk.END)
            self.output_path_entry.insert(0, command_line_args.output_path)

    def on_submit(self):
        try:
            # Collecting input values as strings
            shrink_factor_str = self.shrink_factor_entry.get()
            max_iterations_str = self.max_iterations_entry.get()
            save_timelapse_str = self.save_timelapse_entry.get().lower()
            fps_str = self.fps_entry.get()
            include_reverse_str = self.include_reverse_entry.get().lower()
            save_reversed_str = self.save_reversed_entry.get().lower()
            resampling_method = self.resampling_method_entry.get()
            rotation_angle_str = self.rotation_angle_entry.get().lower()
            output_format = self.output_format_entry.get().lower()

            output_path = self.output_path_entry.get().strip()
            is_output_format_provided = False
            
            # Validate and process the parameters
            validated_params = validate_parameters(
                self.file_path,
                shrink_factor_str, max_iterations_str, save_timelapse_str, fps_str,
                include_reverse_str, save_reversed_str, resampling_method,
                rotation_angle_str, output_format, output_path,
                is_output_format_provided
            )

            # If validation is successful, set the result
            self.result = validated_params
            self.result['output_path'] = output_path
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))

def main():
    # Command-line argument parsing
    parser = argparse.ArgumentParser(description="Create Droste Image Effect")
    parser.add_argument("--image_path", help="Path to the input image")
    parser.add_argument("--shrink_factor", type=float, help="Shrink factor for the image", default=0.95)
    parser.add_argument("--max_iterations", type=int, help="Maximum number of iterations", default=100)
    parser.add_argument("--save_timelapse", type=lambda x: (str(x).lower() in ['yes', 'true']), help="Save timelapse video (yes/true or no/false)", default=True)
    parser.add_argument("--fps", type=int, help="Frames per second for timelapse video", default=10)
    parser.add_argument("--include_reverse", type=lambda x: (str(x).lower() in ['yes', 'true']), help="Include reversed clip in video (yes/true or no/false)", default=False)
    parser.add_argument("--save_reversed", type=lambda x: (str(x).lower() in ['yes', 'true']), help="Save reversed clip by itself (yes/true or no/false)", default=True)
    parser.add_argument("--resampling_method", help="Image Resampling Method", default='Bilinear')
    parser.add_argument("--rotation_angle", type=float, help="Rotation angle per iteration", default=0.0)
    parser.add_argument("--output_format", help="Format for the output image", choices=['png', 'jpg', 'jpeg', 'bmp', 'webp'], default='bmp')
    parser.add_argument("--output_path", help="Path for the output files", default="")

    args = parser.parse_args()

    # Determine if output_format was explicitly provided by the user
    is_output_format_provided = '--output_format' in sys.argv

    if args.image_path:
        # Command-line mode
        try:
            # Convert command-line arguments to strings for validation
            validated_params = validate_parameters(
            args.image_path,
            str(args.shrink_factor), str(args.max_iterations), str(args.save_timelapse),
            str(args.fps), str(args.include_reverse), str(args.save_reversed),
            args.resampling_method, str(args.rotation_angle), args.output_format, args.output_path,
            is_output_format_provided
            )

            # Extract validated parameters
            shrink_factor = validated_params['shrink_factor']
            max_iterations = validated_params['max_iterations']
            save_timelapse = validated_params['save_timelapse']
            fps = validated_params['fps']
            include_reverse = validated_params['include_reverse']
            save_reversed = validated_params['save_reversed']
            resampling_method = validated_params['resampling_method']
            rotation_angle = validated_params['rotation_angle']
            output_format = validated_params['output_format']

            # Handle the output directory
            if args.output_path:
                if not os.path.isdir(args.output_path):
                    raise ValueError(f"The specified output path is not a directory: {args.output_path}")
                output_base_path = os.path.join(args.output_path, os.path.splitext(os.path.basename(args.image_path))[0])
            else:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                base_filename = os.path.splitext(os.path.basename(args.image_path))[0]
                output_base_path = os.path.join(os.getcwd(), f"{base_filename}_{timestamp}")

            output_image_path = f"{output_base_path}.{args.output_format}"
            timelapse_video_path = f"{output_base_path}_timelapse.mp4" if args.save_timelapse else None
            reversed_clip_path = f"{output_base_path}_reversed.mp4" if args.save_reversed else None

            # Call the image processing function with the updated paths
            create_droste_image_effect(
                args.image_path, output_image_path, shrink_factor, max_iterations,
                save_timelapse, fps, include_reverse, timelapse_video_path,
                reversed_clip_path, save_reversed,
                resampling_method, rotation_angle, output_format
            )
        except ValueError as e:
            print(e)
            sys.exit(1)
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

            dialog = CustomDialog(root, file_path)
            dialog.update_gui_defaults(args)
            root.wait_window(dialog)

            if dialog.result:
                # Unpack the result and call the processing function
                result = dialog.result

                # Use the provided output path if available, otherwise default to the current working directory
                output_base_path = result.get('output_path', os.getcwd())
                if output_base_path and not os.path.exists(output_base_path):
                    os.makedirs(output_base_path)

                # Generate filenames for the output files
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                base_filename = os.path.splitext(os.path.basename(file_path))[0]
                final_output_base = os.path.join(output_base_path, f"{base_filename}_{timestamp}")

                output_image_path = f"{final_output_base}.{result['output_format']}"
                timelapse_video_path = f"{final_output_base}_timelapse.mp4" if result['save_timelapse'] else None
                reversed_clip_path = f"{final_output_base}_reversed.mp4" if result['save_reversed'] else None

                create_droste_image_effect(
                    file_path, output_image_path, result['shrink_factor'], result['max_iterations'],
                    result['save_timelapse'], result['fps'], result['include_reverse'], timelapse_video_path,
                    reversed_clip_path, result['save_reversed'],
                    result['resampling_method'], result['rotation_angle'], result['output_format']
                )
                print(f"Image saved as {output_image_path}")
                if result['save_timelapse']:
                    print(f"Time-lapse video saved as {timelapse_video_path}")
                if result['save_reversed']:
                    print(f"Reversed clip saved as {reversed_clip_path}")
            else:
                print("Operation cancelled by the user. Exiting the program.")
                sys.exit(0)

        except Exception as e:
            print(f"An error occurred: {e}")
            traceback.print_exc()
            sys.exit(1)

if __name__ == "__main__":
    main()