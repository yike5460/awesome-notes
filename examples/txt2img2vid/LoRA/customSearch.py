import os
import requests
import cv2
import imagehash
import logging
from PIL import Image
from googleapiclient.discovery import build

import torch
from PIL import Image
from sklearn.metrics.pairwise import cosine_similarity
import clip

from dotenv import load_dotenv

load_dotenv()

# Read from local env file
API_KEY = os.getenv('GOOGLE_API_KEY')
CSE_ID = os.getenv('GOOGLE_CSE_ID')

# Set up logging to output to current stdout for debugging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def is_duplicate(image_directory, threshold=0.9):
    # Load the CLIP model
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, preprocess = clip.load("ViT-B/32", device=device)

    # Dictionary to store image embeddings
    embeddings = {}
    # List to keep track of pairs of duplicate images
    duplicate_pairs = []

    # Function to preprocess and get embedding from an image
    def get_embedding(image_path, preprocess, model):
        with Image.open(image_path) as image:
            logger.info(f"Preprocessing {image_path}")
            image_tensor = preprocess(image).unsqueeze(0).to(device)
            logger.info(f"Getting embedding for {image_path}")
            with torch.no_grad():
                embedding = model.encode_image(image_tensor)
                logger.info(f"Embedding for {image_path}: {embedding}")
            return embedding.cpu().numpy()

    # Iterate over all the images in the directory
    for image_filename in os.listdir(image_directory):
        if image_filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
            image_path = os.path.join(image_directory, image_filename)
            logger.info(f"Processing {image_path}")
            try:
                # Get the embedding of the current image
                logger.info(f"Getting embedding for {image_path}")
                current_embedding = get_embedding(image_path, preprocess, model)
                logger.info(f"Embedding for {image_path}: {current_embedding}")
                # Compare the embedding with the embeddings of previous images
                for prev_image_path, prev_embedding in embeddings.items():
                    logger.info(f"Comparing with {prev_image_path}")
                    similarity = cosine_similarity(current_embedding, prev_embedding)
                    # If the similarity is above the threshold, it's a potential duplicate
                    if similarity >= threshold:
                        logger.info(f"Duplicate found: {image_path} and {prev_image_path}")
                        duplicate_pairs.append((image_path, prev_image_path))
                        break
                else:
                    # No duplicate found, add the image embedding to the dictionary
                    embeddings[image_path] = current_embedding
            except IOError as e:
                logger.error(f"Error processing image {image_path}: {e}")

    return duplicate_pairs

# Use such function to further remove duplicated images since we keep to see redundant images been downloaded even turn on the official API filter
def remove_redundant_images(image_directory, threshold=5):
    """
    Remove redundant images from a directory.
    
    :param image_directory: The directory containing the images to process.
    :param threshold: The Hamming distance threshold to consider images as duplicates.
    :return: None
    """
    # Create a dictionary to store image hash values
    hashes = {}
    # List to keep track of pairs of redundant images
    redundant_pairs = []

    # Iterate over all the images in the directory
    for image_filename in os.listdir(image_directory):
        image_path = os.path.join(image_directory, image_filename)
        logger.info(f"Redundancy check for {image_path}")
        try:
            with Image.open(image_path) as img:
                # Calculate the hash of the image
                h = imagehash.phash(img)
                # Compare the hash with the hashes of previous images
                for prev_h, prev_image_path in hashes.items():
                    # If the hash is within the threshold, it's a potential duplicate
                    if h - prev_h < threshold:
                        logger.info(f"WARNING: {image_path} is redundant with {prev_image_path}")
                        redundant_pairs.append((image_path, prev_image_path))
                        break
                else:
                    # No match found, add the image hash to the dictionary
                    hashes[h] = image_path
        except IOError as e:
            logger.info(f"Error processing image {image_path}: {e}")

    # Remove redundant images
    for image_path, _ in redundant_pairs:
        logger.info(f"Removed redundant image: {image_path}")
        # os.remove(image_path)

def is_blurry(image_path, threshold=100.0):
    """ Check if the image is blurry based on the variance of the Laplacian. """
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    fm = cv2.Laplacian(gray, cv2.CV_64F).var()
    return fm < threshold

# Function to perform a Google Custom Search and return image URLs
def google_search(search_term, api_key, cse_id, img_size="medium", img_type="photo", img_color_type="color", img_dominant_color=None, rights=None, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    # More schema refer to https://developers.google.com/custom-search/v1/reference/rest/v1/cse/list
    try:
        res = service.cse().list(
            q=search_term,
            cx=cse_id,
            searchType='image',
            imgSize=img_size,
            imgType=img_type,
            imgColorType=img_color_type,
            imgDominantColor=img_dominant_color,
            rights=rights,
            filter='1', # Turns on duplicate content filter
            c2coff='1', # Enables Simplified and Traditional Chinese Search.
            **kwargs
        ).execute()
        return res['items']
    except Exception as e:
        logger.error(f"An error occurred during the search: {e}")
        return []

# Function to download images given a list of URLs
def download_images(image_urls, save_folder):
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    for i, url in enumerate(image_urls):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                image_path = os.path.join(save_folder, f'image_{i}.jpg')
                with open(image_path, 'wb') as file:
                    file.write(response.content)
                    # check if such image is blurry
                    if is_blurry(image_path):
                        logger.info(f"Image image_{i}.jpg is blurry. Warning: it will be removed.")
        except Exception as e:
            logger.info(f"An error occurred while downloading image {url}: {e}")

# User inputs
search_label = input("Enter the label (e.g., 'jeff bezos', 'taylor swift'): ")
img_size = input("Enter the image size (e.g., 'small', 'medium', 'large', 'xlarge'): ").upper()
img_type = input("Enter the image type (e.g., 'face', 'photo', 'clipart', 'lineart'): ")
img_color_type = input("Enter the image color type (e.g., 'color', 'gray', 'mono', 'trans'): ").strip() or 'color'
img_dominant_color = input("Enter the image dominant color (e.g., 'black', 'blue', 'brown', 'gray'): ").strip() or 'white'
rights = input("Enter the license type (e.g., 'cc_publicdomain', 'cc_attribute', 'cc_sharealike', 'cc_noncommercial', 'cc_nonderived'): ").strip() or 'cc_publicdomain'

# Main code entry point
if __name__ == "__main__":

    # Perform the search
    results = google_search(
        search_term=search_label,
        api_key=API_KEY,
        cse_id=CSE_ID,
        img_size=img_size,
        img_type=img_type,
        img_color_type=img_color_type,
        img_dominant_color=img_dominant_color,
        rights=rights,
        num=10 # Number of results to return (Valid values are integers between 1 and 10, inclusive.)
    )

    # Extract image URLs
    image_urls = [item['link'] for item in results]

    # Download the images to a folder named 'downloaded_images'
    download_images(image_urls, 'downloaded_images')
    logger.info("Download completed.")

    # is_duplicate('downloaded_images')
    remove_redundant_images('downloaded_images')
    logger.info("Redundant images removed.")