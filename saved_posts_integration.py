import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

def add_saved_posts_tab(gui_instance):
    """
    Add a tab for downloading and transcribing saved Instagram posts
    
    Args:
        gui_instance: Instance of VideoTranscriberGUI
    """
    # Check if Instagram tab exists and has instaloader_api initialized
    if not hasattr(gui_instance, 'instaloader_api'):
        messagebox.showerror("Error", "Instagram integration is not initialized. Please restart the application.")
        return
        
    # Create saved posts tab
    saved_tab = ttk.Frame(gui_instance.notebook)
    gui_instance.notebook.add(saved_tab, text="Instagram Saved")
    
    # Output directory selection frame
    dir_frame = ttk.LabelFrame(saved_tab, text="Output Directory", padding="10")
    dir_frame.pack(fill=tk.X, padx=5, pady=5)
    
    # Create StringVar for output directory
    if hasattr(gui_instance, 'batch_output_directory'):
        gui_instance.saved_output_dir = gui_instance.batch_output_directory
    else:
        gui_instance.saved_output_dir = tk.StringVar()
        # Set default to user's Downloads folder
        downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads", "Instagram_Saved")
        gui_instance.saved_output_dir.set(downloads_dir)
    
    ttk.Label(dir_frame, text="Save Directory:").grid(row=0, column=0, sticky=tk.W, pady=5)
    ttk.Entry(dir_frame, textvariable=gui_instance.saved_output_dir, width=50).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
    ttk.Button(dir_frame, text="Browse", command=lambda: browse_saved_output_dir(gui_instance)).grid(row=0, column=2, padx=5, pady=5)
    
    dir_frame.columnconfigure(1, weight=1)
    
    # Login frame
    login_frame = ttk.LabelFrame(saved_tab, text="Instagram Login", padding="10")
    login_frame.pack(fill=tk.X, padx=5, pady=5)
    
    # Create StringVars for login credentials
    gui_instance.instagram_username = tk.StringVar()
    gui_instance.instagram_password = tk.StringVar()
    gui_instance.use_browser_cookies = tk.BooleanVar(value=True)
    
    # Use browser cookies option
    ttk.Checkbutton(login_frame, text="Use browser cookies for login (recommended)", 
                  variable=gui_instance.use_browser_cookies).grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=5)
    
    # Username field
    ttk.Label(login_frame, text="Username:").grid(row=1, column=0, sticky=tk.W, pady=5)
    ttk.Entry(login_frame, textvariable=gui_instance.instagram_username, width=30).grid(row=1, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
    
    # Password field
    ttk.Label(login_frame, text="Password:").grid(row=2, column=0, sticky=tk.W, pady=5)
    gui_instance.password_entry = ttk.Entry(login_frame, textvariable=gui_instance.instagram_password, width=30, show="*")
    gui_instance.password_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
    
    # Show/Hide password button
    gui_instance.show_ig_password = tk.BooleanVar(value=False)
    ttk.Checkbutton(login_frame, text="Show", variable=gui_instance.show_ig_password, 
                   command=lambda: toggle_password_visibility(gui_instance)).grid(row=2, column=2, padx=5, pady=5)
    
    # Browser selection
    ttk.Label(login_frame, text="Browser:").grid(row=3, column=0, sticky=tk.W, pady=5)
    gui_instance.browser_var = tk.StringVar(value="firefox")
    browsers = ["firefox", "chrome", "safari", "edge", "brave", "opera"]
    browser_combobox = ttk.Combobox(login_frame, textvariable=gui_instance.browser_var, values=browsers, width=15)
    browser_combobox.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
    
    login_frame.columnconfigure(1, weight=1)
    
    # Options frame
    options_frame = ttk.LabelFrame(saved_tab, text="Download Options", padding="10")
    options_frame.pack(fill=tk.X, padx=5, pady=5)
    
    # Create variables for options
    gui_instance.saved_count = tk.StringVar(value="all")
    gui_instance.download_pictures = tk.BooleanVar(value=True)
    gui_instance.download_videos = tk.BooleanVar(value=True)
    gui_instance.auto_transcribe = tk.BooleanVar(value=True)
    
    # Add auto-delete option to the saved posts tab
    if not hasattr(gui_instance, 'instagram_auto_delete'):
        gui_instance.instagram_auto_delete = tk.BooleanVar(value=False)
    
    # Number of posts to download
    ttk.Label(options_frame, text="Number of posts to download:").grid(row=0, column=0, sticky=tk.W, pady=5)
    count_frame = ttk.Frame(options_frame)
    count_frame.grid(row=0, column=1, sticky=tk.W, pady=5)
    
    ttk.Radiobutton(count_frame, text="All", variable=gui_instance.saved_count, value="all").pack(side=tk.LEFT, padx=5)
    ttk.Radiobutton(count_frame, text="Specify count:", variable=gui_instance.saved_count, value="count").pack(side=tk.LEFT, padx=5)
    gui_instance.count_entry = ttk.Entry(count_frame, width=5)
    gui_instance.count_entry.pack(side=tk.LEFT, padx=5)
    gui_instance.count_entry.insert(0, "20")
    
    # Content type options
    ttk.Checkbutton(options_frame, text="Download pictures", variable=gui_instance.download_pictures).grid(row=1, column=0, sticky=tk.W, pady=5)
    ttk.Checkbutton(options_frame, text="Download videos", variable=gui_instance.download_videos).grid(row=1, column=1, sticky=tk.W, pady=5)
    ttk.Checkbutton(options_frame, text="Auto-transcribe downloaded videos", variable=gui_instance.auto_transcribe).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
    
    # Add auto-delete option
    ttk.Checkbutton(options_frame, text="Auto-delete videos after transcription", 
                  variable=gui_instance.instagram_auto_delete).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
    
    options_frame.columnconfigure(1, weight=1)
    
    # Action buttons
    button_frame = ttk.Frame(saved_tab)
    button_frame.pack(fill=tk.X, pady=10)
    
    ttk.Button(button_frame, text="Download Saved Posts", 
              command=lambda: download_saved_posts(gui_instance)).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Test Login", 
              command=lambda: test_instagram_login(gui_instance)).pack(side=tk.LEFT, padx=5)
    
    # Progress bar and status
    progress_frame = ttk.Frame(saved_tab)
    progress_frame.pack(fill=tk.X, pady=5)
    
    ttk.Label(progress_frame, text="Progress:").pack(side=tk.LEFT, padx=5)
    
    # Create progress bar and status variables
    gui_instance.saved_progress = tk.DoubleVar(value=0)
    gui_instance.saved_status = tk.StringVar(value="Ready to download saved posts")
    
    ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, length=100, 
                   variable=gui_instance.saved_progress, mode='determinate').pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
    
    # Status label
    status_label = ttk.Label(saved_tab, textvariable=gui_instance.saved_status, anchor=tk.W)
    status_label.pack(fill=tk.X, pady=5)
    
    # Log text area
    ttk.Label(saved_tab, text="Download Log:").pack(anchor=tk.W, pady=5)
    gui_instance.saved_log = tk.Text(saved_tab, wrap=tk.WORD, height=8)
    gui_instance.saved_log.pack(fill=tk.BOTH, expand=True, pady=5)
    
    # Help text
    help_frame = ttk.LabelFrame(saved_tab, text="Information", padding="10")
    help_frame.pack(fill=tk.X, padx=5, pady=5)
    
    help_text = tk.Text(help_frame, wrap=tk.WORD, height=6)
    help_text.pack(fill=tk.BOTH, expand=True)
    help_text.insert(tk.END, """
How to use Instagram Saved Posts Downloader:

1. Choose where to save the downloaded posts
2. Login to Instagram using browser cookies (recommended) or your username and password
3. Set your download preferences (count, content types, auto-transcribe)
4. Enable auto-delete to automatically remove videos after transcription to save disk space
5. Click "Download Saved Posts" to begin the process
6. Downloaded videos can be automatically sent to the transcription process

Note: This feature requires login to access your saved posts collection.
    """)
    help_text.config(state=tk.DISABLED)

def toggle_password_visibility(gui_instance):
    """Toggle the visibility of the Instagram password field"""
    if gui_instance.show_ig_password.get():
        gui_instance.password_entry.config(show="")
    else:
        gui_instance.password_entry.config(show="*")

def browse_saved_output_dir(gui_instance):
    """Browse for output directory for downloaded saved posts"""
    directory = filedialog.askdirectory(title="Select Directory to Save Posts")
    if directory:
        gui_instance.saved_output_dir.set(directory)

def update_saved_log(gui_instance, message):
    """Update the saved posts log with a message"""
    gui_instance.root.after(0, lambda: _update_saved_log_impl(gui_instance, message))

def _update_saved_log_impl(gui_instance, message):
    """Implementation of saved log update (called from main thread)"""
    gui_instance.saved_log.insert(tk.END, message + "\n")
    gui_instance.saved_log.see(tk.END)  # Scroll to the end

def update_saved_progress(gui_instance, value, status_text):
    """Update progress bar and status text for saved posts download"""
    gui_instance.root.after(0, lambda: gui_instance.saved_progress.set(value))
    gui_instance.root.after(0, lambda: gui_instance.saved_status.set(status_text))

def test_instagram_login(gui_instance):
    """Test Instagram login credentials"""
    # Start in a separate thread
    threading.Thread(
        target=test_instagram_login_thread,
        args=(gui_instance,),
        daemon=True
    ).start()

def test_instagram_login_thread(gui_instance):
    """Thread function to test Instagram login"""
    update_saved_progress(gui_instance, 10, "Testing Instagram login...")
    update_saved_log(gui_instance, "Testing Instagram login...")
    
    try:
        import instaloader
        import inspect
    except ImportError:
        # Try to install instaloader if not already installed
        success, message = gui_instance.instaloader_api.install_instaloader(
            lambda value, status: update_saved_progress(gui_instance, value, status)
        )
        if not success:
            update_saved_progress(gui_instance, 0, "Failed to install Instaloader")
            gui_instance.root.after(0, lambda: messagebox.showerror("Error", message))
            return
        
        try:
            import instaloader
            import inspect
        except ImportError:
            update_saved_progress(gui_instance, 0, "Failed to import Instaloader after installation")
            gui_instance.root.after(0, lambda: messagebox.showerror(
                "Error", 
                "Failed to import Instaloader after installation. Please restart the application."
            ))
            return
    
    try:
        # Create a new instance for login testing
        L = instaloader.Instaloader()
        
        if gui_instance.use_browser_cookies.get():
            # Check if the browser cookie function exists
            has_browser_cookie_support = hasattr(L, 'load_session_from_browser')
            
            if not has_browser_cookie_support:
                # Check instaloader version
                version = getattr(instaloader, '__version__', 'unknown')
                update_saved_progress(gui_instance, 0, "Browser cookie login not supported")
                update_saved_log(gui_instance, f"✗ Browser cookie login not supported in Instaloader version {version}")
                # Use lambda without capturing 'e'
                gui_instance.root.after(0, lambda: messagebox.showerror(
                    "Feature Not Available", 
                    f"Browser cookie login is not supported in your Instaloader version ({version}).\n\n"
                    "Please use username/password login instead, or upgrade Instaloader with:\n"
                    "pip install --upgrade instaloader"
                ))
                return
                
            # Login with browser cookies
            browser = gui_instance.browser_var.get()
            update_saved_log(gui_instance, f"Trying to login with {browser} cookies...")
            
            try:
                try:
                    # Try importing browser_cookie3 first
                    import browser_cookie3
                except ImportError:
                    update_saved_log(gui_instance, f"✗ Missing browser_cookie3 package")
                    # Use a separate lambda for this error message
                    gui_instance.root.after(0, lambda: messagebox.showerror(
                        "Missing Dependency", 
                        "The browser_cookie3 package is required for browser cookie login.\n\n"
                        "Please install it with:\npip install browser_cookie3"
                    ))
                    return
                
                # Now try the actual login
                L.load_session_from_browser(browser)
                test_user = L.test_login()
                
                if test_user:
                    update_saved_progress(gui_instance, 100, f"Login successful as {test_user}")
                    update_saved_log(gui_instance, f"✓ Login successful as {test_user}")
                    # Use a separate lambda for success message
                    gui_instance.root.after(0, lambda: messagebox.showinfo(
                        "Login Successful", 
                        f"Successfully logged in as {test_user} using {browser} cookies."
                    ))
                else:
                    update_saved_progress(gui_instance, 0, "Login failed with browser cookies")
                    update_saved_log(gui_instance, "✗ Login failed with browser cookies")
                    # Use a separate lambda for failure message
                    gui_instance.root.after(0, lambda: messagebox.showerror(
                        "Login Failed", 
                        f"Failed to login using {browser} cookies. Try another browser or use username/password."
                    ))
            except Exception as e:
                error_message = str(e)
                update_saved_progress(gui_instance, 0, f"Error loading cookies: {error_message}")
                update_saved_log(gui_instance, f"✗ Error loading cookies: {error_message}")
                # Create a function to avoid capturing 'e' in lambda
                def show_error_message():
                    messagebox.showerror(
                        "Login Error", 
                        f"Error loading cookies from {browser}: {error_message}\n\n"
                        "Try another browser or use username/password."
                    )
                gui_instance.root.after(0, show_error_message)
        else:
            # Login with username and password
            username = gui_instance.instagram_username.get()
            password = gui_instance.instagram_password.get()
            
            if not username or not password:
                update_saved_progress(gui_instance, 0, "Username or password is missing")
                gui_instance.root.after(0, lambda: messagebox.showerror(
                    "Login Error", 
                    "Please enter both username and password."
                ))
                return
            
            update_saved_log(gui_instance, f"Trying to login as {username}...")
            
            try:
                L.login(username, password)
                test_user = L.test_login()
                
                if test_user:
                    update_saved_progress(gui_instance, 100, f"Login successful as {test_user}")
                    update_saved_log(gui_instance, f"✓ Login successful as {test_user}")
                    gui_instance.root.after(0, lambda: messagebox.showinfo(
                        "Login Successful", 
                        f"Successfully logged in as {test_user}."
                    ))
                else:
                    update_saved_progress(gui_instance, 0, "Login failed with username/password")
                    update_saved_log(gui_instance, "✗ Login failed with username/password")
                    gui_instance.root.after(0, lambda: messagebox.showerror(
                        "Login Failed", 
                        "Failed to login with provided username and password. Please check your credentials."
                    ))
            except Exception as e:
                error_message = str(e)
                update_saved_progress(gui_instance, 0, f"Login error: {error_message}")
                update_saved_log(gui_instance, f"✗ Login error: {error_message}")
                # Create a function to avoid capturing 'e' in lambda
                def show_login_error():
                    messagebox.showerror(
                        "Login Error", 
                        f"Login error: {error_message}"
                    )
                gui_instance.root.after(0, show_login_error)
    except Exception as e:
        error_message = str(e)
        update_saved_progress(gui_instance, 0, f"Error initializing Instaloader: {error_message}")
        update_saved_log(gui_instance, f"✗ Error initializing Instaloader: {error_message}")
        # Create a function to avoid capturing 'e' in lambda
        def show_init_error():
            messagebox.showerror(
                "Error", 
                f"Error initializing Instaloader: {error_message}"
            )
        gui_instance.root.after(0, show_init_error)

def download_saved_posts(gui_instance):
    """Start downloading saved posts"""
    output_dir = gui_instance.saved_output_dir.get()
    
    if not output_dir:
        messagebox.showerror("Error", "Please specify an output directory.")
        return
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create output directory: {str(e)}")
            return
    
    # Check if instaloader is installed
    if not gui_instance.instaloader_api.ensure_instaloader_installed():
        messagebox.showerror(
            "Error", 
            "Instaloader is not installed. Please install it first."
        )
        return
    
    # Reset progress and log
    update_saved_progress(gui_instance, 0, "Starting download...")
    gui_instance.saved_log.delete(1.0, tk.END)
    
    # Start download in a thread
    threading.Thread(
        target=download_saved_posts_thread,
        args=(gui_instance, output_dir),
        daemon=True
    ).start()

def download_saved_posts_thread(gui_instance, output_dir):
    """Thread function to download saved posts"""
    try:
        import instaloader
    except ImportError:
        update_saved_progress(gui_instance, 0, "Failed to import Instaloader")
        update_saved_log(gui_instance, "Error: Failed to import Instaloader")
        return
    
    try:
        # Create Instaloader instance with custom settings
        L = instaloader.Instaloader(
            dirname_pattern=output_dir + "/{profile}",
            filename_pattern="{date_utc}_UTC_{shortcode}",
            download_pictures=gui_instance.download_pictures.get(),
            download_videos=gui_instance.download_videos.get(),
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=True,
            post_metadata_txt_pattern="{caption}"
        )
        
        update_saved_log(gui_instance, "Instaloader initialized with custom settings")
        update_saved_progress(gui_instance, 10, "Logging in to Instagram...")
        
        # Login to Instagram
        if gui_instance.use_browser_cookies.get():
            # Login with browser cookies
            browser = gui_instance.browser_var.get()
            update_saved_log(gui_instance, f"Logging in with {browser} cookies...")
            
            try:
                L.load_session_from_browser(browser)
                username = L.test_login()
                
                if not username:
                    update_saved_progress(gui_instance, 0, "Login failed with browser cookies")
                    update_saved_log(gui_instance, "Error: Login failed with browser cookies")
                    gui_instance.root.after(0, lambda: messagebox.showerror(
                        "Login Failed", 
                        f"Failed to login using {browser} cookies. Try another browser or use username/password."
                    ))
                    return
                
                update_saved_log(gui_instance, f"Logged in as {username}")
            except Exception as e:
                update_saved_progress(gui_instance, 0, f"Error loading cookies: {str(e)}")
                update_saved_log(gui_instance, f"Error loading cookies: {str(e)}")
                gui_instance.root.after(0, lambda: messagebox.showerror(
                    "Login Error", 
                    f"Error loading cookies from {browser}: {str(e)}"
                ))
                return
        else:
            # Login with username and password
            username = gui_instance.instagram_username.get()
            password = gui_instance.instagram_password.get()
            
            if not username or not password:
                update_saved_progress(gui_instance, 0, "Username or password is missing")
                update_saved_log(gui_instance, "Error: Username or password is missing")
                gui_instance.root.after(0, lambda: messagebox.showerror(
                    "Login Error", 
                    "Please enter both username and password."
                ))
                return
            
            update_saved_log(gui_instance, f"Logging in as {username}...")
            
            try:
                L.login(username, password)
                if not L.test_login():
                    update_saved_progress(gui_instance, 0, "Login failed with username/password")
                    update_saved_log(gui_instance, "Error: Login failed with username/password")
                    gui_instance.root.after(0, lambda: messagebox.showerror(
                        "Login Failed", 
                        "Failed to login with provided username and password. Please check your credentials."
                    ))
                    return
                
                update_saved_log(gui_instance, f"Logged in successfully as {username}")
            except Exception as e:
                update_saved_progress(gui_instance, 0, f"Login error: {str(e)}")
                update_saved_log(gui_instance, f"Login error: {str(e)}")
                gui_instance.root.after(0, lambda: messagebox.showerror(
                    "Login Error", 
                    f"Login error: {str(e)}"
                ))
                return
        
        # Determine post count
        post_count = None
        if gui_instance.saved_count.get() == "count":
            try:
                post_count = int(gui_instance.count_entry.get())
                update_saved_log(gui_instance, f"Will download up to {post_count} saved posts")
            except ValueError:
                update_saved_progress(gui_instance, 0, "Invalid count value")
                update_saved_log(gui_instance, "Error: Invalid count value")
                gui_instance.root.after(0, lambda: messagebox.showerror(
                    "Error", 
                    "Please enter a valid number for post count."
                ))
                return
        else:
            update_saved_log(gui_instance, "Will download all saved posts")
        
        # Start downloading saved posts
        update_saved_progress(gui_instance, 20, "Fetching saved posts...")
        update_saved_log(gui_instance, "Fetching list of saved posts...")
        
        # Track videos for transcription
        downloaded_videos = []
        counter = 0
        
        try:
            saved_posts = L.get_saved_posts()
            total_posts = post_count if post_count else 999999  # Arbitrarily large number if downloading all
            
            # Main download loop
            for post in saved_posts:
                if counter >= total_posts:
                    break
                
                try:
                    # Update progress
                    progress = min(20 + int(70 * (counter + 1) / total_posts), 90)
                    update_saved_progress(gui_instance, progress, f"Downloading post {counter + 1}...")
                    
                    # Skip non-video posts if only downloading videos
                    if not gui_instance.download_pictures.get() and not post.is_video:
                        update_saved_log(gui_instance, f"Skipping post {post.shortcode} (not a video)")
                        continue
                    
                    # Skip videos if not downloading videos
                    if not gui_instance.download_videos.get() and post.is_video:
                        update_saved_log(gui_instance, f"Skipping post {post.shortcode} (is a video)")
                        continue
                    
                    update_saved_log(gui_instance, f"Downloading post {post.shortcode} from {post.owner_username}...")
                    
                    # Download the post
                    L.download_post(post, target=f"{post.owner_username}_{post.shortcode}")
                    
                    # Track video for transcription
                    if post.is_video and gui_instance.download_videos.get() and gui_instance.auto_transcribe.get():
                        # Determine filename based on instaloader pattern
                        date_str = post.date_utc.strftime("%Y-%m-%d_%H-%M-%S")
                        video_filename = f"{output_dir}/{post.owner_username}/{date_str}_UTC_{post.shortcode}.mp4"
                        if os.path.exists(video_filename):
                            downloaded_videos.append(video_filename)
                            update_saved_log(gui_instance, f"✓ Video added to transcription queue: {post.shortcode}")
                    
                    counter += 1
                except Exception as e:
                    update_saved_log(gui_instance, f"Error downloading post {post.shortcode}: {str(e)}")
                    continue
            
            # Complete download process
            if counter == 0:
                update_saved_progress(gui_instance, 100, "No posts were downloaded")
                update_saved_log(gui_instance, "No posts were downloaded. Check your download settings.")
                gui_instance.root.after(0, lambda: messagebox.showinfo(
                    "Download Complete", 
                    "No posts were downloaded. You may need to check your download settings."
                ))
            else:
                update_saved_progress(gui_instance, 100, f"Download complete - {counter} posts downloaded")
                update_saved_log(gui_instance, f"Download complete - {counter} posts downloaded")
                
                # Start transcription if videos were downloaded
                if downloaded_videos and gui_instance.auto_transcribe.get():
                    update_saved_log(gui_instance, f"Starting transcription for {len(downloaded_videos)} videos...")
                    
                    # Queue videos for transcription
                    gui_instance.root.after(0, lambda: queue_videos_for_transcription(gui_instance, downloaded_videos))
                else:
                    gui_instance.root.after(0, lambda: messagebox.showinfo(
                        "Download Complete", 
                        f"Successfully downloaded {counter} posts.\n\n"
                        f"Posts saved to: {output_dir}"
                    ))
        
        except Exception as e:
            update_saved_progress(gui_instance, 0, f"Error fetching saved posts: {str(e)}")
            update_saved_log(gui_instance, f"Error fetching saved posts: {str(e)}")
            gui_instance.root.after(0, lambda: messagebox.showerror(
                "Error", 
                f"Error fetching saved posts: {str(e)}"
            ))
    
    except Exception as e:
        update_saved_progress(gui_instance, 0, f"Error: {str(e)}")
        update_saved_log(gui_instance, f"Error: {str(e)}")
        gui_instance.root.after(0, lambda: messagebox.showerror(
            "Error", 
            f"An unexpected error occurred: {str(e)}"
        ))

def queue_videos_for_transcription(gui_instance, video_files):
    """Queue multiple videos for transcription with auto-delete support"""
    if not video_files:
        return
    
    # Show confirmation dialog
    if not messagebox.askyesno(
        "Start Transcription", 
        f"Ready to transcribe {len(video_files)} downloaded videos?\n\n"
        "This will add them to the batch processing queue."
    ):
        return
    
    # Create a list to track completed videos for auto-deletion
    if gui_instance.instagram_auto_delete.get():
        if not hasattr(gui_instance, 'batch_completed_videos'):
            gui_instance.batch_completed_videos = []
        # Add these videos to the tracking list
        gui_instance.batch_completed_videos.extend(video_files)
    
    # Switch to batch processing tab if it exists
    for i in range(gui_instance.notebook.index("end")):
        if gui_instance.notebook.tab(i, "text") == "Batch Processing":
            gui_instance.notebook.select(i)
            break
    
    # Set batch processing directories
    if hasattr(gui_instance, 'batch_directory') and hasattr(gui_instance, 'batch_output_directory'):
        # Get the common directory of the videos
        common_dir = os.path.dirname(os.path.commonprefix(video_files))
        output_dir = os.path.join(common_dir, "transcripts")
        
        gui_instance.batch_directory.set(common_dir)
        gui_instance.batch_output_directory.set(output_dir)
        
        # Start batch processing
        if hasattr(gui_instance, 'start_batch_transcription'):
            gui_instance.root.after(500, gui_instance.start_batch_transcription)
        else:
            messagebox.showinfo(
                "Transcription", 
                f"Videos have been downloaded to:\n{common_dir}\n\n"
                "You can now manually transcribe them using the Transcription tab."
            )
    else:
        # If batch processing is not available, just let the user know where the videos are
        common_dir = os.path.dirname(os.path.commonprefix(video_files))
        messagebox.showinfo(
            "Download Complete", 
            f"Videos have been downloaded to:\n{common_dir}\n\n"
            "You can now manually transcribe them using the Transcription tab."
        )