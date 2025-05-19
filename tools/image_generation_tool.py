# tools/image_generation_tool.py
from smolagents import Tool

class ImageGenerationTool(Tool):
    name = "image_generator"
    description = "Generates an image based on a text prompt using OpenAI's GPT-Image-1 model."
    inputs = {
        "prompt": {
            "type": "string",
            "description": "The text description of the image to generate",
        },
        "style_guide": {
            "type": "string",
            "description": "Optional style guide for the image",
            "nullable": True
        }
    }
    output_type = "string"

    def forward(self, prompt, style_guide=None):
        """
        Generate an image based on the provided prompt and style guide.
        
        Args:
            prompt (str): Text description of the image to generate
            style_guide (str, optional): Style guide for the image
            
        Returns:
            str: Path to the generated image file
        """
        from openai import OpenAI
        import os
        import uuid
        import base64
        import re
        
        # Initialize OpenAI client
        client = OpenAI()
        
        # Set up output directory
        output_dir = os.path.join(os.getcwd(), "generated_images")
        os.makedirs(output_dir, exist_ok=True)
        
        # Create filename
        filename_base = "generated_image"
        clean_filename = re.sub(r'[^\w\-_.]', '', filename_base.replace(" ", "_").lower())
        unique_suffix = uuid.uuid4().hex[:6]
        image_filename = f"{clean_filename}_{unique_suffix}.png"
        output_path = os.path.join(output_dir, image_filename)
        
        # Combine prompt with style guide if provided
        enhanced_prompt = prompt
        if style_guide:
            enhanced_prompt = f"{prompt}. Style: {style_guide}"
        
        # Generate image with GPT-Image-1
        response = client.images.generate(
            model="gpt-image-1",
            prompt=enhanced_prompt,
            size="1024x1024",
            n=1
        )
        
        # Save the image
        image_base64 = response.data[0].b64_json
        image_bytes = base64.b64decode(image_base64)
        with open(output_path, 'wb') as f:
            f.write(image_bytes)
            
        return output_path

# Create an instance of the tool
image_generation_tool = ImageGenerationTool()
