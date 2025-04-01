import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

from instaloader_integration import integrate_instaloader

def integrate_instagram(gui_instance):
    """
    Integrate Instagram functionality into the VideoTranscriberGUI class.
    This function creates a new tab for Instagram video downloading.
    
    Args:
        gui_instance: The VideoTranscriberGUI instance
    """
    # First, bind the required modules to gui_instance for use by the instaloader module
    gui_instance.filedialog = filedialog
    gui_instance.messagebox = messagebox
    gui_instance.threading = threading
    
    # Then call the integration function from instaloader_integration
    integrate_instaloader(gui_instance)