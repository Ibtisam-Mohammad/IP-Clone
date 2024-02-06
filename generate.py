import io
import sys
import cv2
import time
import torch
import base64
import numpy as np
from PIL import Image
sys.path.append("IP-Adapter")
from insightface.app import FaceAnalysis
from ip_adapter.ip_adapter_faceid import IPAdapterFaceID
from diffusers import StableDiffusionPipeline, DDIMScheduler, AutoencoderKL

base_model_path = "SG161222/Realistic_Vision_V4.0_noVAE"
vae_model_path = "stabilityai/sd-vae-ft-mse"

device = "cuda"

noise_scheduler = DDIMScheduler(
    num_train_timesteps=1000,
    beta_start=0.00085,
    beta_end=0.012,
    beta_schedule="scaled_linear",
    clip_sample=False,
    set_alpha_to_one=False,
    steps_offset=1,
)
vae = AutoencoderKL.from_pretrained(vae_model_path).to(dtype=torch.float16)
pipe = StableDiffusionPipeline.from_pretrained(
    base_model_path,
    torch_dtype=torch.float16,
    scheduler=noise_scheduler,
    vae=vae,
    feature_extractor=None,
    safety_checker=None
)
face_app = FaceAnalysis(name="buffalo_l", providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
face_app.prepare(ctx_id=0, det_size=(640, 640))

ip_ckpt = "ip-adapter-faceid_sd15.bin"
# load ip-adapter
ip_model = IPAdapterFaceID(pipe, ip_ckpt, device)

def resize_image_cv(img):
    # convert the dimension with the shortest dimension being 512 pixels, and the other one to the multiple of 8 while preserving aspect ratio
    original_height, original_width = img.shape[:2]
    if original_width > original_height:
        new_height = 512
        new_width = int((original_width / original_height) * 512)
    else:
        new_width = 512
        new_height = int((original_height / original_width) * 512)
    new_width = (new_width // 8) * 8
    new_height = (new_height // 8) * 8
    resized_img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
    
    return resized_img

def generate(image_path,prompt = "photo of a person in a library"):
  try:
    image = cv2.imread(image_path)
    image = resize_image_cv(image)
    faces = face_app.get(image)
    faceid_embeds = torch.from_numpy(faces[0].normed_embedding).unsqueeze(0)
    negative_prompt = "monochrome, lowres, bad anatomy, worst quality, low quality, blurry"
    print("Generating Image...........")
    images = ip_model.generate(
        prompt=prompt, 
        negative_prompt=negative_prompt, 
        faceid_embeds=faceid_embeds, 
        num_samples=1,
        num_inference_steps=30)
    print("Generation Complete...........")
    return images[0]
  except Exception as e:
      print(f"An error occurred: {e}")
      return False