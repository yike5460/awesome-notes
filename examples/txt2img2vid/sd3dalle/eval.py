"""
The main purpose of this script is try to answer question: How to evaluate and benchmark images quality with any objectively metrics, that all such images are generated by model, e.g. Stable Diffusion model, DALL·E model?
There are some metrics that can be used to evaluate the quality of images, such as:
- Fréchet Inception Distance (FID)
FID is one of the most widely used metrics for evaluating the quality and diversity of generated images. It measures the similarity between the statistics of real and generated images in a feature space defined by a pre-trained Inception model. Lower FID scores indicate that the generated images are more similar to real images in terms of quality and diversity. To calculate FID, you need a set of real images and a set of generated images from the model you want to evaluate.

- Inception Score (IS)
The Inception Score measures both the quality and diversity of generated images using a pre-trained Inception model.
Higher Inception Scores indicate that the generated images are both realistic and diverse. Like FID, you need a set of generated images to calculate the Inception Score.

- Kernel Inception Distance (KID)
KID is a variant of FID that uses a different distance metric between the real and generated distributions, which can be more robust to certain types of noise.

-Perceptual Similarity Metrics
These metrics measure the perceptual similarity between generated and real images, often using pre-trained neural networks.
Examples include LPIPS (Learned Perceptual Image Patch Similarity), DISTS (Deep Image Structure and Texture Similarity), and PieAPP (Perceptual Image-Error Assessment through Pairwise Preference).

And we mainly focus on implement the evaluation and benchmark based on the Fréchet Inception Distance (FID) metric
"""

import os
import urllib.request

import numpy as np
import torch
from PIL import Image
from scipy import linalg
from torch import nn


def prepare_inception_model():
    # Download the pre-trained Inception model

    inception_url = "https://github.com/mseitzer/pytorch-fid/releases/download/fid_weights/pt_inception-2015-12-05-6726825d.pth"
    urllib.request.urlretrieve(inception_url, "inception-2015-12-05.pt")


def calculate_fid(mu1, sigma1, mu2, sigma2, eps=1e-6):
    """Calculation of FID between two distributions"""

    # Calculate the square root of the product of the covariance matrices
    covmean, _ = linalg.sqrtm(sigma1.dot(sigma2), disp=False)

    # Calculate the difference between the means
    mu_diff = mu1 - mu2

    # Calculate the trace of the product of covariance matrices
    covmean_trace = np.trace(covmean)

    # Calculate the FID
    fid = mu_diff.dot(mu_diff) + np.trace(sigma1) + np.trace(sigma2) - 2 * covmean_trace

    # Add a small epsilon to avoid numerical instability
    fid = fid + eps

    return fid


def compute_fid(real_images, fake_images, batch_size=64, device="cpu"):
    """Compute FID between two image distributions"""

    # Load the Inception V3 model
    inception = torch.hub.load(
        "mseitzer/pytorch-fid:master", "inception_v3_google", pretrained=True
    )
    inception = inception.to(device)
    inception.eval()

    # Compute activations for real images
    mu_real, sigma_real = compute_activations(
        real_images, inception, batch_size, device
    )

    # Compute activations for fake images
    mu_fake, sigma_fake = compute_activations(
        fake_images, inception, batch_size, device
    )

    # Calculate FID
    fid = calculate_fid(mu_real, sigma_real, mu_fake, sigma_fake)

    return fid


def compute_activations(images, model, batch_size, device):
    """Compute activations for a set of images"""

    act = np.empty((len(images), 2048))

    for i in range(0, len(images), batch_size):
        batch = images[i : i + batch_size]
        batch = torch.from_numpy(batch).to(device)

        pred = model(batch)[0]

        # If model output is not scalar, apply global spatial pooling
        if pred.size(2) != 1 or pred.size(3) != 1:
            pred = nn.functional.adaptive_avg_pool2d(pred, output_size=(1, 1))

        act[i : i + batch_size] = pred.cpu().data.numpy().reshape(pred.size(0), 2048)

    mu = np.mean(act, axis=0)
    sigma = np.cov(act, rowvar=False)

    return mu, sigma


def load_images(image_dir):
    """Load images from a directory"""

    images = []
    # check if the directory exists otherwise create the directory in the current working directory
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
    for filename in os.listdir(image_dir):
        if filename.endswith(".png") or filename.endswith(".jpg"):
            img = Image.open(os.path.join(image_dir, filename))
            img = np.asarray(img.resize((299, 299)))
            images.append(img)

    images = np.array(images)

    return images


# main function
if __name__ == "__main__":
    # Prepare the Inception model
    prepare_inception_model()

    """
    NOTE: One question need to be clarified: How to prepare the real image set before the evaluation and benchmark as the fake image or generated image was imaginary, means they can be any style, any content and were randomly generated per execution by model like Stable Diffusion or DALL·E with specific prompt e.g. a astronaut ride a horse on the desert?
    There are some ways to prepare the real image set:
    - Define the scope: Decide on the specific domain, content, or style of images you want to evaluate. For example, if you want to benchmark against the prompt "an astronaut riding a horse on the desert," you should collect real images of astronauts, horses, and desert scenes.
    - Collect a diverse dataset: Gather a large and diverse set of real images that cover the defined scope. Ensure that the images come from various sources, angles, lighting conditions, and resolutions to represent the diversity that generative models can produce.
    - Ensure high quality: Remove any low-quality, blurry, or heavily compressed images from the dataset, as these may introduce noise and bias in the evaluation process, and such process can be done by using some image processing techniques or tools like OpenCV, PIL, etc.
    - Consider diversity in the test set: Ensure that the test set contains a diverse range of images representing different variations of the defined scope. This will help assess the generative model's ability to capture diverse scenarios.

    """
    real_images = load_images("real_images")
    fake_images = load_images("fake_images")

    # Compute FID
    fid_score = compute_fid(
        real_images,
        fake_images,
        batch_size=64,
        device="cuda" if torch.cuda.is_available() else "cpu",
    )
    print(f"FID score: {fid_score:.3f}")