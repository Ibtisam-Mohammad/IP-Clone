# IP-CLone
I use IP-Adapter FaceID along with Stable Diffusion model to transform the face from an uploaded image into a new image based on textual prompts.

## Installation

To set up the application, follow these steps:

1. Clone the repository and enter its directory:

```
git clone https://github.com/Ibtisam-Mohammad/IP-Clone.git
cd IP-Clone
```
2. Clone the IP-Adapter repository inside the IP-Clone directory:

```
git clone https://github.com/tencent-ailab/IP-Adapter.git
```
3. Install the required dependencies:

```
pip install -r requirements.txt
```
4. Download the necessary model file:

```
wget https://huggingface.co/h94/IP-Adapter-FaceID/resolve/main/ip-adapter-faceid_sd15.bin
```
### Usage

To generate an image from a face in an uploaded image, run the generation script with the desired prompt. 
For example, to generate an image based on the prompt "A man in a library":

```
python queue_gen.py --base_path "/content/IP-Clone/" \
                    --image_path img.jpeg \
                    --prompt "A man in a library"
```
### Input Image
![Input](https://github.com/Ibtisam-Mohammad/IP-Clone/assets/63063432/f739d9af-34e7-4735-87fe-d105ac9fcb03)
### Gernerated Image
![Generated](https://github.com/Ibtisam-Mohammad/IP-Clone/assets/63063432/ac27480c-6c3a-4b29-bf23-8f49b3de88d6)

## Note:
- We can use a better diffusion model like SDXL or another version of IP-Adapter, but I sticked to the basic. Although it can be easily changed.
- If AWS isn't available, passing arguments for local testing, should simulate the generation process, otherwise we have to setup the AWS account and pass the related arguments.
- Generated result is saved in the same directory as the uploaded image.
- Exception handling could be made more robust, but I set it to the basic for MVP.
- Reference code: https://huggingface.co/h94/IP-Adapter-FaceID