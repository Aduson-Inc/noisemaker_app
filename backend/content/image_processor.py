"""
Image Processor Module
Advanced album art analysis, color extraction, and promo image composition.
Handles PIL-based image processing for automated music promotion content.

Author: Senior Python Backend Engineer
Version: 1.0
Security Level: Production-ready
"""

from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from PIL.ImageColor import getcolor
import colorsys
import boto3
from botocore.exceptions import ClientError
import os
import io
import requests
from typing import Dict, List, Optional, Tuple, Any
import logging
from datetime import datetime
import hashlib
import tempfile

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ColorAnalyzer:
    """
    Advanced color analysis for album artwork.
    Extracts dominant colors and determines optimal template selection.
    """
    
    def __init__(self):
        """Initialize color analyzer with optimization settings."""
        self.sample_size = (150, 150)  # Resize for faster analysis
        self.color_tolerance = 30      # Color similarity threshold
        self.min_color_percentage = 5  # Minimum color presence (%)
        logger.info("Color analyzer initialized")
    
    def analyze_album_art(self, image_path_or_url: str) -> Dict[str, Any]:
        """
        Analyze album artwork to extract dominant colors and characteristics.
        
        Args:
            image_path_or_url (str): Path to local image or URL to album art
            
        Returns:
            Dict[str, Any]: Color analysis results including primary/secondary colors
        """
        try:
            # Load and prepare image
            image = self._load_image(image_path_or_url)
            if not image:
                return self._get_default_color_analysis()
            
            # Resize for efficient processing
            image = image.resize(self.sample_size, Image.LANCZOS)
            image = image.convert('RGB')
            
            # Extract dominant colors
            dominant_colors = self._extract_dominant_colors(image)
            
            # Determine primary and secondary colors
            primary_color = dominant_colors[0] if dominant_colors else (128, 128, 128)
            secondary_color = dominant_colors[1] if len(dominant_colors) > 1 else (64, 64, 64)
            
            # Calculate image brightness
            brightness = self._calculate_brightness(image)
            
            # Determine contrast needs
            is_dark = brightness < 0.5
            is_light = brightness > 0.8
            
            analysis = {
                'primary_color': self._rgb_to_hex(primary_color),
                'secondary_color': self._rgb_to_hex(secondary_color),
                'primary_color_rgb': primary_color,
                'secondary_color_rgb': secondary_color,
                'brightness': brightness,
                'is_dark': is_dark,
                'is_light': is_light,
                'contrast_recommendation': 'light' if is_dark else 'dark',
                'dominant_colors': [self._rgb_to_hex(color) for color in dominant_colors[:5]],
                'color_temperature': self._get_color_temperature(primary_color),
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Color analysis complete - Primary: {analysis['primary_color']}, Secondary: {analysis['secondary_color']}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing album art colors: {str(e)}")
            return self._get_default_color_analysis()
    
    def _load_image(self, source: str) -> Optional[Image.Image]:
        """Load image from file path or URL."""
        try:
            if source.startswith(('http://', 'https://')):
                # Download from URL
                response = requests.get(source, timeout=10, stream=True)
                response.raise_for_status()
                return Image.open(io.BytesIO(response.content))
            else:
                # Load from local file
                return Image.open(source)
                
        except Exception as e:
            logger.error(f"Error loading image from {source}: {str(e)}")
            return None
    
    def _extract_dominant_colors(self, image: Image.Image, num_colors: int = 5) -> List[Tuple[int, int, int]]:
        """Extract dominant colors using quantization."""
        try:
            # Convert to palette mode to get dominant colors
            quantized = image.quantize(colors=num_colors)
            palette = quantized.getpalette()
            
            # Get color counts
            colors_with_counts = []
            for i in range(num_colors):
                r = palette[i * 3]
                g = palette[i * 3 + 1] 
                b = palette[i * 3 + 2]
                
                # Count pixels of this color
                color_mask = quantized.point(lambda p: 255 if p == i else 0, mode='1')
                count = sum(color_mask.getdata())
                
                if count > 0:
                    colors_with_counts.append(((r, g, b), count))
            
            # Sort by frequency and return colors
            colors_with_counts.sort(key=lambda x: x[1], reverse=True)
            return [color[0] for color in colors_with_counts]
            
        except Exception as e:
            logger.error(f"Error extracting dominant colors: {str(e)}")
            return [(128, 128, 128), (64, 64, 64)]
    
    def _calculate_brightness(self, image: Image.Image) -> float:
        """Calculate overall brightness of image (0.0 = dark, 1.0 = light)."""
        try:
            # Convert to grayscale and calculate mean
            grayscale = image.convert('L')
            pixels = list(grayscale.getdata())
            return sum(pixels) / (len(pixels) * 255.0)
            
        except Exception as e:
            logger.error(f"Error calculating brightness: {str(e)}")
            return 0.5  # Default to medium brightness
    
    def _get_color_temperature(self, rgb: Tuple[int, int, int]) -> str:
        """Determine if color is warm, cool, or neutral."""
        r, g, b = rgb
        
        if r > g and r > b:
            return 'warm'  # Red dominant
        elif b > r and b > g:
            return 'cool'  # Blue dominant
        elif g > r and g > b:
            return 'neutral'  # Green dominant
        else:
            return 'neutral'  # Balanced
    
    def _rgb_to_hex(self, rgb: Tuple[int, int, int]) -> str:
        """Convert RGB tuple to hex string."""
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
    
    def _get_default_color_analysis(self) -> Dict[str, Any]:
        """Return default color analysis when processing fails."""
        return {
            'primary_color': '#808080',
            'secondary_color': '#404040', 
            'primary_color_rgb': (128, 128, 128),
            'secondary_color_rgb': (64, 64, 64),
            'brightness': 0.5,
            'is_dark': False,
            'is_light': False,
            'contrast_recommendation': 'dark',
            'dominant_colors': ['#808080', '#404040'],
            'color_temperature': 'neutral',
            'analysis_timestamp': datetime.now().isoformat()
        }


class PromoImageComposer:
    """
    Composes promotional images by combining album art with template borders
    and overlaying artist/song text with optimal formatting.
    """
    
    def __init__(self):
        """Initialize image composer with settings."""
        self.output_size = (2000, 2000)  # Universal square format per content pipeline design
        self.artwork_size = (1200, 1200)  # Album art size within canvas (60% of 2000)
        # Font paths - try project fonts first, then system fonts
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        frontend_fonts = os.path.join(base_dir, '..', 'frontend', 'public', 'fonts')
        self.font_paths = {
            'regular': os.path.join(frontend_fonts, 'NatomPro-Regular.otf'),
            'bold': os.path.join(frontend_fonts, 'NatomPro-Bold.otf')
        }
        self.min_font_size = 24
        self.max_font_size = 72
        self.text_margin = 20
        
        logger.info("Promo image composer initialized")
    
    def create_promo_image(self, album_art_path: str, template_path: str, 
                          artist_name: str, song_title: str, 
                          color_analysis: Dict[str, Any]) -> Optional[str]:
        """
        Create promotional image by compositing album art with template and text.
        
        Args:
            album_art_path (str): Path to album artwork
            template_path (str): Path to promo card template
            artist_name (str): Artist name for overlay
            song_title (str): Song title for overlay
            color_analysis (Dict[str, Any]): Color analysis results
            
        Returns:
            Optional[str]: Path to generated promo image or None if failed
        """
        try:
            # Load images
            album_art = self._load_and_prepare_artwork(album_art_path)
            template = self._load_template(template_path)
            
            if not album_art or not template:
                logger.error("Failed to load album art or template")
                return None
            
            # Resize template to output size
            template = template.resize(self.output_size, Image.LANCZOS)
            
            # Calculate artwork position (centered)
            art_x = (self.output_size[0] - self.artwork_size[0]) // 2
            art_y = (self.output_size[1] - self.artwork_size[1]) // 2 - 50  # Slightly above center
            
            # Resize and paste album art
            album_art_resized = album_art.resize(self.artwork_size, Image.LANCZOS)
            
            # Paste with alpha if available
            if album_art_resized.mode in ('RGBA', 'LA'):
                template.paste(album_art_resized, (art_x, art_y), album_art_resized)
            else:
                template.paste(album_art_resized, (art_x, art_y))
            
            # Add text overlays
            final_image = self._add_text_overlays(
                template, artist_name, song_title, color_analysis
            )
            
            # Save to temporary file
            output_path = self._generate_output_path(artist_name, song_title)
            final_image.save(output_path, 'PNG', quality=95)
            
            logger.info(f"Promo image created: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error creating promo image: {str(e)}")
            return None
    
    def _load_and_prepare_artwork(self, artwork_path: str) -> Optional[Image.Image]:
        """Load and prepare album artwork."""
        try:
            image = Image.open(artwork_path)
            
            # Convert to RGB if needed
            if image.mode in ('RGBA', 'P'):
                # Create white background for transparency
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            return image
            
        except Exception as e:
            logger.error(f"Error preparing artwork: {str(e)}")
            return None
    
    def _load_template(self, template_path: str) -> Optional[Image.Image]:
        """Load promo card template."""
        try:
            template = Image.open(template_path)
            return template.convert('RGBA')  # Ensure alpha channel for compositing
            
        except Exception as e:
            logger.error(f"Error loading template: {str(e)}")
            return None
    
    def _add_text_overlays(self, image: Image.Image, artist_name: str, 
                          song_title: str, color_analysis: Dict[str, Any]) -> Image.Image:
        """Add artist name and song title text overlays."""
        try:
            draw = ImageDraw.Draw(image)
            
            # Determine text color based on template brightness
            text_color = self._get_optimal_text_color(color_analysis)
            
            # Calculate text positions
            image_width, image_height = image.size
            
            # Artist name position (above artwork)
            artist_y = 50
            artist_font_size = self._calculate_font_size(artist_name, image_width - 2 * self.text_margin)
            artist_font = self._get_font(artist_font_size, bold=True)
            
            # Song title position (below artwork) 
            title_y = image_height - 150
            title_font_size = self._calculate_font_size(song_title, image_width - 2 * self.text_margin)
            title_font = self._get_font(title_font_size, bold=False)
            
            # Draw artist name (centered)
            artist_bbox = draw.textbbox((0, 0), artist_name, font=artist_font)
            artist_width = artist_bbox[2] - artist_bbox[0]
            artist_x = (image_width - artist_width) // 2
            
            draw.text((artist_x, artist_y), artist_name, fill=text_color, font=artist_font)
            
            # Draw song title (centered)
            title_bbox = draw.textbbox((0, 0), song_title, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            title_x = (image_width - title_width) // 2
            
            draw.text((title_x, title_y), song_title, fill=text_color, font=title_font)
            
            return image
            
        except Exception as e:
            logger.error(f"Error adding text overlays: {str(e)}")
            return image  # Return original image if text fails
    
    def _get_optimal_text_color(self, color_analysis: Dict[str, Any]) -> str:
        """Determine optimal text color based on background."""
        if color_analysis.get('is_light', False):
            return '#000000'  # Black text on light background
        else:
            return '#FFFFFF'  # White text on dark background
    
    def _calculate_font_size(self, text: str, max_width: int) -> int:
        """Calculate optimal font size to fit text within width."""
        for font_size in range(self.max_font_size, self.min_font_size - 1, -2):
            font = self._get_font(font_size)
            if font:
                # Create temporary draw object to measure text
                temp_img = Image.new('RGB', (1, 1))
                temp_draw = ImageDraw.Draw(temp_img)
                bbox = temp_draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                
                if text_width <= max_width:
                    return font_size
        
        return self.min_font_size  # Fallback to minimum
    
    def _get_font(self, size: int, bold: bool = False) -> Optional[ImageFont.ImageFont]:
        """Load font with specified size."""
        try:
            font_path = self.font_paths['bold' if bold else 'regular']
            
            # Check if font file exists, otherwise use default
            if os.path.exists(font_path):
                return ImageFont.truetype(font_path, size)
            else:
                # Fallback to default font
                return ImageFont.load_default()
                
        except Exception as e:
            logger.error(f"Error loading font: {str(e)}")
            return ImageFont.load_default()
    
    def _generate_output_path(self, artist_name: str, song_title: str) -> str:
        """Generate unique output path for promo image."""
        # Create safe filename
        safe_artist = "".join(c for c in artist_name if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_title = "".join(c for c in song_title if c.isalnum() or c in (' ', '-', '_')).strip()
        
        # Generate hash for uniqueness
        content_hash = hashlib.md5(f"{artist_name}_{song_title}_{datetime.now()}".encode()).hexdigest()[:8]
        
        filename = f"promo_{safe_artist}_{safe_title}_{content_hash}.png"
        
        # Use temp directory
        temp_dir = tempfile.gettempdir()
        return os.path.join(temp_dir, filename)


# Global instances
color_analyzer = ColorAnalyzer()
image_composer = PromoImageComposer()


# Convenience functions for easy integration
def analyze_album_colors(image_source: str) -> Dict[str, Any]:
    """
    Convenience function to analyze album art colors.
    
    Args:
        image_source (str): Path or URL to album artwork
        
    Returns:
        Dict[str, Any]: Color analysis results
    """
    return color_analyzer.analyze_album_art(image_source)


def create_promotional_image(album_art_path: str, template_path: str, 
                           artist_name: str, song_title: str) -> Optional[str]:
    """
    Convenience function to create promotional image.
    
    Args:
        album_art_path (str): Path to album artwork
        template_path (str): Path to template
        artist_name (str): Artist name
        song_title (str): Song title
        
    Returns:
        Optional[str]: Path to generated image or None
    """
    # Analyze colors first
    color_analysis = analyze_album_colors(album_art_path)
    
    # Create promotional image
    return image_composer.create_promo_image(
        album_art_path, template_path, artist_name, song_title, color_analysis
    )
