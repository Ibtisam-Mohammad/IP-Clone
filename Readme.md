This application leverages a cutting-edge diffusion model to transform the face from an uploaded image into a new image based on textual prompts. Utilizing the power of the IP-Adapter and a custom diffusion model, users can generate creative and unique images from faces with ease.

## Installation

To set up the application, follow these steps:

1. Clone the repository and enter its directory:

```bash
git clone https://github.com/Ibtisam-Mohammad/IP-Clone.git
cd IP-Clone

Clone the IP-Adapter repository inside the IP-Clone directory:

bash

git clone https://github.com/tencent-ailab/IP-Adapter.git

    Install the required dependencies:

bash

pip install -r requirements.txt

    Download the necessary model file:

bash

wget https://huggingface.co/h94/IP-Adapter-FaceID/resolve/main/ip-adapter-faceid_sd15.bin

Usage

To generate an image from a face in an uploaded image, follow these steps:

    Place your target image (e.g., img.jpg) in the IP-Clone directory.

    Run the generation script with the desired prompt. For example, to generate an image based on the prompt "A man":

bash

python queue_gen.py --base_path "/content/IP-Clone/" \
                    --image_path img.jpg \
                    --prompt "A man"

Replace "A man" with any prompt that fits your creative needs.