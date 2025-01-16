import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
from datetime import timedelta
import re
import queue
from processing import AudioProcessor

# Configure appearance
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class TimeRangeFrame(ctk.CTkFrame):
    def __init__(self, parent, index, delete_callback, video_duration=None):
        super().__init__(parent, fg_color="transparent")
        self.index = index
        self.video_duration = video_duration
        
        # Container
        self.container = ctk.CTkFrame(
            self,
            corner_radius=10,
            fg_color=("white", "gray20")
        )
        self.container.pack(fill="x", pady=5, padx=5)
        
        # Range label
        ctk.CTkLabel(
            self.container,
            text=f"Range {index + 1}",
            font=("Helvetica", 14, "bold")
        ).grid(row=0, column=0, padx=(15, 15), pady=10)
        
        # Time entries frame
        time_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        time_frame.grid(row=0, column=1, sticky='ew')
        
        # Start time
        ctk.CTkLabel(
            time_frame,
            text="Start:",
            font=("Helvetica", 12)
        ).pack(side="left", padx=5)
        
        self.start_time = ctk.CTkEntry(
            time_frame,
            width=100,
            placeholder_text="HH:MM:SS"
        )
        self.start_time.insert(0, "00:00:00")
        self.start_time.pack(side="left", padx=5)
        
        # End time
        ctk.CTkLabel(
            time_frame,
            text="End:",
            font=("Helvetica", 12)
        ).pack(side="left", padx=5)
        
        self.end_time = ctk.CTkEntry(
            time_frame,
            width=100,
            placeholder_text="HH:MM:SS"
        )
        self.end_time.insert(0, "00:00:00")
        self.end_time.pack(side="left", padx=5)
        
        # Delete button
        delete_btn = ctk.CTkButton(
            self.container,
            text="✕",
            command=lambda: delete_callback(self),
            width=30,
            fg_color="#ff4444",
            hover_color="#cc0000"
        )
        delete_btn.grid(row=0, column=2, padx=(15, 15))
        
        # Error label
        self.error_label = ctk.CTkLabel(
            self.container,
            text="",
            text_color="#ff4444",
            font=("Helvetica", 10)
        )
        self.error_label.grid(row=1, column=0, columnspan=3, pady=(0, 10))
        
    def validate_time(self, time_str):
        if time_str == "":
            return True
        time_pattern = r'^([0-9]{0,2}:)?([0-9]{0,2}:)?[0-9]{0,2}$'
        return bool(re.match(time_pattern, time_str))
        
    def get_times(self):
        try:
            start = self.parse_time(self.start_time.get())
            end = self.parse_time(self.end_time.get())
            
            if end <= start:
                raise ValueError("End time must be after start time")
                
            if self.video_duration:
                video_end = self.parse_time(self.video_duration)
                if start > video_end or end > video_end:
                    raise ValueError("Time range exceeds video duration")
                    
            self.error_label.configure(text="")
            return (self.start_time.get(), self.end_time.get())
            
        except ValueError as e:
            self.error_label.configure(text=str(e))
            return None
            
    @staticmethod
    def parse_time(time_str):
        try:
            parts = time_str.split(':')
            if len(parts) == 3:
                h, m, s = map(int, parts)
                return timedelta(hours=h, minutes=m, seconds=s).total_seconds()
            raise ValueError("Invalid time format")
        except:
            raise ValueError("Invalid time format (Use HH:MM:SS)")
class AudioProcessorUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Initialize variables
        self.video_path = None
        self.output_path = None
        self.duration = "00:00:00"
        self.ranges = []
        
        # Initialize processor
        self.processor = AudioProcessor(self.message_callback)
        self.message_queue = queue.Queue()

        self.setup_ui()
        self.check_queue()

    def setup_ui(self):
        self.title("Background Music Remover")
        self.geometry('1100x800')
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.create_header()
        self.create_file_section()
        self.create_ranges_section()
        self.create_controls()
        self.create_footer()

    def create_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=20, pady=(20,10), sticky="ew")
        
        ctk.CTkLabel(
            header,
            text="Background Music Remover",
            font=("Helvetica", 32, "bold")
        ).pack()
        
        ctk.CTkLabel(
            header,
            text="Remove background music while keeping vocals",
            font=("Helvetica", 16)
        ).pack()

    def create_file_section(self):
        file_frame = ctk.CTkFrame(self)
        file_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        # Section title
        ctk.CTkLabel(
            file_frame,
            text="File Selection",
            font=("Helvetica", 18, "bold")
        ).pack(pady=10)
        
        # Input video
        input_frame = ctk.CTkFrame(file_frame, fg_color="transparent")
        input_frame.pack(fill="x", padx=20, pady=5)
        
        self.browse_btn = ctk.CTkButton(
            input_frame,
            text="Browse Video",
            command=self.browse_video,
            font=("Helvetica", 12)
        )
        self.browse_btn.pack(side="left")

        self.file_label = ctk.CTkLabel(
            input_frame,
            text="No file selected",
            font=("Helvetica", 12)
        )
        self.file_label.pack(side="left", padx=10)

        # Output location
        output_frame = ctk.CTkFrame(file_frame, fg_color="transparent")
        output_frame.pack(fill="x", padx=20, pady=5)
        
        self.output_btn = ctk.CTkButton(
            output_frame,
            text="Save Output As",
            command=self.browse_output,
            font=("Helvetica", 12)
        )
        self.output_btn.pack(side="left")

        self.output_label = ctk.CTkLabel(
            output_frame,
            text="No output location selected",
            font=("Helvetica", 12)
        )
        self.output_label.pack(side="left", padx=10)

    def create_ranges_section(self):
        ranges_frame = ctk.CTkFrame(self)
        ranges_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        
        # Section title
        ctk.CTkLabel(
            ranges_frame,
            text="Time Ranges",
            font=("Helvetica", 18, "bold")
        ).pack(pady=10)
        
        add_range_btn = ctk.CTkButton(
            ranges_frame,
            text="+ Add Time Range",
            command=self.add_range,
            font=("Helvetica", 12)
        )
        add_range_btn.pack(pady=10)

        # Scrollable container
        self.ranges_canvas = ctk.CTkScrollableFrame(
            ranges_frame,
            fg_color="transparent"
        )
        self.ranges_canvas.pack(fill="both", expand=True, padx=10, pady=10)

        # Add initial range
        self.add_range()

    def create_controls(self):
        controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        controls_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        # Buttons
        button_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=10)

        self.process_btn = ctk.CTkButton(
            button_frame,
            text="▶ Process Video",
            command=self.start_processing,
            font=("Helvetica", 14, "bold"),
            height=40,
            fg_color="#00c853",
            hover_color="#00a844"
        )
        self.process_btn.pack(side="left", padx=5)

        self.cancel_btn = ctk.CTkButton(
            button_frame,
            text="✕ Cancel",
            command=self.cancel_processing,
            font=("Helvetica", 14, "bold"),
            height=40,
            fg_color="#ff4444",
            hover_color="#cc0000",
            state="disabled"
        )
        self.cancel_btn.pack(side="left", padx=5)

        # Progress area
        self.progress = ctk.CTkProgressBar(controls_frame)
        self.progress.pack(fill="x", pady=5)
        self.progress.set(0)

        self.status_label = ctk.CTkLabel(
            controls_frame,
            text="Ready to process",
            font=("Helvetica", 12)
        )
        self.status_label.pack()

    def create_footer(self):
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=4, column=0, padx=20, pady=(10,20), sticky="ew")

        ctk.CTkLabel(
            footer,
            text="Created by Devashish Sharma",
            font=("Helvetica", 10)
        ).pack(side="right")

    def add_range(self):
        range_frame = TimeRangeFrame(
            self.ranges_canvas,
            len(self.ranges),
            self.delete_range,
            self.duration
        )
        range_frame.pack(fill="x")
        self.ranges.append(range_frame)

    def delete_range(self, range_frame):
        if len(self.ranges) > 1:
            self.ranges.remove(range_frame)
            range_frame.destroy()

    def browse_video(self):
        try:
            path = filedialog.askopenfilename(
                title="Select Video File",
                filetypes=[
                    ("Video files", "*.mp4 *.mkv *.avi"),
                    ("All files", "*.*")
                ]
            )
            if path:
                self.video_path = path
                self.file_label.configure(text=os.path.basename(path))
                self.processor.get_video_duration(path, self.update_duration)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load video: {str(e)}")

    def browse_output(self):
        try:
            default_name = "processed_video.mp4" if not self.video_path else \
                          os.path.splitext(os.path.basename(self.video_path))[0] + "_processed.mp4"
            
            path = filedialog.asksaveasfilename(
                title="Save Processed Video As",
                defaultextension=".mp4",
                filetypes=[("MP4 files", "*.mp4")],
                initialfile=default_name
            )
            if path:
                self.output_path = path
                self.output_label.configure(text=os.path.basename(path))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to set output location: {str(e)}")

    def update_duration(self, duration):
        self.duration = duration
        for range_frame in self.ranges:
            range_frame.video_duration = duration
            range_frame.end_time.delete(0, "end")
            range_frame.end_time.insert(0, duration)

    def message_callback(self, message):
        self.message_queue.put(message)

    def check_queue(self):
        try:
            while True:
                message = self.message_queue.get_nowait()
                message_type = message.get('type', '')
                
                if message_type == 'progress':
                    self.progress.set(message['value'] / 100)
                elif message_type == 'status':
                    self.status_label.configure(text=message['text'])
                elif message_type == 'error':
                    messagebox.showerror("Error", message['text'])
                elif message_type == 'complete':
                    self.processing = False
                    self.enable_controls()
                    messagebox.showinfo("Success", message['text'])
                    
        except queue.Empty:
            pass
            
        finally:
            self.after(100, self.check_queue)

    def start_processing(self):
        try:
            # Validate inputs
            if not self.video_path:
                raise ValueError("Please select an input video")
                
            if not self.output_path:
                raise ValueError("Please select an output location")
                
            # Get and validate time ranges
            ranges = []
            for range_frame in self.ranges:
                if range_frame.winfo_exists():
                    times = range_frame.get_times()
                    if times is None:
                        raise ValueError(f"Invalid time range in Range {range_frame.index + 1}")
                    ranges.append(times)
                    
            if not ranges:
                raise ValueError("No valid time ranges specified")
                
            # Disable controls
            self.process_btn.configure(state="disabled")
            self.cancel_btn.configure(state="normal")
            self.browse_btn.configure(state="disabled")
            self.output_btn.configure(state="disabled")
            
            # Start processing
            self.processor.start_processing(self.video_path, self.output_path, ranges)
            
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start processing: {str(e)}")

    def cancel_processing(self):
        self.processor.cancel_processing()
        self.cancel_btn.configure(state="disabled")
        self.status_label.configure(text="Cancelling...")
        
    def enable_controls(self):
        self.process_btn.configure(state="normal")
        self.cancel_btn.configure(state="disabled")
        self.browse_btn.configure(state="normal")
        self.output_btn.configure(state="normal")

if __name__ == "__main__":
    try:
        # Set DPI awareness for Windows
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass
            
        app = AudioProcessorUI()
        app.mainloop()
    except Exception as e:
        messagebox.showerror("Error", f"Application Error: {str(e)}")
        raise e