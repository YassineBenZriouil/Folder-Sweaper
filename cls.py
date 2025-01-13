import os
import logging
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# Configure logging to save deleted folder details
logging.basicConfig(
    filename="deleted_folders.log",
    level=logging.INFO,
    format="%(asctime)s - Deleted: %(message)s",
)

class FolderCleanerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Empty Folder Cleaner")
        self.root.geometry("600x450")
        self.root.resizable(False, False)

        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Variable to track whether to skip confirmations
        self.skip_confirmations = False

        self.create_widgets()

    def create_widgets(self):
        # Frame for directory selection
        dir_frame = ttk.Frame(self.root)
        dir_frame.pack(pady=10)

        self.dir_entry = ttk.Entry(dir_frame, width=50)
        self.dir_entry.pack(side=tk.LEFT, padx=5)

        self.browse_button = ttk.Button(dir_frame, text="Browse", command=self.browse_directory)
        self.browse_button.pack(side=tk.LEFT)

        # Frame for progress bar
        progress_frame = ttk.Frame(self.root)
        progress_frame.pack(pady=10)

        self.progress = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, length=500, mode='determinate')
        self.progress.pack()

        # Text widget to display logs
        self.log_text = tk.Text(self.root, height=15, width=70, state=tk.DISABLED)
        self.log_text.pack(pady=10)

        # Frame for buttons
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)

        self.start_button = ttk.Button(button_frame, text="Start Cleaning", command=self.start_cleaning)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.skip_button = ttk.Button(button_frame, text="Skip All Confirmations", command=self.toggle_skip_confirmations)
        self.skip_button.pack(side=tk.LEFT, padx=5)

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, directory)

    def log_message(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.config(state=tk.DISABLED)
        self.log_text.see(tk.END)

    def toggle_skip_confirmations(self):
        self.skip_confirmations = not self.skip_confirmations
        if self.skip_confirmations:
            self.skip_button.config(text="Enable Confirmations")
            self.log_message("Skipping all confirmations. Empty folders will be deleted directly.")
        else:
            self.skip_button.config(text="Skip All Confirmations")
            self.log_message("Confirmations enabled. You will be prompted before deleting folders.")

    def start_cleaning(self):
        user_path = self.dir_entry.get().strip()
        if not os.path.exists(user_path) or not os.path.isdir(user_path):
            messagebox.showerror("Error", "Invalid path. Please enter a valid directory path.")
            return

        self.start_button.config(state=tk.DISABLED)
        self.skip_button.config(state=tk.DISABLED)
        self.progress['value'] = 0
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

        deleted_count = self.delete_empty_folders(user_path)
        self.progress['value'] = 100
        self.log_message(f"\nCleanup complete. Total empty folders deleted: {deleted_count}")
        self.log_message("Deleted folder paths saved in 'deleted_folders.log'.")
        self.start_button.config(state=tk.NORMAL)
        self.skip_button.config(state=tk.NORMAL)

    def delete_empty_folders(self, path):
        deleted_count = 0
        total_folders = sum([len(dirs) for _, dirs, _ in os.walk(path)])
        self.progress['maximum'] = total_folders

        for root, dirs, _ in os.walk(path, topdown=False):  # Bottom-up traversal
            for folder in dirs:
                folder_path = os.path.join(root, folder)
                try:
                    if not os.listdir(folder_path):  # Check if the folder is empty
                        if self.skip_confirmations:
                            os.rmdir(folder_path)
                            logging.info(folder_path)  # Log the deleted folder
                            self.log_message(f"Deleted: {folder_path}")
                            deleted_count += 1
                        else:
                            confirm = messagebox.askyesno("Confirm Deletion", f"Confirm deletion of {folder_path}?")
                            if confirm:
                                os.rmdir(folder_path)
                                logging.info(folder_path)  # Log the deleted folder
                                self.log_message(f"Deleted: {folder_path}")
                                deleted_count += 1
                            else:
                                self.log_message(f"Skipped: {folder_path}")
                except PermissionError:
                    self.log_message(f"Permission denied: {folder_path}")
                except Exception as e:
                    self.log_message(f"Error deleting {folder_path}: {e}")
                finally:
                    self.progress['value'] += 1
                    self.root.update_idletasks()

        return deleted_count

if __name__ == "__main__":
    root = tk.Tk()
    app = FolderCleanerApp(root)
    root.mainloop()