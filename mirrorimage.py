from PIL import Image
import tkinter as tk
from tkinter import filedialog, simpledialog
import os
from moviepy.editor import ImageSequenceClip
import tempfile

def create_recursive_mirror_effect(image_path, output_path, shrink_factor, max_iterations, save_timelapse, fps):
    try:
        # Load the original image
        original_image = Image.open(image_path)

        # Convert to 'RGB' if the image is not in 'RGB' mode
        if original_image.mode != 'RGB':
            original_image = original_image.convert('RGB')

        current_image = original_image.copy()
        current_size = original_image.size

        # Create a temporary directory to store frames
        with tempfile.TemporaryDirectory() as temp_dir:
            frame_paths = []

            for iteration in range(max_iterations):
                print(f"Processing iteration {iteration + 1}...")

                # Calculate the new size
                new_width = int(current_size[0] * shrink_factor)
                new_height = int(current_size[1] * shrink_factor)

                # Break the loop if the new size is too small
                if new_width <= 0 or new_height <= 0:
                    print("Image has become too small to process further.")
                    break

                # Resize the image with high-quality resampling
                resized_image = current_image.resize((new_width, new_height), Image.Resampling.LANCZOS)

                # Calculate the position to paste the resized image
                paste_x = (original_image.size[0] - new_width) // 2
                paste_y = (original_image.size[1] - new_height) // 2

                # Paste the resized image onto the original image, centered
                original_image.paste(resized_image, (paste_x, paste_y))

                # Update the current size for the next iteration
                current_size = (new_width, new_height)

                # Save the frame
                frame_path = os.path.join(temp_dir, f"frame_{iteration}.png")
                original_image.save(frame_path)
                frame_paths.append(frame_path)

            # Save the final image, consider PNG for lossless output
            original_image.save(output_path, quality=100)
            print("Image processing complete.")

            # Create the time-lapse video if required
            if save_timelapse:
                timelapse_output_filename = "time_lapse.mp4"
                create_timelapse_video(frame_paths, timelapse_output_filename, fps)
                print(f"Time-lapse video saved as {timelapse_output_filename}")
    except Exception as e:
        print(f"An error occurred during image processing: {e}")

def create_timelapse_video(frame_paths, output_filename, fps):
    try:
        # Create a clip from the frames
        clip = ImageSequenceClip(frame_paths, fps=fps)
        # Write the clip to a file
        clip.write_videofile(output_filename, codec='libx264')
    except Exception as e:
        print(f"An error occurred during video creation: {e}")

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
            print("No file selected.")
            return

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
        fps = simpledialog.askinteger("Input", "Enter FPS for timelapse (e.g., 10):", parent=root, minvalue=1)


        # Define the output path (same as script's directory)
        output_path = "output_image.png"  # Changed to PNG

        # Create the recursive mirror effect
        create_recursive_mirror_effect(file_path, output_path, shrink_factor, max_iterations, save_timelapse, fps)
        print(f"Image saved as {output_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
