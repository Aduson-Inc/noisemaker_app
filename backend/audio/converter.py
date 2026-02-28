"""
Audio Converter Module
Handles WAV to MP3 conversion using ffmpeg.
"""

import subprocess
import logging
import os

logger = logging.getLogger(__name__)


def convert_wav_to_mp3(input_path: str, output_path: str) -> bool:
    """
    Convert WAV file to MP3 using ffmpeg.

    Args:
        input_path: Path to input WAV file
        output_path: Path for output MP3 file

    Returns:
        True on success, False on failure
    """
    try:
        result = subprocess.run(
            [
                "ffmpeg", "-i", input_path,
                "-codec:a", "libmp3lame",
                "-qscale:a", "2",
                "-y",  # Overwrite output
                output_path,
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode != 0:
            logger.error(f"ffmpeg conversion failed: {result.stderr}")
            return False

        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            logger.error("Output MP3 file is empty or missing")
            return False

        logger.info(f"Converted WAV to MP3: {output_path}")
        return True

    except FileNotFoundError:
        logger.error("ffmpeg not installed or not in PATH")
        return False
    except subprocess.TimeoutExpired:
        logger.error("ffmpeg conversion timed out (120s)")
        return False
    except Exception as e:
        logger.error(f"Conversion error: {e}")
        return False
