import cv2
import time
import torch
from PIL import Image
from insightface.app import FaceAnalysis
from ip_adapter.ip_adapter_faceid import IPAdapterFaceID
from diffusers import StableDiffusionPipeline, DDIMScheduler, AutoencoderKL
import fastapi
from fastapi import File, UploadFile
import base64
import io
from PIL import Image
import numpy as np

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

def generate(image_path,prompt = "photo of a person"):
  try:
    image = cv2.imread(image_path)
    faces = face_app.get(image)
    faceid_embeds = torch.from_numpy(faces[0].normed_embedding).unsqueeze(0)
    # generate image
    negative_prompt = "monochrome, lowres, bad anatomy, worst quality, low quality, blurry"
    images = ip_model.generate(
        prompt=prompt, negative_prompt=negative_prompt, faceid_embeds=faceid_embeds, num_samples=1, width=512, height=768, num_inference_steps=30)
    return images[0]
  except:
      return False