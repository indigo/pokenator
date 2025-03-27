"""Voice module for the Pokenator game.

This module handles text-to-speech functionality for the game.
"""
from pathlib import Path
import os
import hashlib
import re
import time
from typing import Optional, Dict, List, Set
import csv

# Try to import pygame for audio playback
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("[VOICE] Pygame not available. Audio playback disabled.")
except Exception:
    PYGAME_AVAILABLE = False
    print("[VOICE] Error initializing pygame. Audio playback disabled.")

class VoiceEngine:
    """Voice engine for text-to-speech functionality."""
    
    def __init__(self, enabled: bool = False, language: str = 'fr', 
                 audio_dir: Optional[Path] = None,
                 use_pregenerated: bool = True):
        """Initialize the voice engine.
        
        Args:
            enabled: Whether voice output is enabled
            language: Language code (e.g., 'fr' for French)
            audio_dir: Directory containing pre-generated audio files
            use_pregenerated: Whether to use pre-generated audio files
        """
        self.enabled = enabled
        self.language = language
        self.audio_dir = audio_dir or Path(__file__).parent.parent / 'audio'
        self.use_pregenerated = use_pregenerated
        
        # Voice engine will be initialized when needed
        self._engine = None
        self._initialized = False
        self._available_files = set()
        self.voice_mapping = self._load_voice_mapping()
        
        # Initialize pygame mixer if available
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.init()
                self.mixer_initialized = True
            except Exception as e:
                print(f"[VOICE] Failed to initialize pygame mixer: {e}")
                self.mixer_initialized = False
        else:
            self.mixer_initialized = False
        
        # Load available audio files if the directory exists
        if self.use_pregenerated and self.audio_dir.exists():
            self._load_available_files()
    
    def _load_available_files(self) -> None:
        """Load the list of available pre-generated audio files."""
        self._available_files = set()
        if self.audio_dir.exists():
            for file in self.audio_dir.glob(f"**/{self.language}/*.mp3"):
                self._available_files.add(file.stem)
    
    def _load_voice_mapping(self) -> Dict[str, str]:
        """Load voice mapping from CSV file.
        
        Returns:
            Dictionary mapping keys to audio filenames
        """
        mapping = {}
        mapping_file = self.audio_dir / self.language / 'voice_mapping.csv'
        
        if mapping_file.exists():
            try:
                with open(mapping_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        mapping[row['key']] = row['filename']
                        # Also map the text directly to the filename for backward compatibility
                        mapping[row['text']] = row['filename']
                print(f"[VOICE] Loaded {len(mapping)} voice mappings from {mapping_file}")
            except Exception as e:
                print(f"[VOICE] Error loading voice mapping: {e}")
        
        return mapping
    
    def _get_audio_path(self, text: str) -> Path:
        """Generate a deterministic filename based on the text content.
        
        Args:
            text: Text to generate filename for
            
        Returns:
            Path to the audio file
        """
        # First check if we have a mapping for this text
        if text in self.voice_mapping:
            return self.audio_dir / self.language / self.voice_mapping[text]
        
        # Check for special keys (evolution questions)
        if "peut évoluer" in text:
            if "evolution_can" in self.voice_mapping:
                return self.audio_dir / self.language / self.voice_mapping["evolution_can"]
        
        if "forme finale" in text or "ne peut plus évoluer" in text:
            if "evolution_cannot" in self.voice_mapping:
                return self.audio_dir / self.language / self.voice_mapping["evolution_cannot"]
        
        # Fall back to the hash-based filename
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        prefix = re.sub(r'[^a-zA-Z0-9]', '_', text[:30].lower())
        filename = f"{prefix}_{text_hash[:8]}.mp3"
        return self.audio_dir / self.language / filename
    
    def initialize(self) -> bool:
        """Initialize the voice engine.
        
        This method will be implemented when we add voice support.
        It should initialize the TTS engine and return True if successful.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        # If using pre-generated files, just check if the directory exists
        if self.use_pregenerated:
            if not self.audio_dir.exists():
                print(f"[VOICE] Audio directory not found: {self.audio_dir}")
                return False
            self._load_available_files()
            self._initialized = True
            return True
            
        # This will be implemented when we add live TTS support
        self._initialized = False
        return self._initialized
    
    def speak(self, text: str, blocking: bool = True) -> bool:
        """Convert text to speech and play it.
        
        Args:
            text: Text to convert to speech
            blocking: Whether to block until speech is complete
            
        Returns:
            True if speech was generated and played, False otherwise
        """
        if not self.enabled:
            return False
            
        if not self._initialized and not self.initialize():
            return False
        
        # If using pre-generated files, try to find and play the file
        if self.use_pregenerated:
            audio_path = self._get_audio_path(text)
            if audio_path.exists():
                # Play the audio file using pygame if available
                if PYGAME_AVAILABLE:
                    try:
                        pygame.mixer.music.load(str(audio_path))
                        pygame.mixer.music.play()
                        
                        # If blocking, wait for playback to complete
                        if blocking:
                            while pygame.mixer.music.get_busy():
                                time.sleep(0.1)
                        
                        return True
                    except Exception as e:
                        print(f"[VOICE] Error playing audio: {e}")
                        # Fall back to text output
                        print(f"[VOICE] Text: {text}")
                        return False
                else:
                    # No pygame, just print the text
                    print(f"[VOICE] Would play: {audio_path}")
                    print(f"[VOICE] Text: {text}")
                    return True
            else:
                print(f"[VOICE] Audio file not found: {audio_path}")
                # Fall back to text output
                print(f"[VOICE] Text: {text}")
                return False
        
        # This will be implemented when we add live TTS support
        print(f"[VOICE] Would speak: {text}")
        return True
    
    def generate_audio_file(self, text: str, force: bool = False) -> Optional[Path]:
        """Generate an audio file for the given text.
        
        Args:
            text: Text to convert to speech
            force: Whether to force regeneration if the file already exists
            
        Returns:
            Path to the generated audio file, or None if generation failed
        """
        if not self._initialized and not self.initialize():
            return None
            
        audio_path = self._get_audio_path(text)
        
        # Create the directory if it doesn't exist
        audio_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Skip if the file already exists and we're not forcing regeneration
        if not force and audio_path.exists():
            return audio_path
            
        # This will be implemented when we add TTS support
        print(f"[VOICE] Would generate audio file: {audio_path}")
        print(f"[VOICE] Text: {text}")
        
        # For now, return None to indicate that generation is not implemented
        return None
    
    def set_language(self, language: str) -> bool:
        """Set the language for text-to-speech.
        
        Args:
            language: Language code (e.g., 'fr' for French)
            
        Returns:
            True if language was set successfully, False otherwise
        """
        if self.language != language:
            self.language = language
            if self.use_pregenerated:
                self._load_available_files()
                self.voice_mapping = self._load_voice_mapping()
        return True
    
    def enable(self) -> None:
        """Enable voice output."""
        self.enabled = True
        
    def disable(self) -> None:
        """Disable voice output."""
        self.enabled = False
        
    def is_enabled(self) -> bool:
        """Check if voice output is enabled."""
        return self.enabled


# Create a default voice engine instance
default_engine = VoiceEngine(enabled=False)

def speak(text: str, blocking: bool = True) -> bool:
    """Convert text to speech and play it using the default engine.
    
    Args:
        text: Text to convert to speech
        blocking: Whether to block until speech is complete
        
    Returns:
        True if speech was generated and played, False otherwise
    """
    return default_engine.speak(text, blocking)

def generate_audio_file(text: str, force: bool = False) -> Optional[Path]:
    """Generate an audio file for the given text using the default engine.
    
    Args:
        text: Text to convert to speech
        force: Whether to force regeneration if the file already exists
        
    Returns:
        Path to the generated audio file, or None if generation failed
    """
    return default_engine.generate_audio_file(text, force)

def enable_voice() -> None:
    """Enable voice output for the default engine."""
    default_engine.enable()
    
def disable_voice() -> None:
    """Disable voice output for the default engine."""
    default_engine.disable()
    
def is_voice_enabled() -> bool:
    """Check if voice output is enabled for the default engine."""
    return default_engine.is_enabled()
    
def set_language(language: str) -> bool:
    """Set the language for the default engine.
    
    Args:
        language: Language code (e.g., 'fr' for French)
        
    Returns:
        True if language was set successfully, False otherwise
    """
    return default_engine.set_language(language)
