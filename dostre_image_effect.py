import datetime
import os
import tempfile
import tkinter as tk
import traceback
from tkinter import filedialog, simpledialog

from PIL import Image
from moviepy.editor import ImageSequenceClip, concatenate_videoclips, vfx

def create_dostre_image_effect(image_path, output_path, shrink_factor, max_iterations, save_timelapse, fps, include_reverse, timelapse_video_path, reversed_clip_path, save_reversed_clip, unique_suffix, resampling_method, frame_format, rotation_angle):
    try:
        # Load the original image
        original_image = Image.open(image_path)

        # Convert to 'RGBA' for transparency support
        if original_image.mode != 'RGBA':
            original_image = original_image.convert('RGBA')

        current_image = original_image.copy()
        current_size = original_image.size
        total_rotation = 0  # Initialize total rotation

        # Create a temporary directory to store frames
        with tempfile.TemporaryDirectory() as temp_dir:
            frame_paths = []

            # Save the original image as the first frame
            frame_path = os.path.join(temp_dir, f"frame_0.{frame_format}")
            original_image.save(frame_path)
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
                original_image.save(frame_path)
                frame_paths.append(frame_path)

            # Save the final image, consider PNG for lossless output
            original_image.save(output_path, quality=100)
            print("Image processing complete.")

            # Create the time-lapse video if required
            if save_timelapse:
                create_timelapse_video(frame_paths, timelapse_video_path, fps, include_reverse)
                print(f"Time-lapse video saved as {timelapse_video_path}")

                # Create the reversed clip if required and save it separately
                if save_reversed_clip:
                    reversed_clip_path = f"reversed_clip_{unique_suffix}.mp4"
                    create_timelapse_video(frame_paths[::-1], reversed_clip_path, fps, False)
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
    except Exception as e:
        print(f"An error occurred during video creation: {e}")
        traceback.print_exc()

def main():
    try:
        # Set up a root window for the file dialog (but don't display it)
        root = tk.Tk()
        root.withdraw()

        # Notify user to be patient
        print("Please select an image file. This may take a few moments...")

        # Open a file dialog to select an image
        file_path = filedialog.askopenfilename(title="Select an Image", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])
        if not file_path:
            raise ValueError("No file selected. Exiting the program.")

        # Get parameters from the user

        # Shrink factor determines how much each iteration of the image is reduced in size.
        # A smaller shrink factor means the image shrinks more with each iteration.
        # For example, a shrink factor of 0.99 reduces the image size by 1% each time.
        shrink_factor = simpledialog.askfloat("Input", "Enter shrink factor (e.g., 0.99):", parent=root, minvalue=0.01, maxvalue=1.00)

        # Max iterations sets the number of times the image will be shrunk and pasted onto itself.
        # A higher number of iterations means more repetitions of the shrinking and pasting process.
        max_iterations = simpledialog.askinteger("Input", "Enter maximum iterations (e.g., 100):", parent=root, minvalue=1)

        # This parameter allows the user to choose whether to save a timelapse video of the image processing.
        # Responding 'yes' will save a video showing each iteration of the process.
        save_timelapse = simpledialog.askstring("Input", "Save timelapse video? (yes/no):", parent=root).lower() == 'yes'

        # FPS (Frames Per Second) for the timelapse video.
        # This determines how many frames are shown per second in the timelapse video.
        # A higher FPS results in a smoother video.
        fps = None

        # This variable controls whether the reversed clip is included in the timelapse video.
        # Including the reversed clip creates a seamless loop effect in the video.
        include_reverse = False
        save_reversed_clip = False

        if save_timelapse:
            # Ask the user for the FPS value if they have chosen to save a timelapse video.
            fps = simpledialog.askinteger("Input", "Enter FPS for timelapse (e.g., 10):", parent=root, minvalue=1)
            # Ask the user if they want to include the reversed clip in the timelapse video.
            # A 'yes' response will result in the timelapse video showing the image sequence forwards and then in reverse.
            include_reverse = simpledialog.askstring("Input", "Include reversed clip in video? (yes/no):", parent=root).lower() == 'yes'

            # Ask the user if they want to save the reversed clip by itself
            save_reversed_clip = simpledialog.askstring("Input", "Save reversed clip by itself? (yes/no):", parent=root).lower() == 'yes'

        # Image Resampling Method
        resampling_options = ['NEAREST', 'BOX', 'BILINEAR', 'HAMMING', 'BICUBIC', 'LANCZOS']
        resampling_method = simpledialog.askstring("Input", f"Enter Image Resampling Method (choose from {', '.join(resampling_options)}):", parent=root).upper()

        # Frame Format
        frame_format_options = ['png', 'jpg', 'jpeg', 'bmp']
        frame_format = simpledialog.askstring("Input", f"Enter Frame Format (choose from {', '.join(frame_format_options)}):", parent=root).lower()

        rotation_angle = simpledialog.askfloat("Input", "Enter rotation angle per iteration (e.g., 10):", parent=root)

        # Validate user input for Image Resampling Method
        if resampling_method not in resampling_options:
            raise ValueError(f"Invalid resampling method. Please choose from {', '.join(resampling_options)}.")

        # Validate user input for Frame Format
        if frame_format not in frame_format_options:
            raise ValueError(f"Invalid frame format. Please choose from {', '.join(frame_format_options)}.")

        # Get the base filename without extension
        base_filename = os.path.splitext(os.path.basename(file_path))[0]
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_suffix = f"{base_filename}_{timestamp}"
        output_image_path = f"output_{unique_suffix}.{frame_format}"
        timelapse_video_path = f"time_lapse_{unique_suffix}.mp4" if save_timelapse else None
        reversed_clip_path = f"reversed_clip_{unique_suffix}.mp4" if save_reversed_clip else None

        # Create the recursive mirror effect
        create_dostre_image_effect(
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
