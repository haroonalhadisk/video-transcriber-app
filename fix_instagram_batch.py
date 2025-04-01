import os
import re
import sys
import fileinput

def fix_integration():
    # Define the update_instagram_progress function that needs to be added
    function_to_add = """
def update_instagram_progress(gui_instance, value, status_text):
    """Update progress bar and status text for Instagram download"""
    gui_instance.root.after(0, lambda: gui_instance.instagram_progress.set(value))
    gui_instance.root.after(0, lambda: gui_instance.instagram_status.set(status_text))
"""
    
    # Path to batch_instagram_integration.py
    batch_file = 'batch_instagram_integration.py'
    
    # First check if the file exists
    if not os.path.exists(batch_file):
        print(f"Error: Could not find {batch_file}")
        return False
    
    # Read the file content
    with open(batch_file, 'r') as f:
        content = f.read()
    
    # Check if function is already defined
    if 'def update_instagram_progress' in content:
        print("Function already exists, no need to add it.")
        return True
    
    # Add the function at the top of the file after imports
    import_pattern = r'import.*?\n\n'
    import_matches = list(re.finditer(import_pattern, content, re.DOTALL))
    
    if import_matches:
        # Insert after the last import section
        last_import = import_matches[-1]
        position = last_import.end()
        new_content = content[:position] + function_to_add + content[position:]
    else:
        # If no import section found, add at the beginning
        new_content = function_to_add + content
    
    # Write the updated content back to the file
    with open(batch_file, 'w') as f:
        f.write(new_content)
    
    print(f"Successfully added update_instagram_progress function to {batch_file}")
    return True

def fix_filedialog():
    # Path to instagram_integration.py
    integration_file = 'instagram_integration.py'
    
    # First check if the file exists
    if not os.path.exists(integration_file):
        print(f"Error: Could not find {integration_file}")
        return False
    
    # Replace gui_instance.filedialog with filedialog
    changes_made = False
    
    for line in fileinput.input(integration_file, inplace=True):
        if 'gui_instance.filedialog' in line:
            changes_made = True
            print(line.replace('gui_instance.filedialog', 'filedialog'), end='')
        elif 'gui_instance.messagebox' in line:
            changes_made = True
            print(line.replace('gui_instance.messagebox', 'messagebox'), end='')
        else:
            print(line, end='')
    
    if changes_made:
        print(f"Successfully updated {integration_file} to use filedialog and messagebox directly")
        return True
    else:
        print(f"No changes needed in {integration_file}")
        return True

def add_alias():
    # Path to instagram_integration.py
    integration_file = 'instagram_integration.py'
    
    # First check if the file exists
    if not os.path.exists(integration_file):
        print(f"Error: Could not find {integration_file}")
        return False
    
    # Read the file content
    with open(integration_file, 'r') as f:
        content = f.read()
    
    # Check if alias is already defined
    if 'integrate_instagram = integrate_instaloader' in content:
        print("Alias already exists, no need to add it.")
        return True
    
    # Add the alias at the end of the file
    alias_line = "\n# Alias for backward compatibility\nintegrate_instagram = integrate_instaloader\n"
    
    with open(integration_file, 'a') as f:
        f.write(alias_line)
    
    print(f"Successfully added alias to {integration_file}")
    return True

if __name__ == "__main__":
    print("Starting automatic fixes for Instagram batch processing...")
    fix_integration()
    fix_filedialog()
    add_alias()
    print("All fixes applied. Please run your application again.")