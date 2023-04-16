# Copyright (c) <year>, <copyright holder>
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

import json
import requests
import io
import os
import sys
import base64
import re
from pathlib import Path
from PIL import Image, PngImagePlugin


def generate_previews(checkpoint_dir, url="http://127.0.0.1:7860"):
    skip_models = ["instruct-pix2pix-00-22000"]
    skip_models_txt = " ".join(skip_models)

    # get available previews
    chk_previews = [f for f in os.listdir(checkpoint_dir) if re.match(r'.*\.png', f)]

    # load preview payload
    # NOTE modify as desired to customize preview data
    preview_payload = open('../assets/preview_payload.json')
    payload = json.load(preview_payload)

    # refresh checkpoints
    requests.post(url=f'{url}/sdapi/v1/refresh-checkpoints')
    # get available models
    models = requests.get(url=f'{url}/sdapi/v1/sd-models').json()

    # loop models and generate preview (embedding result)
    # NOTE: taken from api sample code @ https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki/API
    for model in models:
        # skip models if configured
        model_filename = Path(model['filename']).stem
        if model_filename in skip_models_txt:
            print(f"Skipping model {model['title']}")
            continue

        # check if model preview is already in target folder
        preview = model_filename + ".png"
        if preview in chk_previews:
            print(f"Preview already present, skipping model {model['title']}")
            continue

        print(f"Generating preview for model {model['title']}")
        # load sd model
        option_payload = {
            "sd_model_checkpoint": model['title']
        }
        response = requests.post(url=f'{url}/sdapi/v1/options', json=option_payload)
        if response.status_code == 200:
            # generate image
            response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload)
            r = response.json()
            for i in r['images']:
                image = Image.open(io.BytesIO(base64.b64decode(i.split(",", 1)[0])))
                png_payload = {
                    "image": "data:image/png;base64," + i
                }
                response2 = requests.post(url=f'{url}/sdapi/v1/png-info', json=png_payload)
                pnginfo = PngImagePlugin.PngInfo()
                pnginfo.add_text("parameters", response2.json().get("info"))
                # save image with generation metadata
                image.save(Path(checkpoint_dir, preview), pnginfo=pnginfo)


if __name__ == '__main__':
    target_checkpoint_dir = None
    if len(sys.argv) > 1:
        target_checkpoint_dir = sys.argv[1]
    else:
        print("usage: python preview.py <target_checkpoints_dir>")
        exit(1)
    generate_previews(target_checkpoint_dir)
