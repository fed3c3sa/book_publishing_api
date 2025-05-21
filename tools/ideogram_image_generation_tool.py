# tools/ideogram_image_generation_tool.py
from smolagents import Tool
import requests
import os
import uuid
import re
import time      # still used for the rare retry branch
import dotenv

dotenv.load_dotenv("secrets.env")


class IdeogramImageGenerationTool(Tool):
    name = "ideogram_image_generator"
    description = "Generates an image based on a text prompt using Ideogram API (v3 synchronous endpoint)."
    inputs = {
        "prompt": {
            "type": "string",
            "description": "The text description of the image to generate",
        },
        "style_guide": {
            "type": "string",
            "description": (
                "Optional style type for the image: 'AUTO', 'GENERAL', "
                "'REALISTIC', or 'DESIGN' (Ideogram v3 style_type enum)"
            ),
            "nullable": True,
        },
    }
    output_type = "string"

    def forward(self, prompt, style_guide=None):
        """
        Generate an image based on the provided prompt and (optionally)
        an Ideogram v3 style_type.

        Args:
            prompt (str): Text description of the image to generate.
            style_guide (str, optional): One of the v3 style_type values.

        Returns:
            str: Local path to the downloaded PNG.
        """
        # 1. API key ────────────────────────────────────────────────────
        api_key = os.getenv("IDEOGRAM_API_KEY")
        if not api_key:
            return "Error: IDEOGRAM_API_KEY not configured in environment."

        # 2. Output path setup ─────────────────────────────────────────
        output_dir = os.path.join(os.getcwd(), "generated_images")
        os.makedirs(output_dir, exist_ok=True)

        clean_filename = re.sub(r"[^\w\-_.]", "", "ideogram_image".lower())
        unique_suffix = uuid.uuid4().hex[:6]
        image_filename = f"{clean_filename}_{unique_suffix}.png"
        output_path = os.path.join(output_dir, image_filename)

        # 3. Payload construction (multipart form) ─────────────────────
        payload = {
            "prompt": prompt,
            "aspect_ratio": "1x1",  # default; matches v3 enum
        }
        if style_guide:
            payload["style_type"] = style_guide

        #   ─ requests will set Content-Type: multipart/form-data
        files = {k: (None, str(v)) for k, v in payload.items()}

        # 4. Request ───────────────────────────────────────────────────
        try:
            response = requests.post(
                "https://api.ideogram.ai/v1/ideogram-v3/generate",  # v3 sync endpoint
                headers={"Api-Key": api_key},
                files=files,
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()

            # 5. Parse & download first image ─────────────────────────
            first_image = (
                data.get("data", [{}])[0] if isinstance(data.get("data"), list) else {}
            )
            image_url = first_image.get("url")
            if not image_url:
                return f"Error: No image URL returned. Response: {data}"

            # optional: tiny retry loop in case the pre-signed URL
            #           hasn’t propagated yet (rare but possible)
            for _ in range(3):
                try:
                    img_resp = requests.get(image_url, timeout=60)
                    img_resp.raise_for_status()
                    break
                except requests.exceptions.RequestException:
                    time.sleep(2)
            else:
                return "Error: Failed to download image after retries."

            with open(output_path, "wb") as f:
                f.write(img_resp.content)

            return output_path

        except requests.exceptions.HTTPError as e:
            return f"HTTP Error: {e}"
        except requests.exceptions.RequestException as e:
            return f"Request Error: {e}"
        except Exception as e:
            return f"Unexpected Error: {str(e)}"


# Create an instance of the tool
ideogram_image_generation_tool = IdeogramImageGenerationTool()
