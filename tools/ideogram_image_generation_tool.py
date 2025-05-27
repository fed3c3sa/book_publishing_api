# tools/ideogram_image_generation_tool.py
from smolagents import Tool
import requests
import os
import uuid
import re
import time
import dotenv

dotenv.load_dotenv("secrets.env")


class IdeogramImageGenerationTool(Tool):
    name = "ideogram_image_generator"
    description = "Generates an image based on a text prompt using Ideogram API (v3 synchronous endpoint) with optional style reference."
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
        "style_reference_image_path": {
            "type": "string",
            "description": "Optional path to an image to use as style reference",
            "nullable": True,
        },
    }
    output_type = "string"

    def forward(self, prompt, style_guide=None, style_reference_image_path=None):
        """
        Generate an image based on the provided prompt, optional style type,
        and optional style reference image.

        Args:
            prompt (str): Text description of the image to generate.
            style_guide (str, optional): One of the v3 style_type values.
            style_reference_image_path (str, optional): Path to image for style reference.

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
        # Build the files dictionary for multipart/form-data
        files = {}
        
        # Add text parameters
        files['prompt'] = (None, prompt)
        files['aspect_ratio'] = (None, '1x1')
        
        if style_guide:
            files['style_type'] = (None, style_guide)
        
        # Add style reference image if provided
        if style_reference_image_path and os.path.exists(style_reference_image_path):
            try:
                with open(style_reference_image_path, 'rb') as img_file:
                    # Read the image content
                    image_content = img_file.read()
                    
                    # Check file size (max 10MB)
                    if len(image_content) > 10 * 1024 * 1024:
                        print(f"Warning: Style reference image exceeds 10MB limit, skipping")
                    else:
                        # Get the file extension to determine MIME type
                        ext = os.path.splitext(style_reference_image_path)[1].lower()
                        mime_types = {
                            '.jpg': 'image/jpeg',
                            '.jpeg': 'image/jpeg',
                            '.png': 'image/png',
                            '.webp': 'image/webp'
                        }
                        mime_type = mime_types.get(ext, 'image/jpeg')
                        
                        # Add to files with proper filename and MIME type
                        files['style_reference_images'] = (
                            os.path.basename(style_reference_image_path),
                            image_content,
                            mime_type
                        )
                        print(f"Using style reference image: {style_reference_image_path}")
            except Exception as e:
                print(f"Warning: Could not read style reference image: {e}")

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
            #           hasn't propagated yet (rare but possible)
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