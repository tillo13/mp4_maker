import os
import datetime
import shutil
import requests
from openai_utils import create_image
import mp4_maker_engine
import glob

#====GLOBAL VARIABLES====#
CHARACTER_DESCRIPTION = """
This image is a stylized, cartoonish depiction of a watermelon that is merged with a hippo.

- Shape: The subject has a cube-like structure, resembling a boxy, three-dimensional head.
- Base Color: Mainly a vibrant green with darker green stripes to mimic the pattern of a watermelon's exterior.
- Eyes: Two large, white circles with smaller black circles in the center, representing cartoony eyes. They are set wide apart on the front of the face.
- Nose: The nose is not distinctly separated but implied by a simple triangular green shape with rounded edges, sitting above the mouth area.
- Mouth: A bright red semi-circular shape with small black seeds, resembling a slice of watermelon. This forms the smiling mouth of the character.
- Ears: Two bright red, oval shapes protruding from the top corners, giving the impression of exaggerated, simplistic ears.
- Cheeks: Two lighter green circular patches on each cheek, below the eyes, adding to the cutesy animal-like appearance.

"""

STORYLINE_DESCRIPTION = """
The hippomelon is very engaged in this exact activity:
"""

GPT_IMAGE_DESCRIPTION = [
    "The hippolemon wakes up bright and early",
    "The hippomelon eats cheerios for breakfast",
    "THe hippomelon reads the newspaper",
    "The hippomelon gets excited about a news story talking about the sun shining",
    "The hippomelon plays at the park.",
    "The hippomelon goes home and falls asleep on his couch.",
    "The hippomelon is startled by a loud noise outside his house.",
    "The hippomelon is scared."

]

VIDEO_CAPTIONS = [
    "Hippomelon wakes up energized...",
    "Hippomelon eats his favorite breakfast...",
    "Hippomelon reads the newspaper...",
    "What's this?  Sunshine today?",
    "Hippomelon goes to the park...",
    "Hippo is tired, and takes a nap...",
    "Hippomelon hears a loud noise...",
    "What should hippomelon do now?"

]

IMAGE_SIZE = "1024x1024"
MODEL_NAME = "dall-e-3"
IMAGE_QUALITY = "hd"
IMAGE_STYLE = "vivid"
USER_ID = "unique_user_identifier"

VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1080
FONT_SIZE = 36
FONT_COLOR = 'white'
CAPTION_OFFSET_Y = '0.10*h'
DISPLAY_DURATION_PER_IMAGE = 4
AUDIO_TRACK_TYPE = 'halloween'
OUTPUT_FILENAME_PATTERN = 'output_with_captions'

def download_image(url, dest_folder, filename):
    response = requests.get(url)
    if response.status_code == 200:
        with open(os.path.join(dest_folder, filename), 'wb') as f:
            f.write(response.content)
    else:
        print(f"Error downloading {url}: Status code {response.status_code}")

def archive_existing_images(base_directory):
    image_files = [f for f in os.listdir(base_directory) if f.endswith((".png", ".jpg", ".jpeg"))]
    
    if image_files:
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        archive_directory = os.path.join(base_directory, f"{timestamp}_images")
        os.makedirs(archive_directory, exist_ok=True)
        print(f"Archiving existing images to {archive_directory}")

        for filename in image_files:
            old_path = os.path.join(base_directory, filename)
            new_path = os.path.join(archive_directory, filename)
            shutil.move(old_path, new_path)
            print(f"Moved {filename} to archive.")
    else:
        print("No existing images to archive. The directory is clean.")


def get_image_files(folder_path):
    image_extensions = ('.jpg', '.png', '.jpeg')
    return sorted(
        [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith(image_extensions)],
        key=lambda x: os.path.basename(x).lower()
    )

def main():
    working_directory = os.path.join(os.getcwd(), 'video_images')
    archive_existing_images(working_directory)
    os.makedirs(working_directory, exist_ok=True)

    # Generate images
    for i, image_description in enumerate(GPT_IMAGE_DESCRIPTION):
        # Add CHARACTER_DESCRIPTION and STORYLINE_DESCRIPTION to the prompt
        image_prompt = f"{CHARACTER_DESCRIPTION.strip()} {STORYLINE_DESCRIPTION.strip()} {image_description.strip()}"

        image_response = create_image(
            prompt=image_prompt,
            model=MODEL_NAME,
            n=1,
            quality=IMAGE_QUALITY,
            response_format="url",
            size=IMAGE_SIZE,
            style=IMAGE_STYLE,
            user_id=USER_ID
        )

        if 'data' in image_response:
            image_url = image_response['data'][0]['url']
            filename = f"image_{i:04d}.png"  # Ensure files are named sequentially
            download_image(image_url, working_directory, filename)

    # Verify that the number of generated images equals the number of descriptions
    generated_image_files = get_image_files(working_directory)
    if len(GPT_IMAGE_DESCRIPTION) != len(generated_image_files):
        print(f"The number of generated images ({len(generated_image_files)}) does not match the number of descriptions ({len(GPT_IMAGE_DESCRIPTION)}).")
        return  # Stop the execution if they don't match

    caption_properties = {
        'font_size': FONT_SIZE,
        'font_color': FONT_COLOR,
        'caption_offset_y': CAPTION_OFFSET_Y,
    }

    mp4_maker_engine.main(
        VIDEO_CAPTIONS,
        working_directory,
        VIDEO_WIDTH,
        VIDEO_HEIGHT,
        caption_properties,
        DISPLAY_DURATION_PER_IMAGE,
        AUDIO_TRACK_TYPE,
        OUTPUT_FILENAME_PATTERN
    )

from openai_utils import summarize_and_estimate_cost

summary_data_example = {
    'summary_text': 'Video generation completed.',
    'total_input_tokens': 0,  # Assuming no chat completions, you can fill this in if needed
    'total_output_tokens': 0,  # Assuming no chat completions, you can fill this in if needed
    'number_of_images': len(VIDEO_CAPTIONS)
}
summarize_and_estimate_cost(summary_data_example)

if __name__ == '__main__':
    main()