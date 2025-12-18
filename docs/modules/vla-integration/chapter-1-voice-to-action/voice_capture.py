"""
Voice input capture module for the Vision-Language-Action (VLA) system.

This module handles capturing voice input from various sources including
microphones, audio files, and streaming sources, with preprocessing for
optimal speech recognition.
"""

import asyncio
import logging
import wave
import pyaudio
import numpy as np
from datetime import datetime
from typing import Optional, Tuple, Union
from pathlib import Path
import tempfile
import os


class VoiceCapture:
    """
    Service for capturing voice input from various sources.
    """

    def __init__(self):
        """
        Initialize the voice capture service.
        """
        self.logger = logging.getLogger(__name__)

        # Audio configuration
        self.audio_format = pyaudio.paInt16  # 16-bit resolution
        self.channels = 1                   # 1 channel (mono)
        self.rate = 44100                   # 44.1kHz sampling rate
        self.chunk = 1024                   # Buffer size
        self.pyaudio_instance = pyaudio.PyAudio()

    def __del__(self):
        """
        Clean up PyAudio instance when object is destroyed.
        """
        if hasattr(self, 'pyaudio_instance'):
            self.pyaudio_instance.terminate()

    async def capture_from_microphone(self, duration: float = 5.0) -> str:
        """
        Capture voice input from the default microphone.

        Args:
            duration: Recording duration in seconds

        Returns:
            Path to the saved audio file
        """
        try:
            self.logger.info(f"Starting microphone capture for {duration} seconds...")

            # Open stream
            stream = self.pyaudio_instance.open(
                format=self.audio_format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk
            )

            frames = []

            # Record for specified duration
            for _ in range(0, int(self.rate / self.chunk * duration)):
                data = stream.read(self.chunk)
                frames.append(data)

            # Stop and close stream
            stream.stop_stream()
            stream.close()

            # Save to temporary file
            filename = f"temp_voice_capture_{int(datetime.now().timestamp())}.wav"
            filepath = await self._save_audio_frames(frames, filename)

            self.logger.info(f"Microphone capture completed: {filepath}")
            return filepath

        except Exception as e:
            self.logger.error(f"Error capturing from microphone: {str(e)}")
            raise

    async def capture_until_silence(self, max_duration: float = 10.0, silence_threshold: float = 500) -> str:
        """
        Capture voice input until a period of silence is detected.

        Args:
            max_duration: Maximum recording duration in seconds
            silence_threshold: Threshold below which audio is considered silence

        Returns:
            Path to the saved audio file
        """
        try:
            self.logger.info(f"Starting voice capture until silence (max {max_duration}s)...")

            stream = self.pyaudio_instance.open(
                format=self.audio_format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk
            )

            frames = []
            silent_chunks = 0
            max_silent_chunks = int(self.rate / self.chunk * 1.0)  # 1 second of silence
            total_chunks = int(self.rate / self.chunk * max_duration)

            for i in range(total_chunks):
                data = stream.read(self.chunk)
                frames.append(data)

                # Check for silence
                audio_data = np.frombuffer(data, dtype=np.int16)
                amplitude = np.abs(audio_data).mean()

                if amplitude < silence_threshold:
                    silent_chunks += 1
                    if silent_chunks >= max_silent_chunks:
                        self.logger.info(f"Silence detected after {i/(self.rate/self.chunk):.2f} seconds")
                        break
                else:
                    silent_chunks = 0  # Reset if not silent

            # Stop and close stream
            stream.stop_stream()
            stream.close()

            # Save to temporary file
            filename = f"temp_voice_capture_{int(datetime.now().timestamp())}.wav"
            filepath = await self._save_audio_frames(frames, filename)

            self.logger.info(f"Voice capture until silence completed: {filepath}")
            return filepath

        except Exception as e:
            self.logger.error(f"Error capturing until silence: {str(e)}")
            raise

    async def preprocess_audio(self, audio_file_path: str, normalize: bool = True,
                              remove_silence: bool = True) -> str:
        """
        Preprocess an audio file to improve speech recognition quality.

        Args:
            audio_file_path: Path to the input audio file
            normalize: Whether to normalize audio amplitude
            remove_silence: Whether to trim silence from beginning/end

        Returns:
            Path to the preprocessed audio file
        """
        try:
            import soundfile as sf

            # Read the audio file
            data, sample_rate = sf.read(audio_file_path)

            # Convert to mono if stereo
            if len(data.shape) > 1:
                data = np.mean(data, axis=1)

            # Normalize amplitude
            if normalize:
                data = data / np.max(np.abs(data))
                data = data * 0.8  # Reduce volume slightly to prevent clipping

            # Remove silence from beginning and end
            if remove_silence:
                data = self._remove_silence(data, sample_rate)

            # Save the preprocessed audio
            preprocessed_filename = f"preprocessed_{Path(audio_file_path).name}"
            preprocessed_path = Path(audio_file_path).parent / preprocessed_filename
            sf.write(str(preprocessed_path), data, sample_rate)

            self.logger.info(f"Audio preprocessing completed: {preprocessed_path}")
            return str(preprocessed_path)

        except Exception as e:
            self.logger.error(f"Error preprocessing audio: {str(e)}")
            # If preprocessing fails, return the original file
            return audio_file_path

    def _remove_silence(self, audio_data: np.ndarray, sample_rate: int,
                       silence_threshold: float = 0.01, chunk_size: int = 1024) -> np.ndarray:
        """
        Remove silence from the beginning and end of audio data.

        Args:
            audio_data: Audio data as numpy array
            sample_rate: Sample rate of the audio
            silence_threshold: Threshold below which audio is considered silence
            chunk_size: Size of chunks to analyze

        Returns:
            Audio data with silence removed from beginning and end
        """
        # Convert threshold to the range of the audio data
        threshold = silence_threshold * np.max(np.abs(audio_data))

        # Find the start of non-silent audio
        start_idx = 0
        for i in range(0, len(audio_data), chunk_size):
            chunk = audio_data[i:i + chunk_size]
            if np.max(np.abs(chunk)) > threshold:
                start_idx = i
                break

        # Find the end of non-silent audio
        end_idx = len(audio_data)
        for i in range(len(audio_data) - 1, -1, -chunk_size):
            chunk_start = max(0, i - chunk_size + 1)
            chunk = audio_data[chunk_start:i + 1]
            if np.max(np.abs(chunk)) > threshold:
                end_idx = min(len(audio_data), i + chunk_size)
                break

        return audio_data[start_idx:end_idx]

    async def _save_audio_frames(self, frames: list, filename: str) -> str:
        """
        Save audio frames to a WAV file.

        Args:
            frames: List of audio frames
            filename: Name of the file to save

        Returns:
            Path to the saved file
        """
        filepath = Path(tempfile.gettempdir()) / filename

        with wave.open(str(filepath), 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.pyaudio_instance.get_sample_size(self.audio_format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(frames))

        return str(filepath)

    def validate_audio_file(self, file_path: str) -> Tuple[bool, str]:
        """
        Validate an audio file to ensure it's suitable for processing.

        Args:
            file_path: Path to the audio file

        Returns:
            Tuple of (is_valid, validation_message)
        """
        try:
            # Check if file exists
            if not Path(file_path).exists():
                return False, f"File does not exist: {file_path}"

            # Check file size (too small might indicate empty recording)
            file_size = Path(file_path).stat().st_size
            if file_size < 1024:  # Less than 1KB
                return False, f"File too small ({file_size} bytes), may be empty"

            # Try to open as WAV to verify it's a valid audio file
            with wave.open(file_path, 'rb') as wf:
                params = wf.getparams()
                n_channels, sampwidth, framerate, n_frames = params[:4]

                # Validate basic parameters
                if n_channels != 1:  # Whisper works best with mono
                    self.logger.warning(f"Audio is not mono: {n_channels} channels")
                if sampwidth not in [2, 4]:  # 16-bit or 32-bit
                    return False, f"Unsupported sample width: {sampwidth * 8} bits"
                if framerate not in [8000, 16000, 22050, 44100, 48000]:  # Common rates
                    self.logger.warning(f"Uncommon sample rate: {framerate}Hz")

                duration = n_frames / float(framerate)
                if duration < 0.1:  # Less than 0.1 seconds is likely not speech
                    return False, f"Audio duration too short: {duration:.2f}s"
                if duration > 30:  # More than 30 seconds might be too long
                    self.logger.warning(f"Audio duration is long: {duration:.2f}s")

            return True, f"Valid audio file: {n_channels}ch, {framerate}Hz, {duration:.2f}s"

        except wave.Error:
            return False, f"Invalid WAV file: {file_path}"
        except Exception as e:
            return False, f"Error validating audio file: {str(e)}"


class VoiceCapturePipeline:
    """
    Complete pipeline for capturing and preparing voice input for processing.
    """

    def __init__(self):
        """
        Initialize the voice capture pipeline.
        """
        self.logger = logging.getLogger(__name__)
        self.capture_service = VoiceCapture()

    async def capture_voice_input(self, source: str = "microphone", **kwargs) -> str:
        """
        Capture voice input from the specified source.

        Args:
            source: Source of voice input ("microphone", "until_silence", or file path)
            **kwargs: Additional arguments for specific capture methods

        Returns:
            Path to the captured/preprocessed audio file
        """
        try:
            self.logger.info(f"Starting voice capture from: {source}")

            if source == "microphone":
                duration = kwargs.get("duration", 5.0)
                file_path = await self.capture_service.capture_from_microphone(duration)
            elif source == "until_silence":
                max_duration = kwargs.get("max_duration", 10.0)
                file_path = await self.capture_service.capture_until_silence(max_duration)
            elif Path(source).exists():
                # It's a file path, just return it
                file_path = source
            else:
                raise ValueError(f"Unknown capture source: {source}")

            # Validate the captured audio
            is_valid, validation_msg = self.capture_service.validate_audio_file(file_path)
            if not is_valid:
                raise ValueError(f"Invalid audio captured: {validation_msg}")

            self.logger.info(f"Voice capture completed: {validation_msg}")

            # Preprocess the audio for better recognition
            preprocessed_path = await self.capture_service.preprocess_audio(file_path)
            self.logger.info(f"Audio preprocessing completed: {preprocessed_path}")

            return preprocessed_path

        except Exception as e:
            self.logger.error(f"Error in voice capture pipeline: {str(e)}")
            raise


# Example usage and testing functions
async def example_voice_capture():
    """
    Example function demonstrating voice capture usage.
    """
    print("=== Voice Capture Example ===")

    # Initialize the capture pipeline
    pipeline = VoiceCapturePipeline()

    # Example 1: Capture from microphone for 5 seconds
    print("Example 1: Capturing from microphone for 5 seconds...")
    try:
        # Note: In a real implementation, this would actually record
        # For this example, we'll just show the structure
        print("Would capture from microphone for 5 seconds")
        print("To actually run this, uncomment the code below:")
        print("# audio_file = await pipeline.capture_voice_input('microphone', duration=5.0)")
        print("# print(f'Captured audio file: {audio_file}')")
    except Exception as e:
        print(f"Error in microphone capture: {e}")

    # Example 2: Capture until silence
    print("\nExample 2: Capturing until silence detected...")
    try:
        print("Would capture until silence is detected")
        print("To actually run this, uncomment the code below:")
        print("# audio_file = await pipeline.capture_voice_input('until_silence', max_duration=10.0)")
        print("# print(f'Captured audio file: {audio_file}')")
    except Exception as e:
        print(f"Error in silence capture: {e}")

    # Example 3: Process an existing audio file
    print("\nExample 3: Processing existing audio file...")
    try:
        # This would be used with an actual file path
        print("Would process existing audio file")
        print("To actually run this, use:")
        print("# audio_file = await pipeline.capture_voice_input('/path/to/audio/file.wav')")
        print("# print(f'Processed audio file: {audio_file}')")
    except Exception as e:
        print(f"Error in file processing: {e}")


if __name__ == "__main__":
    # Run the example
    asyncio.run(example_voice_capture())