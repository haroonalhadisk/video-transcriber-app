import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

def update_instagram_progress(gui_instance, value, status_text):
    """Update progress bar and status text for Instagram download"""
    gui_instance.root.after(0, lambda: gui_instance.instagram_progress.set(value))
    gui_instance.root.after(0, lambda: gui_instance.instagram_status.set(status_text))

def add_batch_instagram_features(gui_instance):
    """
    Add batch Instagram link processing functionality to the Instagram tab
    
    Args:
        gui_instance: Instance of VideoTranscriberGUI
    """
    # Find the Instagram tab
    instagram_tab = None
    for i in range(gui_instance.notebook.index("end")):
        if gui_instance.notebook.tab(i, "text") == "Instagram Download":
            instagram_tab = gui_instance.notebook.winfo_children()[i]
            break
    
    if not instagram_tab:
        return  # Instagram tab not found
    
    # Find the button frame in the Instagram tab
    button_frame = None
    for child in instagram_tab.winfo_children():
        if isinstance(child, ttk.Frame) and not isinstance(child, ttk.LabelFrame):
            if len(child.winfo_children()) > 0 and isinstance(child.winfo_children()[0], ttk.Button):
                button_frame = child
                break
    
    if not button_frame:
        # Create a new button frame if not found
        button_frame = ttk.Frame(instagram_tab)
        button_frame.pack(fill=tk.X, pady=10)
    
    # Add batch processing button to existing button frame
    ttk.Button(button_frame, text="Load URLs from File", 
              command=lambda: load_urls_from_file(gui_instance)).pack(side=tk.LEFT, padx=5)
    
    # Add batch processing variables
    gui_instance.is_batch_instagram_processing = False
    gui_instance.instagram_urls = []
    gui_instance.current_instagram_index = 0
    gui_instance.instagram_batch_thread = None

def load_urls_from_file(gui_instance):
    """
    Load Instagram URLs from a text file for batch processing
    """
    file_path = filedialog.askopenfilename(
        title="Select Text File with Instagram URLs",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    
    if not file_path:
        return
    
    try:
        with open(file_path, 'r') as file:
            urls = [line.strip() for line in file if line.strip()]
        
        # Filter valid URLs
        instagram_urls = []
        for url in urls:
            if "instagram.com" in url and ("/p/" in url or "/reel/" in url or "/tv/" in url):
                instagram_urls.append(url)
        
        if not instagram_urls:
            messagebox.showerror("Error", "No valid Instagram URLs found in the file. URLs should contain 'instagram.com/p/', 'instagram.com/reel/', or 'instagram.com/tv/'.")
            return
        
        # Ask for confirmation
        confirmation = messagebox.askyesno(
            "Confirm Batch Processing",
            f"Found {len(instagram_urls)} Instagram URLs in the file. Process all of them?\n\n"
            f"The first 3 URLs:\n" + "\n".join(instagram_urls[:3]) + 
            ("\n..." if len(instagram_urls) > 3 else "")
        )
        
        if not confirmation:
            return
        
        # Start batch processing
        start_batch_instagram_processing(gui_instance, instagram_urls)
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read URLs from file: {str(e)}")

def start_batch_instagram_processing(gui_instance, urls):
    """
    Start the batch processing of Instagram URLs
    
    Args:
        gui_instance: Instance of VideoTranscriberGUI
        urls: List of Instagram URLs to process
    """
    if gui_instance.is_batch_instagram_processing:
        messagebox.showinfo("Info", "Batch processing is already in progress.")
        return
    
    # Check if Instaloader is installed
    if not gui_instance.instaloader_api.ensure_instaloader_installed():
        messagebox.showerror(
            "Error", 
            "Instaloader is not installed. Please click 'Install Instaloader' first."
        )
        return
    
    # Check output directory
    output_dir = gui_instance.instagram_output_dir.get()
    if not output_dir:
        messagebox.showerror("Error", "Please specify an output directory.")
        return
    
    # Initialize batch processing
    gui_instance.is_batch_instagram_processing = True
    gui_instance.instagram_urls = urls
    gui_instance.current_instagram_index = 0
    
    # Update status
    update_instagram_progress(
        gui_instance, 
        0, 
        f"Starting batch processing of {len(urls)} Instagram videos..."
    )
    
    # Start batch thread
    gui_instance.instagram_batch_thread = threading.Thread(
        target=process_next_instagram_url,
        args=(gui_instance,),
        daemon=True
    )
    gui_instance.instagram_batch_thread.start()

def process_next_instagram_url(gui_instance):
    """
    Process the next Instagram URL in the batch queue
    """
    if not gui_instance.is_batch_instagram_processing or gui_instance.current_instagram_index >= len(gui_instance.instagram_urls):
        # Batch processing completed or canceled
        gui_instance.root.after(0, lambda: update_instagram_progress(
            gui_instance, 
            100, 
            f"Batch processing completed. Processed {gui_instance.current_instagram_index} of {len(gui_instance.instagram_urls)} videos."
        ))
        gui_instance.is_batch_instagram_processing = False
        return
    
    # Get current URL and increment index
    current_url = gui_instance.instagram_urls[gui_instance.current_instagram_index]
    output_dir = gui_instance.instagram_output_dir.get()
    
    # Update status
    gui_instance.root.after(0, lambda: update_instagram_progress(
        gui_instance, 
        (gui_instance.current_instagram_index / len(gui_instance.instagram_urls)) * 100,
        f"Processing ({gui_instance.current_instagram_index + 1}/{len(gui_instance.instagram_urls)}): {current_url}"
    ))
    
    try:
        # Call the download method
        success, result = gui_instance.instaloader_api.download_instagram_post(
            current_url, 
            output_dir,
            lambda value, status: update_instagram_batch_progress(gui_instance, value, status, current_url)
        )
        
        if success:
            video_path = result
            
            # Log success
            log_message = f"✓ Downloaded: {os.path.basename(video_path)}"
            gui_instance.root.after(0, lambda: gui_instance.update_batch_log(log_message))
            
            # Set up transcription paths
            output_file = os.path.splitext(video_path)[0] + "_transcript.txt"
            
            # Set video and output paths for transcription
            gui_instance.video_path.set(video_path)
            gui_instance.output_path.set(output_file)
            
            # Wait until previous transcription is complete
            while hasattr(gui_instance, 'is_transcribing') and gui_instance.is_transcribing:
                import time
                time.sleep(0.5)
            
            # Start transcription
            transcribe_instagram_video(gui_instance, video_path, output_file)
            
            # Wait until transcription is complete
            while hasattr(gui_instance, 'is_transcribing') and gui_instance.is_transcribing:
                import time
                time.sleep(0.5)
            
            # Log transcription completion
            log_message = f"✓ Transcribed: {os.path.basename(output_file)}"
            gui_instance.root.after(0, lambda: gui_instance.update_batch_log(log_message))
            
        else:
            error_message = result
            # Log error
            log_message = f"✗ Error downloading {current_url}: {error_message}"
            gui_instance.root.after(0, lambda: gui_instance.update_batch_log(log_message))
    
    except Exception as e:
        # Log unexpected error
        log_message = f"✗ Unexpected error processing {current_url}: {str(e)}"
        gui_instance.root.after(0, lambda: gui_instance.update_batch_log(log_message))
    
    # Increment index and process next URL
    gui_instance.current_instagram_index += 1
    process_next_instagram_url(gui_instance)

def update_instagram_batch_progress(gui_instance, value, status, current_url):
    """
    Update progress bar and status text for batch Instagram download with current URL context
    """
    # Calculate the overall progress
    if gui_instance.is_batch_instagram_processing:
        overall_progress = ((gui_instance.current_instagram_index + (value / 100)) / len(gui_instance.instagram_urls)) * 100
        status_text = f"({gui_instance.current_instagram_index + 1}/{len(gui_instance.instagram_urls)}) {status}"
        
        gui_instance.root.after(0, lambda: gui_instance.instagram_progress.set(overall_progress))
        gui_instance.root.after(0, lambda: gui_instance.instagram_status.set(status_text))

def transcribe_instagram_video(gui_instance, video_path, output_file):
    """
    Transcribe an Instagram video in the batch processing flow
    """
    # Check if we need to switch behavior for batch mode
    original_is_transcribing = gui_instance.is_transcribing
    
    # Start transcription in the same thread for batch processing
    gui_instance.is_transcribing = True
    gui_instance.video_path.set(video_path)
    gui_instance.output_path.set(output_file)
    
    # Use the existing transcribe_video_thread method but call it directly
    # instead of starting a new thread
    gui_instance.transcribe_video_thread()

def cancel_batch_instagram_processing(gui_instance):
    """
    Cancel the batch Instagram processing
    """
    if gui_instance.is_batch_instagram_processing:
        gui_instance.is_batch_instagram_processing = False
        update_instagram_progress(
            gui_instance, 
            0, 
            f"Batch processing canceled after {gui_instance.current_instagram_index} of {len(gui_instance.instagram_urls)} videos."
        )
        messagebox.showinfo("Info", "Batch Instagram processing will be canceled after the current video completes.")

# This should be added to instaloader_integration.py's integrate_instaloader function
def extend_instagram_integration(gui_instance):
    """
    Extend the Instagram integration with batch processing capabilities
    """
    # Add batch Instagram features
    add_batch_instagram_features(gui_instance)
    
    # Add cancel button to the Instagram tab
    instagram_tab = None
    for i in range(gui_instance.notebook.index("end")):
        if gui_instance.notebook.tab(i, "text") == "Instagram Download":
            instagram_tab = gui_instance.notebook.winfo_children()[i]
            break
    
    if instagram_tab:
        # Find button frame
        button_frame = None
        for child in instagram_tab.winfo_children():
            if isinstance(child, ttk.Frame) and not isinstance(child, ttk.LabelFrame):
                if len(child.winfo_children()) > 0 and isinstance(child.winfo_children()[0], ttk.Button):
                    button_frame = child
                    break
        
        if button_frame:
            # Add cancel button
            gui_instance.instagram_cancel_button = ttk.Button(
                button_frame, 
                text="Cancel Batch", 
                command=lambda: cancel_batch_instagram_processing(gui_instance),
                state=tk.DISABLED
            )
            gui_instance.instagram_cancel_button.pack(side=tk.LEFT, padx=5)
    
    # Make batch log visible in Instagram tab if not already present
    if not hasattr(gui_instance, 'batch_log'):
        # Create a log frame
        log_frame = ttk.LabelFrame(instagram_tab, text="Processing Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        import tkinter.scrolledtext as scrolledtext
        gui_instance.batch_log = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=10)
        gui_instance.batch_log.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Add update_batch_log method if not present
        if not hasattr(gui_instance, 'update_batch_log'):
            def update_batch_log(self, message):
                """Update the batch processing log with a message"""
                self.root.after(0, lambda: self._update_batch_log_impl(message))
            
            def _update_batch_log_impl(self, message):
                """Implementation of batch log update (called from main thread)"""
                self.batch_log.insert(tk.END, message + "\n")
                self.batch_log.see(tk.END)  # Scroll to the end
            
            gui_instance.update_batch_log = update_batch_log.__get__(gui_instance)
            gui_instance._update_batch_log_impl = _update_batch_log_impl.__get__(gui_instance)