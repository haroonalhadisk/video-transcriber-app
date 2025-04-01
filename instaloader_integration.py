import os
import re
import sys
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

class InstaloaderIntegration:
    def __init__(self):
        """Initialize the Instaloader integration"""
        self.ensure_instaloader_installed()
    
    def ensure_instaloader_installed(self):
        """Check if Instaloader is installed, and install it if not"""
        try:
            # Try to import instaloader to check if it's installed
            import instaloader
            return True
        except ImportError:
            # Not installed, prompt to install
            return False
    
    def install_instaloader(self, callback=None):
        """Install Instaloader using pip"""
        try:
            if callback:
                callback(10, "Installing Instaloader...")
            
            subprocess.check_call([sys.executable, "-m", "pip", "install", "instaloader"])
            
            if callback:
                callback(100, "Instaloader installed successfully")
            
            return True, "Instaloader installed successfully"
        except Exception as e:
            if callback:
                callback(0, f"Error installing Instaloader: {str(e)}")
            
            return False, f"Error installing Instaloader: {str(e)}"
    
    def extract_post_shortcode(self, url):
        """
        Extract the Instagram post shortcode from a URL
        
        Args:
            url (str): Instagram URL
            
        Returns:
            str: Post shortcode or None if invalid URL
        """
        # Match patterns like instagram.com/p/ABC123/ or instagram.com/reel/XYZ789/
        match = re.search(r'instagram\.com/(?:p|reel|tv)/([^/?]+)', url)
        if match:
            return match.group(1)
        return None
    
    def download_instagram_post(self, url, output_dir, callback=None):
        """
        Download an Instagram post using Instaloader
        
        Args:
            url (str): Instagram post URL
            output_dir (str): Directory to save the post
            callback (function, optional): Callback function for progress updates
            
        Returns:
            tuple: (success, filepath or error_message)
        """
        # First, ensure Instaloader is installed
        try:
            import instaloader
        except ImportError:
            success, message = self.install_instaloader(callback)
            if not success:
                return False, message
            try:
                import instaloader
            except ImportError:
                return False, "Failed to import Instaloader after installation. Please restart the application."
        
        # Extract post shortcode from URL
        shortcode = self.extract_post_shortcode(url)
        if not shortcode:
            return False, "Invalid Instagram URL. Please provide a valid post URL (e.g., https://www.instagram.com/p/ABC123/)."
        
        if callback:
            callback(20, f"Downloading post with shortcode: {shortcode}")
        
        try:
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Initialize Instaloader with the output directory
            L = instaloader.Instaloader(
                dirname_pattern=output_dir,
                filename_pattern="{shortcode}",
                download_videos=True,
                download_video_thumbnails=False,
                download_geotags=False,
                download_comments=False,
                save_metadata=False,
                compress_json=False
            )
            
            if callback:
                callback(30, "Fetching post from Instagram...")
            
            # Get post by shortcode
            post = instaloader.Post.from_shortcode(L.context, shortcode)
            
            if callback:
                callback(50, "Downloading media...")
            
            # Download the post
            L.download_post(post, target=shortcode)
            
            if callback:
                callback(90, "Processing downloaded files...")
            
            # Find the downloaded video file
            video_extensions = ['.mp4', '.mov']
            downloaded_files = os.listdir(output_dir)
            video_file = None
            
            for file in downloaded_files:
                if any(file.endswith(ext) for ext in video_extensions) and shortcode in file:
                    video_file = os.path.join(output_dir, file)
                    break
            
            if video_file:
                if callback:
                    callback(100, f"Download completed: {os.path.basename(video_file)}")
                return True, video_file
            else:
                return False, "No video was found in the post. The post might contain only images."
            
        except instaloader.exceptions.InstaloaderException as e:
            return False, f"Instaloader error: {str(e)}"
        except Exception as e:
            return False, f"Error downloading Instagram post: {str(e)}"

def integrate_instaloader(gui_instance):
    """
    Integrate Instaloader functionality into the VideoTranscriberGUI class
    
    Args:
        gui_instance: Instance of VideoTranscriberGUI
    """
    # Create Instaloader integration instance
    gui_instance.instaloader_api = InstaloaderIntegration()
    
    # Check if Instagram tab already exists
    tab_exists = False
    for i in range(gui_instance.notebook.index("end")):
        if gui_instance.notebook.tab(i, "text") == "Instagram Download":
            tab_exists = True
            break
    
    if not tab_exists:
        # Add Instagram tab to the notebook
        instagram_tab = ttk.Frame(gui_instance.notebook)
        gui_instance.notebook.add(instagram_tab, text="Instagram Download")
        
        # Instagram URL input
        url_frame = ttk.LabelFrame(instagram_tab, text="Instagram Video URL", padding="10")
        url_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Create StringVar for URL
        gui_instance.instagram_url = tk.StringVar()
        
        ttk.Label(url_frame, text="Instagram URL:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(url_frame, textvariable=gui_instance.instagram_url, width=50).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        
        # Output directory selection
        ttk.Label(url_frame, text="Save Directory:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        # Reuse batch output directory if available, or create a new one
        if hasattr(gui_instance, 'batch_output_directory'):
            gui_instance.instagram_output_dir = gui_instance.batch_output_directory
        else:
            gui_instance.instagram_output_dir = tk.StringVar()
            # Set default to user's Downloads folder
            downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
            gui_instance.instagram_output_dir.set(downloads_dir)
        
        ttk.Entry(url_frame, textvariable=gui_instance.instagram_output_dir, width=50).grid(row=1, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        ttk.Button(url_frame, text="Browse", command=lambda: browse_output_dir(gui_instance)).grid(row=1, column=2, padx=5, pady=5)
        
        url_frame.columnconfigure(1, weight=1)
        
        # Instaloader status
        status_frame = ttk.Frame(url_frame)
        status_frame.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        ttk.Label(status_frame, text="Instaloader Status:").pack(side=tk.LEFT, padx=5)
        
        if gui_instance.instaloader_api.ensure_instaloader_installed():
            status_label = ttk.Label(status_frame, text="Installed", foreground="green")
        else:
            status_label = ttk.Label(status_frame, text="Not Installed", foreground="red")
        status_label.pack(side=tk.LEFT, padx=5)
        
        if not gui_instance.instaloader_api.ensure_instaloader_installed():
            ttk.Button(status_frame, text="Install Instaloader", 
                      command=lambda: install_instaloader_thread(gui_instance)).pack(side=tk.LEFT, padx=5)
        
        # Action buttons
        button_frame = ttk.Frame(instagram_tab)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Download & Transcribe", 
                   command=lambda: download_and_transcribe(gui_instance)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Download Only", 
                   command=lambda: download_only(gui_instance)).pack(side=tk.LEFT, padx=5)
        
        # Progress bar and status
        progress_frame = ttk.Frame(instagram_tab)
        progress_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(progress_frame, text="Progress:").pack(side=tk.LEFT, padx=5)
        
        # Create progress bar and status variables
        gui_instance.instagram_progress = tk.DoubleVar(value=0)
        gui_instance.instagram_status = tk.StringVar(value="Ready to download")
        
        ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, length=100, 
                        variable=gui_instance.instagram_progress, mode='determinate').pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Status label
        status_label = ttk.Label(instagram_tab, textvariable=gui_instance.instagram_status, anchor=tk.W)
        status_label.pack(fill=tk.X, pady=5)
        
        # Information frame with help text
        info_frame = ttk.LabelFrame(instagram_tab, text="Information", padding="10")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        info_text = tk.Text(info_frame, wrap=tk.WORD, height=8)
        info_text.pack(fill=tk.BOTH, expand=True)
        info_text.insert(tk.END, """
How to use Instagram Video Downloader (Instaloader):

1. Copy the URL of an Instagram post or reel that contains a video
   (e.g., https://www.instagram.com/p/ABC123/ or https://www.instagram.com/reel/XYZ789/)
2. Paste the URL in the field above
3. Choose where to save the downloaded video
4. Click "Download & Transcribe" to download the video and proceed with transcription
5. Or click "Download Only" if you just want to save the video without transcribing

Note: This feature works with public Instagram posts only by default. 
For private posts, you would need to login with Instaloader separately.

Instaloader is a powerful tool to download Instagram posts with many more features.
For advanced usage, see: https://instaloader.github.io/
        """)
        info_text.config(state=tk.DISABLED)

def browse_output_dir(gui_instance):
    """Browse for output directory for downloaded videos"""
    directory = filedialog.askdirectory(title="Select Directory to Save Videos")
    if directory:
        gui_instance.instagram_output_dir.set(directory)

def update_instagram_progress(gui_instance, value, status_text):
    """Update progress bar and status text for Instagram download"""
    gui_instance.root.after(0, lambda: gui_instance.instagram_progress.set(value))
    gui_instance.root.after(0, lambda: gui_instance.instagram_status.set(status_text))

def install_instaloader_thread(gui_instance):
    """Install Instaloader in a separate thread"""
    threading.Thread(
        target=install_instaloader_task,
        args=(gui_instance,),
        daemon=True
    ).start()

def install_instaloader_task(gui_instance):
    """Thread function to install Instaloader"""
    success, message = gui_instance.instaloader_api.install_instaloader(
        lambda value, status: update_instagram_progress(gui_instance, value, status)
    )
    
    if success:
        gui_instance.root.after(0, lambda: messagebox.showinfo("Success", message))
        # Reload the tab to update the status
        gui_instance.root.after(100, lambda: integrate_instaloader(gui_instance))
    else:
        gui_instance.root.after(0, lambda: messagebox.showerror("Error", message))

def download_only(gui_instance):
    """Download Instagram video without transcribing"""
    url = gui_instance.instagram_url.get().strip()
    output_dir = gui_instance.instagram_output_dir.get()
    
    if not url:
        messagebox.showerror("Error", "Please enter an Instagram video URL.")
        return
    
    if not output_dir:
        messagebox.showerror("Error", "Please specify an output directory.")
        return
    
    if not gui_instance.instaloader_api.ensure_instaloader_installed():
        messagebox.showerror(
            "Error", 
            "Instaloader is not installed. Please click 'Install Instaloader' first."
        )
        return
    
    # Reset progress
    update_instagram_progress(gui_instance, 0, "Starting download...")
    
    # Start download in a thread
    threading.Thread(
        target=download_instagram_thread,
        args=(gui_instance, url, output_dir, False),
        daemon=True
    ).start()

def download_and_transcribe(gui_instance):
    """Download Instagram video and proceed to transcribe it"""
    url = gui_instance.instagram_url.get().strip()
    output_dir = gui_instance.instagram_output_dir.get()
    
    if not url:
        messagebox.showerror("Error", "Please enter an Instagram video URL.")
        return
    
    if not output_dir:
        messagebox.showerror("Error", "Please specify an output directory.")
        return
    
    if not gui_instance.instaloader_api.ensure_instaloader_installed():
        messagebox.showerror(
            "Error", 
            "Instaloader is not installed. Please click 'Install Instaloader' first."
        )
        return
    
    # Reset progress
    update_instagram_progress(gui_instance, 0, "Starting download...")
    
    # Start download in a thread
    threading.Thread(
        target=download_instagram_thread,
        args=(gui_instance, url, output_dir, True),
        daemon=True
    ).start()

def download_instagram_thread(gui_instance, url, output_dir, transcribe_after=False):
    """Thread function to download Instagram video"""
    try:
        # Call the download method with a callback for progress updates
        success, result = gui_instance.instaloader_api.download_instagram_post(
            url, 
            output_dir,
            lambda value, status: update_instagram_progress(gui_instance, value, status)
        )
        
        if success:
            video_path = result
            update_instagram_progress(gui_instance, 100, f"Download complete: {os.path.basename(video_path)}")
            
            # Show success message
            gui_instance.root.after(0, lambda: messagebox.showinfo(
                "Download Complete", 
                f"Instagram video successfully downloaded to:\n{video_path}"
            ))
            
            if transcribe_after:
                # Switch to transcription tab
                gui_instance.root.after(100, lambda: gui_instance.notebook.select(0))
                
                # Set video path and generate output path
                gui_instance.video_path.set(video_path)
                output_file = os.path.splitext(video_path)[0] + "_transcript.txt"
                gui_instance.output_path.set(output_file)
                
                # Start transcription after a short delay to ensure UI updates
                gui_instance.root.after(500, gui_instance.start_transcription)
        else:
            error_message = result
            update_instagram_progress(gui_instance, 0, f"Download failed: {error_message}")
            
            # Show error message
            gui_instance.root.after(0, lambda: messagebox.showerror(
                "Download Failed", 
                f"Failed to download Instagram video:\n{error_message}"
            ))
    except Exception as e:
        update_instagram_progress(gui_instance, 0, f"Error: {str(e)}")
        gui_instance.root.after(0, lambda: messagebox.showerror(
            "Error", 
            f"An unexpected error occurred:\n{str(e)}"
        ))