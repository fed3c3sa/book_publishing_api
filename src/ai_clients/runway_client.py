"""
Runway API integration module for the Children's Book Generator.

This module provides a client for generating images using the Runway API
for children's book illustrations with advanced character consistency features.
"""

import os
import time
import requests
import base64
from typing import Dict, Any, Optional, Union, List
from pathlib import Path

from ..utils.config import load_config


class RunwayClient:
    """Client for interacting with Runway Gen-4 Image API."""
    
    def __init__(self, config: Optional[Dict[str, str]] = None):
        """
        Initialize the Runway client.
        
        Args:
            config: Configuration dictionary. If None, loads from environment.
        """
        if config is None:
            config = load_config()
        
        self.api_key = config.get("runway_api_key")
        if not self.api_key:
            raise ValueError("Runway API key not found. Please set RUNWAY_API_KEY environment variable.")
            
        self.base_url = "https://api.dev.runwayml.com/v1"
        self.text_to_image_url = f"{self.base_url}/text_to_image"
    
    def _encode_image_to_data_uri(self, image_path: Union[str, Path]) -> str:
        """
        Encode an image file to a data URI for use with Runway API.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Data URI string for the image
        """
        image_path = Path(image_path)
        
        # Read the image file
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        # Encode to base64
        base64_image = base64.b64encode(image_data).decode('utf-8')
        
        # Determine MIME type based on file extension
        ext = image_path.suffix.lower()
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg', 
            '.png': 'image/png',
            '.webp': 'image/webp'
        }
        mime_type = mime_types.get(ext, 'image/jpeg')
        
        return f"data:{mime_type};base64,{base64_image}"
    
    def generate_image(
        self,
        prompt: str,
        output_path: Union[str, Path],
        reference_images: Optional[List[Dict[str, str]]] = None,
        ratio: str = "720:1280",
        model: str = "gen4_image",
        seed: Optional[int] = None
    ) -> str:
        """
        Generate an image using Runway API.
        
        Args:
            prompt: Text prompt for image generation
            output_path: Path where the generated image will be saved
            reference_images: List of reference images with format:
                [{"uri": "path_or_url", "tag": "character1"}, ...]
                Tags can be referenced in prompt using @tag syntax
            ratio: Aspect ratio for the image (e.g., "1920:1080", "1:1")
            model: Runway model to use (default: "gen4_image")
            seed: Random seed for reproducible generation
            
        Returns:
            Path to the generated image file
        """
        # Ensure output directory exists
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Prepare request payload using EXACT Runway API parameters
        payload = {
            "promptText": prompt,  # Runway uses "promptText", not "prompt"
            "model": model,
            "ratio": ratio
        }
        
        # Add seed if provided
        if seed is not None:
            payload["seed"] = seed
        
        # Process reference images using EXACT Runway format
        if reference_images:
            processed_refs = []
            for ref in reference_images:
                ref_dict = {}
                
                # Handle the URI (can be file path or URL)
                uri = ref.get("uri", "")
                if uri:
                    if uri.startswith(("http://", "https://")):
                        # It's already a URL
                        ref_dict["uri"] = uri
                    else:
                        # It's a local file path, convert to data URI
                        if os.path.exists(uri):
                            ref_dict["uri"] = self._encode_image_to_data_uri(uri)
                        else:
                            print(f"Warning: Reference image not found: {uri}")
                            continue
                
                # Add tag if provided (optional according to docs)
                if "tag" in ref and ref["tag"]:
                    ref_dict["tag"] = ref["tag"]
                
                if ref_dict.get("uri"):
                    processed_refs.append(ref_dict)
            
            if processed_refs:
                payload["referenceImages"] = processed_refs  # Runway uses "referenceImages"
        
        # Prepare headers
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Runway-Version": "2024-11-06"
        }
        
        try:
            # Validate and clean prompt text
            prompt_text = payload.get("promptText", "")
            if not prompt_text or not prompt_text.strip():
                raise ValueError("Prompt text is empty or invalid")
            
            # Clean and validate prompt text
            prompt_text = prompt_text.strip()
            
            # Remove or replace problematic characters
            import re
            # Keep only printable ASCII characters, spaces, and common punctuation
            prompt_text = re.sub(r'[^\x20-\x7E]', ' ', prompt_text)
            # Replace multiple spaces with single space
            prompt_text = re.sub(r'\s+', ' ', prompt_text).strip()
            
            # Comprehensive content filtering to ensure child-friendly content
            # This ensures prompts pass Runway's moderation for children's book content
            def make_child_friendly(text):
                """Convert text to be child-friendly and pass content moderation."""
                
                # Extended list of terms that might trigger moderation
                replacements = {
                    # Violence & conflict
                    'violence': 'adventure', 'violent': 'energetic', 'fight': 'play',
                    'battle': 'game', 'war': 'adventure', 'attack': 'approach',
                    'destroy': 'change', 'defeat': 'overcome', 'conquer': 'explore',
                    
                    # Weapons & dangerous items
                    'weapon': 'tool', 'gun': 'toy', 'knife': 'utensil', 'sword': 'stick',
                    'blade': 'edge', 'arrow': 'pointer', 'spear': 'stick', 'axe': 'tool',
                    
                    # Death & harm
                    'death': 'sleep', 'die': 'rest', 'kill': 'stop', 'murder': 'stop',
                    'dead': 'sleeping', 'harm': 'bother', 'hurt': 'sad', 'pain': 'discomfort',
                    
                    # Scary & dark themes
                    'scary': 'exciting', 'frightening': 'surprising', 'terrifying': 'amazing',
                    'horror': 'adventure', 'nightmare': 'dream', 'monster': 'creature',
                    'demon': 'character', 'ghost': 'spirit', 'zombie': 'sleepy character',
                    'evil': 'mischievous', 'wicked': 'playful', 'sinister': 'mysterious',
                    
                    # Mature themes
                    'adult': 'grown-up', 'mature': 'wise', 'explicit': 'clear',
                    'inappropriate': 'unusual', 'forbidden': 'special', 'dangerous': 'exciting',
                    
                    # Body parts that might be flagged
                    'blood': 'red liquid', 'bleeding': 'red', 'wound': 'mark',
                    'injury': 'scratch', 'broken': 'bent', 'torn': 'worn',
                    
                    # Negative emotions (soften them)
                    'angry': 'upset', 'furious': 'very upset', 'rage': 'frustration',
                    'hate': 'dislike', 'revenge': 'justice', 'jealous': 'envious'
                }
                
                # Apply replacements
                for problematic, safe in replacements.items():
                    if problematic in text.lower():
                        print(f"⚠️  Making child-friendly: {problematic} → {safe}")
                        text = re.sub(rf'\b{problematic}\b', safe, text, flags=re.IGNORECASE)
                
                # Remove any remaining potentially problematic patterns
                # Remove excessive adjectives that might be concerning
                concerning_patterns = [
                    r'\b(very|extremely|incredibly|terribly)\s+(scary|frightening|dangerous|violent)\b',
                    r'\b(blood|gore|violence|death)\s+\w+',
                    r'\b\w+\s+(blood|gore|violence|death)\b'
                ]
                
                for pattern in concerning_patterns:
                    if re.search(pattern, text, re.IGNORECASE):
                        print(f"⚠️  Removing concerning pattern: {pattern}")
                        text = re.sub(pattern, 'interesting', text, flags=re.IGNORECASE)
                
                return text
            
            # Apply child-friendly filtering
            original_prompt = prompt_text
            prompt_text = make_child_friendly(prompt_text)
            
            if original_prompt != prompt_text:
                print(f"📝 Content filtering applied:")
                print(f"   Original: {original_prompt[:60]}...")
                print(f"   Filtered: {prompt_text[:60]}...")
            
            # Check length limit
            if len(prompt_text) > 1000:  # Runway has a 1000 character limit based on examples
                print(f"⚠️  Prompt too long ({len(prompt_text)} chars), truncating to 1000...")
                prompt_text = prompt_text[:997] + "..."
            
            # Final validation
            if not prompt_text:
                raise ValueError("Prompt text is empty after cleaning")
            
            # Update payload with cleaned prompt
            payload["promptText"] = prompt_text
            
            # Debug: Print the exact payload being sent
            print(f"🔧 Runway API Request:")
            print(f"   URL: {self.text_to_image_url}")
            print(f"   Model: {payload.get('model')}")
            print(f"   Ratio: {payload.get('ratio')}")
            print(f"   Prompt length: {len(prompt_text)}")
            print(f"   Prompt preview: {prompt_text[:100]}...")
            if 'referenceImages' in payload:
                print(f"   Reference images: {len(payload['referenceImages'])}")
            
            # Make the API request
            response = requests.post(
                self.text_to_image_url,
                json=payload,
                headers=headers,
                timeout=120
            )
            response.raise_for_status()
            response_data = response.json()
            
            # For Runway, the response typically contains a task that needs to be polled
            print(f"✅ Runway API Response: {response.status_code}")
            print(f"   Response keys: {list(response_data.keys())}")
            
            image_url = None
            
            if "output" in response_data and response_data["output"]:
                # Direct output (some models return images immediately)
                print(f"   Direct output received")
                image_url = response_data["output"][0] if isinstance(response_data["output"], list) else response_data["output"]
            elif "id" in response_data:
                # Task-based response, need to poll for completion
                task_id = response_data["id"]
                print(f"   Task created: {task_id}")
                image_url = self._poll_task_completion(task_id)
            else:
                print(f"   Unexpected response format: {response_data}")
                raise Exception(f"Unexpected response format: {response_data}")
            
            if not image_url:
                raise Exception(f"No image URL returned. Response: {response_data}")
            
            # Download the image
            self._download_image(image_url, output_path)
            
            return str(output_path)
            
        except requests.exceptions.HTTPError as e:
            # Include response content for better debugging
            error_msg = f"HTTP Error: {e}"
            try:
                if hasattr(e.response, 'text'):
                    error_msg += f"\nResponse: {e.response.text}"
            except:
                pass
            raise Exception(error_msg)
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request Error: {e}")
        except Exception as e:
            raise Exception(f"Unexpected Error: {str(e)}")
    
    def _poll_task_completion(self, task_id: str, max_wait_time: int = 300) -> Optional[str]:
        """
        Poll a Runway task until completion and return the image URL.
        
        Args:
            task_id: The task ID to poll
            max_wait_time: Maximum time to wait in seconds
            
        Returns:
            Image URL when task is complete, None if failed
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "X-Runway-Version": "2024-11-06"
        }
        
        task_url = f"{self.base_url}/tasks/{task_id}"
        start_time = time.time()
        
        print(f"🔄 Polling task {task_id} for completion...")
        poll_count = 0
        
        while time.time() - start_time < max_wait_time:
            try:
                poll_count += 1
                response = requests.get(task_url, headers=headers, timeout=30)
                response.raise_for_status()
                task_data = response.json()
                
                status = task_data.get("status", "").lower()
                progress = task_data.get("progress", 0)
                
                # Log polling status every few attempts
                if poll_count % 5 == 1:  # Log every 5th poll (every ~10 seconds)
                    print(f"   Poll #{poll_count}: {status} (progress: {progress})")
                
                if status == "succeeded":
                    # Task completed successfully
                    output = task_data.get("output", [])
                    if output:
                        return output[0] if isinstance(output, list) else output
                    else:
                        raise Exception(f"Task succeeded but no output found: {task_data}")
                
                elif status in ["failed", "cancelled"]:
                    # Task failed - get detailed error information
                    error_msg = task_data.get("error", "Unknown error")
                    failure_reason = task_data.get("failure", {})
                    progress = task_data.get("progress", "Unknown")
                    
                    detailed_error = f"Task {task_id} failed: {error_msg}"
                    if failure_reason:
                        detailed_error += f"\nFailure details: {failure_reason}"
                    detailed_error += f"\nProgress: {progress}"
                    detailed_error += f"\nFull task data: {task_data}"
                    
                    print(f"❌ Detailed task failure info:")
                    print(f"   Task ID: {task_id}")
                    print(f"   Status: {status}")
                    print(f"   Error: {error_msg}")
                    print(f"   Failure: {failure_reason}")
                    print(f"   Progress: {progress}")
                    
                    raise Exception(detailed_error)
                
                elif status in ["pending", "running"]:
                    # Task still in progress, wait and retry
                    time.sleep(2)
                    continue
                
                else:
                    # Unknown status
                    print(f"Unknown task status: {status}, continuing to poll...")
                    time.sleep(2)
                    continue
                    
            except requests.exceptions.RequestException as e:
                print(f"Error polling task {task_id}: {e}")
                time.sleep(2)
                continue
        
        raise Exception(f"Task {task_id} timed out after {max_wait_time} seconds")
    
    def _download_image(self, image_url: str, output_path: Path) -> None:
        """
        Download an image from URL to local path.
        
        Args:
            image_url: URL of the image to download
            output_path: Local path to save the image
        """
        for attempt in range(3):
            try:
                img_response = requests.get(image_url, timeout=60)
                img_response.raise_for_status()
                
                with open(output_path, "wb") as f:
                    f.write(img_response.content)
                
                break  # Success
                
            except requests.exceptions.RequestException as e:
                if attempt < 2:  # Don't sleep on the last attempt
                    time.sleep(2)
                else:
                    raise Exception(f"Failed to download image after retries: {e}")
    
    def generate_character_reference_image(
        self,
        character_data: Dict[str, Any],
        output_dir: Path,
        character_tag: Optional[str] = None
    ) -> str:
        """
        Generate a reference image for a character to use for consistency.
        
        Args:
            character_data: Character description dictionary
            output_dir: Directory to save the character image
            character_tag: Optional tag for the character (defaults to character name)
            
        Returns:
            Path to the generated character image file
        """
        # Extract character information
        char_name = character_data.get("character_name", "character")
        char_tag = character_tag or char_name.lower().replace(" ", "_")
        
        print(f"🎭 Generating character reference for: {char_name}")
        
        # Build character description prompt with fallback
        prompt_parts = []
        
        try:
            # Use consistency formula as primary description
            consistency_formula = character_data.get("consistency_formula", "")
            if consistency_formula and isinstance(consistency_formula, str):
                print(f"   Using consistency formula: {consistency_formula[:50]}...")
                prompt_parts.append(str(consistency_formula))
            
            # Add ideogram character seed if available
            char_seed = character_data.get("ideogram_character_seed", "")
            if char_seed and isinstance(char_seed, str):
                print(f"   Using character seed: {char_seed[:50]}...")
                prompt_parts.append(str(char_seed))
            
            # Fallback to original description
            if not prompt_parts:
                original_desc = character_data.get("original_user_description", "")
                if original_desc and isinstance(original_desc, str):
                    print(f"   Using original description: {original_desc[:50]}...")
                    prompt_parts.append(f"{char_name}: {str(original_desc)}")
                else:
                    # Last resort: build simple description
                    species = str(character_data.get("species", "character"))
                    age = str(character_data.get("age_category", ""))
                    
                    desc = f"{char_name}, {species}"
                    if age:
                        desc += f", {age}"
                    
                    print(f"   Using fallback description: {desc}")
                    prompt_parts.append(desc)
            
            # Create the main prompt
            main_prompt = " ".join(str(part) for part in prompt_parts if part)
            
        except Exception as e:
            print(f"⚠️  Error building character prompt: {e}")
            # Ultimate fallback: simple, ultra-safe prompt
            main_prompt = f"{char_name}, friendly children's book character"
        
        # Add ultra-safe style specifications for children's book character
        style_specs = (
            " Character reference sheet style, clean white background, "
            "cheerful children's book illustration, bright happy colors, friendly and kind, "
            "wholesome family-friendly digital art, cute character design, smiling portrait"
        )
        main_prompt += style_specs
        
        # Final safety check - if prompt is still too complex, use ultra-simple version
        if len(main_prompt) > 300 or any(word in main_prompt.lower() for word in ['dark', 'shadow', 'black', 'night']):
            print(f"⚠️  Using ultra-safe fallback prompt for {char_name}")
            main_prompt = f"{char_name}, happy smiling children's book character, bright colors, friendly, cheerful illustration, wholesome family-friendly art"
        
        print(f"   Final prompt length: {len(main_prompt)} characters")
        print(f"   Final prompt preview: {main_prompt[:100]}...")
        
        # Determine output filename
        safe_char_name = "".join(c for c in char_name if c.isalnum() or c in (' ', '_')).strip().replace(' ', '_')
        output_filename = f"character_{safe_char_name}.png"
        output_path = output_dir / output_filename
        
        # Generate the character reference image (using vertical 720p ratio)
        return self.generate_image(
            prompt=main_prompt,
            output_path=output_path,
            ratio="720:1280"  # Vertical 720p format for cost-effective character references
        )
    
    def generate_book_page_image(
        self,
        image_prompt_data: Dict[str, Any],
        page_number: int,
        output_dir: Path,
        reference_image_path: Optional[Path] = None,
        characters_data: Optional[List[Dict[str, Any]]] = None,
        character_images: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Generate an image for a specific book page.
        
        Args:
            image_prompt_data: Structured image prompt data from Gemini
            page_number: Page number for file naming
            output_dir: Directory to save the image
            reference_image_path: Optional reference image for style consistency (legacy)
            characters_data: Optional list of character data for consistency
            character_images: Dict mapping character names to their reference image paths
            
        Returns:
            Path to the generated image file
        """
        # Extract the main prompt
        main_prompt = image_prompt_data.get("image_prompt", "")
        
        # Prepare reference images for character consistency
        reference_images = []
        
        # Add character reference images
        if character_images and characters_data:
            for char_data in characters_data:
                char_name = char_data.get("character_name", "")
                if char_name in character_images:
                    char_tag = char_name.lower().replace(" ", "_")
                    reference_images.append({
                        "uri": character_images[char_name],
                        "tag": char_tag
                    })
                    
                    # Update prompt to reference the character
                    if f"@{char_tag}" not in main_prompt:
                        # Add character reference to prompt
                        char_ref = f"featuring @{char_tag}"
                        if "featuring" in main_prompt.lower():
                            main_prompt = main_prompt.replace("featuring", f"featuring @{char_tag},")
                        else:
                            main_prompt = f"{main_prompt}, {char_ref}"
        
        # Add legacy reference image for style consistency if provided
        if reference_image_path and os.path.exists(reference_image_path):
            reference_images.append({
                "uri": str(reference_image_path)
                # No tag for style reference
            })
        
        # Add style specifications if available
        style_specs = image_prompt_data.get("style_specifications", "")
        if style_specs:
            main_prompt += f" {style_specs}"
        
        # Add composition notes if available
        composition = image_prompt_data.get("composition_notes", "")
        if composition:
            main_prompt += f" {composition}"
        
        # Enhance prompt for children's book style
        main_prompt += " Children's book illustration, bright colors, friendly and engaging, high quality digital art"
        
        # Determine output filename
        output_filename = f"page_{page_number:02d}.png"
        output_path = output_dir / output_filename
        
        # Generate the image
        return self.generate_image(
            prompt=main_prompt,
            output_path=output_path,
            reference_images=reference_images if reference_images else None,
            ratio="720:1280"  # Vertical 720p format for cost-effective book pages
        )
    
    def generate_book_cover(
        self,
        title: str,
        characters: List[Dict[str, Any]],
        theme: str,
        output_dir: Path,
        reference_image_path: Optional[Path] = None,
        character_images: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Generate a cover image for the book.
        
        Args:
            title: Book title
            characters: List of main characters
            theme: Book theme/genre
            output_dir: Directory to save the cover
            reference_image_path: Optional reference image for style consistency (legacy)
            character_images: Dict mapping character names to their reference image paths
            
        Returns:
            Path to the generated cover image file
        """
        # Create cover prompt
        main_characters = [char for char in characters if char.get("character_type") == "main"]
        
        cover_prompt = f"Children's book cover illustration for '{title}', "
        
        # Prepare reference images for character consistency
        reference_images = []
        
        # Add character reference images and mentions
        if character_images and main_characters:
            char_mentions = []
            for char in main_characters:
                char_name = char.get("character_name", "")
                if char_name in character_images:
                    char_tag = char_name.lower().replace(" ", "_")
                    reference_images.append({
                        "uri": character_images[char_name],
                        "tag": char_tag
                    })
                    char_mentions.append(f"@{char_tag}")
            
            if char_mentions:
                cover_prompt += f"featuring {', '.join(char_mentions)}, "
        
        # Add legacy reference image for style consistency if provided
        if reference_image_path and os.path.exists(reference_image_path):
            reference_images.append({
                "uri": str(reference_image_path)
                # No tag for style reference
            })
        
        cover_prompt += (
            f"theme: {theme}, bright and colorful children's book illustration style, "
            f"engaging and friendly, high quality, professional book cover design, "
            f"title space at top, appealing to children"
        )
        
        # Determine output filename
        output_filename = "cover.png"
        output_path = output_dir / output_filename
        
        # Generate the cover (using portrait orientation of 1080p)
        return self.generate_image(
            prompt=cover_prompt,
            output_path=output_path,
            reference_images=reference_images if reference_images else None,
            ratio="1080:1920"  # Portrait orientation of 1080p for book cover
        )