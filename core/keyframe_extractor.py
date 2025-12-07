"""Keyframe extraction using OpenCV"""

import cv2
import numpy as np
from pathlib import Path
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)


class KeyframeExtractor:
    """Extract keyframes from video using motion and histogram analysis"""
    
    def __init__(self, motion_threshold=30, histogram_threshold=0.7, 
                 min_frame_interval=30, max_keyframes=20):
        self.motion_threshold = motion_threshold
        self.histogram_threshold = histogram_threshold
        self.min_frame_interval = min_frame_interval
        self.max_keyframes = max_keyframes
        
    def extract_keyframes(self, video_path: str, output_dir: str = None) -> List[Tuple[int, str]]:
        """
        Extract keyframes from video
        
        Args:
            video_path: Path to input video file
            output_dir: Directory to save keyframes (optional)
            
        Returns:
            List of tuples (frame_number, frame_path)
        """
        logger.info(f"Starting keyframe extraction from {video_path}")
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")
        
        keyframes = []
        prev_gray = None
        prev_hist = None
        frame_count = 0
        last_keyframe_idx = -self.min_frame_interval
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        logger.info(f"Video info: {total_frames} frames, {fps} fps")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            # Convert to grayscale for analysis
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Calculate histogram
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            hist = cv2.normalize(hist, hist).flatten()
            
            is_keyframe = False
            
            if prev_gray is not None and frame_count - last_keyframe_idx >= self.min_frame_interval:
                # Motion detection using frame difference
                frame_diff = cv2.absdiff(gray, prev_gray)
                motion_score = np.mean(frame_diff)
                
                # Scene change detection using histogram comparison
                hist_similarity = cv2.compareHist(hist, prev_hist, cv2.HISTCMP_CORREL)
                
                # Check if this is a keyframe
                if motion_score > self.motion_threshold or hist_similarity < self.histogram_threshold:
                    is_keyframe = True
                    
            # Always include first frame
            if frame_count == 0:
                is_keyframe = True
                
            if is_keyframe:
                if output_dir:
                    # Save keyframe
                    Path(output_dir).mkdir(parents=True, exist_ok=True)
                    timestamp = frame_count / fps
                    filename = f"keyframe_{len(keyframes):03d}_t{timestamp:.2f}s.jpg"
                    filepath = str(Path(output_dir) / filename)
                    cv2.imwrite(filepath, frame)
                    keyframes.append((frame_count, filepath))
                    logger.info(f"Extracted keyframe {len(keyframes)} at frame {frame_count} ({timestamp:.2f}s)")
                else:
                    keyframes.append((frame_count, frame))
                    
                last_keyframe_idx = frame_count
                
                # Stop if we've reached max keyframes
                if len(keyframes) >= self.max_keyframes:
                    logger.info(f"Reached maximum keyframes limit: {self.max_keyframes}")
                    break
                    
            prev_gray = gray
            prev_hist = hist
            frame_count += 1
            
        cap.release()
        
        # If we have very few keyframes, add some evenly spaced ones
        if len(keyframes) < 5:
            logger.info("Too few keyframes detected, adding evenly spaced frames")
            keyframes = self._add_evenly_spaced_frames(video_path, output_dir, min(10, self.max_keyframes))
            
        logger.info(f"Extracted {len(keyframes)} keyframes total")
        return keyframes
    
    def _add_evenly_spaced_frames(self, video_path: str, output_dir: str, count: int) -> List[Tuple[int, str]]:
        """Extract evenly spaced frames as fallback"""
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        keyframes = []
        frame_indices = np.linspace(0, total_frames - 1, count, dtype=int)
        
        for idx in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if ret:
                if output_dir:
                    Path(output_dir).mkdir(parents=True, exist_ok=True)
                    timestamp = idx / fps
                    filename = f"keyframe_{len(keyframes):03d}_t{timestamp:.2f}s.jpg"
                    filepath = str(Path(output_dir) / filename)
                    cv2.imwrite(filepath, frame)
                    keyframes.append((idx, filepath))
                else:
                    keyframes.append((idx, frame))
                    
        cap.release()
        return keyframes
