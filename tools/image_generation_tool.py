# tools/image_generation_tool.py
import os
import uuid

# This is a placeholder for a real image generation tool.
# In a real application, this would interface with an image generation API (e.g., DALL-E, Stable Diffusion via Replicate, etc.)
# or a local model if available.

def generate_image_from_prompt(prompt: str, style_guide: str, output_dir: str, filename_base: str) -> str:
    """
    Simulates generating an image based on a prompt and style guide, saving it, and returning the path.

    Args:
        prompt (str): The detailed text prompt for the image.
        style_guide (str): A description of the desired artistic style.
        output_dir (str): The directory to save the generated image.
        filename_base (str): The base name for the image file (e.g., "chapter1_image1").

    Returns:
        str: The full path to the (simulated) generated image file, or an error string.
    """
    print(f"[ImageGenerationTool] Received prompt: \t{prompt}\t with style: \t{style_guide}")
    
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir, exist_ok=True)
            print(f"[ImageGenerationTool] Created output directory: {output_dir}")
        except Exception as e:
            error_msg = f"[ImageGenerationTool] Error creating output directory {output_dir}: {e}"
            print(error_msg)
            return error_msg

    # Generate a unique filename to avoid overwrites
    unique_suffix = uuid.uuid4().hex[:6]
    image_filename = f"{filename_base.replace(	 	, 	_	).lower()}_{unique_suffix}.png" # Ensure filename is clean
    full_image_path = os.path.join(output_dir, image_filename)

    try:
        # Simulate image generation by creating a dummy file with the prompt and style
        with open(full_image_path, "w") as f:
            f.write(f"Simulated Image for Prompt:\n{prompt}\n\nStyle Guide:\n{style_guide}")
        
        success_msg = f"[ImageGenerationTool] Successfully simulated image generation. Image saved to: {full_image_path}"
        print(success_msg)
        return full_image_path
    except Exception as e:
        error_msg = f"[ImageGenerationTool] Error simulating image generation and saving to {full_image_path}: {e}"
        print(error_msg)
        return error_msg

if __name__ == "__main__":
    # Example Usage (for testing the tool directly)
    sample_prompt = "A friendly dragon reading a book in a cozy cave, illuminated by glowing crystals."
    sample_style = "Warm, whimsical, detailed illustration, storybook style."
    sample_output_dir = "/home/ubuntu/book_writing_agent/outputs/tool_test/images"
    sample_filename_base = "dragon_reading_test"

    # Ensure the base output directory for the test exists
    if not os.path.exists(sample_output_dir):
        os.makedirs(sample_output_dir, exist_ok=True)

    image_path_or_error = generate_image_from_prompt(
        prompt=sample_prompt,
        style_guide=sample_style,
        output_dir=sample_output_dir,
        filename_base=sample_filename_base
    )
    print(f"Tool execution result: {image_path_or_error}")

    # Test with a prompt that might have characters needing cleaning for a filename
    sample_prompt_2 = "A cat *flying* on a broomstick!"
    sample_filename_base_2 = "cat_flying_&^%"
    image_path_or_error_2 = generate_image_from_prompt(
        prompt=sample_prompt_2,
        style_guide=sample_style,
        output_dir=sample_output_dir,
        filename_base=sample_filename_base_2
    )
    print(f"Tool execution result 2: {image_path_or_error_2}")

