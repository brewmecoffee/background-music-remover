import os
import sys
import threading
import subprocess
import ffmpeg
from spleeter.separator import Separator
from pydub import AudioSegment
from datetime import timedelta
import tempfile
import shutil
import logging
from pathlib import Path

class AudioProcessor:
    def __init__(self, callback):
        self.callback = callback
        self.processing = False
        self.process_thread = None
        self.setup_logging()

    def setup_logging(self):
        """Setup logging for debugging"""
        log_path = self.get_app_data_path() / 'app.log'
        logging.basicConfig(
            filename=log_path,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    @staticmethod
    def get_app_data_path():
        """Get path for application data"""
        if sys.platform == 'win32':
            app_data = Path(os.getenv('APPDATA')) / 'BackgroundMusicRemover'
        else:
            app_data = Path.home() / '.BackgroundMusicRemover'
        
        app_data.mkdir(parents=True, exist_ok=True)
        return app_data

    @staticmethod
    def get_ffmpeg_path():
        """Get ffmpeg path"""
        return 'ffmpeg'

    def get_video_duration(self, video_path, duration_callback):
        """Get duration of input video"""
        try:
            probe = ffmpeg.probe(video_path)
            video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
            duration = float(probe['format']['duration'])
            
            hours = int(duration // 3600)
            minutes = int((duration % 3600) // 60)
            seconds = int(duration % 60)
            duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            
            logging.info(f"Video duration: {duration_str}")
            duration_callback(duration_str)
            
        except Exception as e:
            logging.error(f"Failed to get video duration: {str(e)}")
            self.callback({
                'type': 'error',
                'text': f"Failed to get video duration: {str(e)}"
            })

    def start_processing(self, video_path, output_path, ranges):
        """Start processing in a separate thread"""
        self.processing = True
        self.process_thread = threading.Thread(
            target=self._process_video,
            args=(video_path, output_path, ranges)
        )
        self.process_thread.daemon = True
        self.process_thread.start()
        logging.info("Started processing thread")

    def cancel_processing(self):
        """Cancel ongoing processing"""
        self.processing = False
        logging.info("Processing cancelled by user")

    def _create_temp_dir(self):
        """Create a temporary directory for processing"""
        temp_base = self.get_app_data_path() / 'temp'
        temp_base.mkdir(parents=True, exist_ok=True)
        return tempfile.mkdtemp(dir=temp_base)

    def _cleanup_temp_dir(self, temp_dir):
        """Clean up temporary directory"""
        try:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            logging.info(f"Cleaned up temp directory: {temp_dir}")
        except Exception as e:
            logging.error(f"Failed to cleanup temp directory: {str(e)}")

    def _process_video(self, video_path, output_path, ranges):
        """Main processing function"""
        temp_dir = self._create_temp_dir()
        try:
            logging.info(f"Starting video processing: {video_path}")
            
            # Extract audio
            self.callback({
                'type': 'status',
                'text': "Extracting audio..."
            })
            self.callback({
                'type': 'progress',
                'value': 0
            })

            temp_audio = os.path.join(temp_dir, "temp_audio.wav")
            ffmpeg_extract = [
                self.get_ffmpeg_path(),
                '-i', video_path,
                '-vn',  # No video
                '-acodec', 'pcm_s16le',  # PCM 16-bit output
                '-ar', '44100',  # 44.1kHz sampling rate
                '-ac', '2',  # Stereo
                '-y',  # Overwrite output
                temp_audio
            ]
            
            subprocess.run(ffmpeg_extract, check=True, capture_output=True)
            logging.info("Audio extraction complete")

            # Initialize Spleeter
            separator = Separator('spleeter:2stems')
            logging.info("Initialized Spleeter")

            # Load the full audio file
            audio = AudioSegment.from_wav(temp_audio)
            processed_audio = audio

            # Process each time range
            total_ranges = len(ranges)
            for idx, (start_time, end_time) in enumerate(ranges, 1):
                if not self.processing:
                    raise InterruptedError("Processing cancelled by user")

                self.callback({
                    'type': 'status',
                    'text': f"Processing range {idx}/{total_ranges}: {start_time} to {end_time}"
                })
                self.callback({
                    'type': 'progress',
                    'value': (idx - 1) * 90 / total_ranges
                })

                # Convert times to seconds
                start_sec = self._time_to_seconds(start_time)
                end_sec = self._time_to_seconds(end_time)

                # Extract segment to process
                process_part = audio[start_sec * 1000:end_sec * 1000]
                temp_process = os.path.join(temp_dir, "temp_process.wav")
                process_part.export(temp_process, format="wav")

                # Separate vocals
                separator.separate_to_file(temp_process, temp_dir)
                logging.info(f"Processed range {idx}: {start_time} - {end_time}")

                # Replace segment with processed audio
                vocals = AudioSegment.from_wav(os.path.join(temp_dir, "temp_process", "vocals.wav"))
                processed_audio = processed_audio[:start_sec * 1000] + vocals + processed_audio[end_sec * 1000:]

                self.callback({
                    'type': 'progress',
                    'value': idx * 90 / total_ranges
                })

            # Export final audio
            self.callback({
                'type': 'status',
                'text': "Creating final video..."
            })

            final_audio = os.path.join(temp_dir, "processed_audio.wav")
            processed_audio.export(final_audio, format="wav")

            # Combine with video
            ffmpeg_combine = [
                self.get_ffmpeg_path(),
                '-i', video_path,
                '-i', final_audio,
                '-c:v', 'copy',  # Copy video stream
                '-c:a', 'aac',   # AAC audio codec
                '-b:a', '192k',  # Audio bitrate
                '-map', '0:v:0', # Use video from first input
                '-map', '1:a:0', # Use audio from second input
                '-y',            # Overwrite output
                output_path
            ]
            
            subprocess.run(ffmpeg_combine, check=True, capture_output=True)
            logging.info("Final video creation complete")

            self.callback({
                'type': 'progress',
                'value': 100
            })

            self.callback({
                'type': 'complete',
                'text': f"Processing complete!\nOutput saved as: {output_path}"
            })

        except InterruptedError as e:
            logging.info("Processing cancelled")
            self.callback({
                'type': 'status',
                'text': "Processing cancelled"
            })
            self.callback({
                'type': 'complete',
                'text': "Processing was cancelled"
            })
        except subprocess.CalledProcessError as e:
            logging.error(f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}")
            self.callback({
                'type': 'error',
                'text': f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}"
            })
        except Exception as e:
            logging.error(f"Processing error: {str(e)}")
            self.callback({
                'type': 'error',
                'text': f"Error during processing: {str(e)}"
            })
            self.callback({
                'type': 'complete',
                'text': "Processing failed"
            })
        finally:
            self._cleanup_temp_dir(temp_dir)

    @staticmethod
    def _time_to_seconds(time_str):
        """Convert time string to seconds"""
        try:
            h, m, s = map(int, time_str.split(':'))
            return timedelta(hours=h, minutes=m, seconds=s).total_seconds()
        except ValueError as e:
            logging.error(f"Time conversion error: {str(e)}")
            raise ValueError(f"Invalid time format: {time_str}. Use HH:MM:SS format.")