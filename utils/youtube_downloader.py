"""YouTube video downloader utility"""

import logging
from pathlib import Path
from typing import Tuple, Optional
import yt_dlp
import re

logger = logging.getLogger(__name__)


class YouTubeDownloader:
    """Handle YouTube video downloads"""
    
    def __init__(self, output_dir: str = "uploads"):
        """
        Initialize YouTube downloader
        
        Args:
            output_dir: Directory to save downloaded videos
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def is_valid_youtube_url(url: str) -> bool:
        """
        Check if URL is a valid YouTube URL
        
        Args:
            url: URL string to validate
            
        Returns:
            True if valid YouTube URL, False otherwise
        """
        youtube_patterns = [
            r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+',
            r'(https?://)?(www\.)?youtube\.com/watch\?v=[\w-]+',
            r'(https?://)?(www\.)?youtu\.be/[\w-]+',
            r'(https?://)?(www\.)?youtube\.com/embed/[\w-]+',
            r'(https?://)?(www\.)?youtube\.com/v/[\w-]+',
        ]
        
        return any(re.match(pattern, url) for pattern in youtube_patterns)
    
    def get_video_info(self, url: str) -> Optional[dict]:
        """
        Get video information without downloading
        
        Args:
            url: YouTube video URL
            
        Returns:
            Dictionary with video info or None if error
        """
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return {
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'duration_formatted': self._format_duration(info.get('duration', 0)),
                    'uploader': info.get('uploader', 'Unknown'),
                    'view_count': info.get('view_count', 0),
                    'upload_date': info.get('upload_date', 'Unknown'),
                    'thumbnail': info.get('thumbnail', ''),
                }
        
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            return None
    
    def download_video(self, url: str, output_filename: str = None) -> Tuple[bool, str]:
        """
        Download YouTube video
        
        Args:
            url: YouTube video URL
            output_filename: Custom filename (without extension)
            
        Returns:
            Tuple of (success: bool, file_path or error_message: str)
        """
        try:
            logger.info(f"Starting YouTube download: {url}")
            
            # Validate URL
            if not self.is_valid_youtube_url(url):
                return False, "Invalid YouTube URL"
            
            # Generate output template
            if output_filename:
                output_template = str(self.output_dir / f"{output_filename}.%(ext)s")
            else:
                output_template = str(self.output_dir / "%(title)s_%(id)s.%(ext)s")
            
            # Download options
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': output_template,
                'quiet': False,
                'no_warnings': False,
                'merge_output_format': 'mp4',
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }],
            }
            
            # Download video
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                # Get downloaded file path
                if output_filename:
                    downloaded_file = self.output_dir / f"{output_filename}.mp4"
                else:
                    video_id = info.get('id', 'unknown')
                    title = info.get('title', 'video')
                    # Clean title for filename
                    safe_title = self._sanitize_filename(title)
                    downloaded_file = self.output_dir / f"{safe_title}_{video_id}.mp4"
                
                # Check if file exists
                if downloaded_file.exists():
                    logger.info(f"✅ Download complete: {downloaded_file}")
                    return True, str(downloaded_file)
                else:
                    # Try to find the file with any extension
                    possible_files = list(self.output_dir.glob(f"{output_filename}.*" if output_filename else "*"))
                    if possible_files:
                        downloaded_file = possible_files[0]
                        logger.info(f"✅ Download complete: {downloaded_file}")
                        return True, str(downloaded_file)
                    else:
                        return False, "Downloaded file not found"
        
        except Exception as e:
            error_msg = f"Download error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg
    
    @staticmethod
    def _format_duration(seconds: int) -> str:
        """Format duration in seconds to HH:MM:SS"""
        if not seconds:
            return "Unknown"
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"
    
    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """Remove invalid characters from filename and make URL-safe"""
        import re
        
        # Remove invalid characters
        invalid_chars = '<>:"/\\|?*#%&{}[]@!$\'^+=`~;,'
        for char in invalid_chars:
            filename = filename.replace(char, '')
        
        # Replace spaces and multiple underscores with single underscore
        filename = re.sub(r'[\s_]+', '_', filename)
        
        # Remove leading/trailing underscores
        filename = filename.strip('_')
        
        # Limit length
        return filename[:80]


# Test function
def main():
    """Test YouTube downloader"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python youtube_downloader.py <youtube_url>")
        sys.exit(1)
    
    url = sys.argv[1]
    
    downloader = YouTubeDownloader()
    
    # Get info
    print("📺 Getting video info...")
    info = downloader.get_video_info(url)
    
    if info:
        print(f"✅ Title: {info['title']}")
        print(f"✅ Duration: {info['duration_formatted']}")
        print(f"✅ Uploader: {info['uploader']}")
    
    # Download
    print("\n📥 Downloading video...")
    success, result = downloader.download_video(url)
    
    if success:
        print(f"✅ Success! File saved to: {result}")
    else:
        print(f"❌ Error: {result}")


if __name__ == "__main__":
    main()
