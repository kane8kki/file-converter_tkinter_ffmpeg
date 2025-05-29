import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
import customtkinter as ctk # Import customtkinter

# --- Core Conversion Logic (with minor improvements) ---
def convert_file(input_file, output_file, progress_callback):
    """
    Converts the input file to the output file using FFmpeg.

    Args:
        input_file (str): Path to the input file.
        output_file (str): Path for the converted output file.
        progress_callback (function): Callback function to update progress (currently simulates completion).

    Returns:
        bool: True if conversion was successful, False otherwise.
    """
    # Attempt to find ffmpeg: first in a local ./ffmpeg/bin directory, then in system PATH
    local_ffmpeg_path = os.path.join(os.getcwd(), "ffmpeg", "bin", "ffmpeg.exe")
    if os.name == 'posix': # For Linux/macOS, the executable is just 'ffmpeg'
        local_ffmpeg_path = os.path.join(os.getcwd(), "ffmpeg", "bin", "ffmpeg")


    if os.path.exists(local_ffmpeg_path):
        ffmpeg_path = local_ffmpeg_path
    else:
        ffmpeg_path = "ffmpeg" # Assume ffmpeg is in system PATH

    if not os.path.exists(input_file):
        messagebox.showerror("Erreur de Fichier", f"Le fichier d'entrée '{input_file}' n'existe pas.")
        if progress_callback:
            progress_callback(0, "Erreur: Fichier d'entrée non trouvé.")
        return False

    # Ensure the output directory exists
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
        except OSError as e:
            messagebox.showerror("Erreur de Répertoire", f"Impossible de créer le répertoire de sortie '{output_dir}': {e}")
            if progress_callback:
                progress_callback(0, f"Erreur: Impossible de créer le répertoire de sortie.")
            return False

    command = [
        ffmpeg_path,
        "-i", input_file,
        output_file,
        "-y"  # Overwrite output file if it exists
    ]

    try:
        # For real-time progress, ffmpeg's stdout/stderr needs to be parsed.
        # This is a simplified version.
        # Using CREATE_NO_WINDOW to prevent the ffmpeg console from appearing on Windows.
        startupinfo = None
        if os.name == 'nt': # Windows
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE # Hide window

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, # Redirect stderr to stdout
            universal_newlines=True,
            startupinfo=startupinfo
        )

        # You could attempt to parse process.stdout for progress here
        # For example, looking for lines containing "time=" or "frame="
        # For now, we just wait for completion.
        for line in process.stdout:
            print(f"FFmpeg: {line.strip()}") # Log ffmpeg output (optional)
            # Example of very basic progress parsing (highly dependent on ffmpeg output format)
            # if "time=" in line and progress_callback:
            #    pass # Add logic to parse time and estimate progress

        process.wait() # Wait for the process to complete

        if process.returncode == 0:
            if progress_callback:
                progress_callback(100, f"Conversion réussie: {os.path.basename(output_file)}")
            messagebox.showinfo("Succès", f"Conversion réussie : '{os.path.basename(input_file)}' → '{os.path.basename(output_file)}'")
            return True
        else:
            error_message = f"Erreur lors de la conversion (code: {process.returncode})."
            messagebox.showerror("Erreur de Conversion", error_message + " Vérifiez la console pour les messages de FFmpeg.")
            if progress_callback:
                progress_callback(0, f"Erreur de conversion (code: {process.returncode}).")
            return False

    except FileNotFoundError:
         messagebox.showerror("Erreur FFmpeg", f"FFmpeg non trouvé. Veuillez vous assurer que '{ffmpeg_path}' est correct ou que FFmpeg est dans votre PATH système.")
         if progress_callback:
            progress_callback(0, "Erreur: FFmpeg non trouvé.")
         return False
    except Exception as e:
        messagebox.showerror("Erreur Inattendue", f"Une erreur inattendue est survenue: {e}")
        if progress_callback:
            progress_callback(0, f"Erreur inattendue: {e}")
        return False

# --- GUI Application using CustomTkinter ---
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Appearance ---
        ctk.set_appearance_mode("Dark")  # Modes: "System" (default), "Light", "Dark"
        ctk.set_default_color_theme("blue")  # Themes: "blue", "green", "dark-blue"

        # --- Window Setup ---
        self.title("Modern FFmpeg Converter")
        self.geometry("750x500") # Adjusted size
        self.minsize(650, 450)

        # --- Configure Grid Layout ---
        # Main window grid: 0 for banner, 1 for main content
        self.grid_rowconfigure(0, weight=0) # Banner row, fixed height
        self.grid_rowconfigure(1, weight=1) # Main content row, expands
        self.grid_columnconfigure(0, weight=1) # Single column spanning full width

        # --- Banner Frame (like a header) ---
        self.banner_frame = ctk.CTkFrame(self, height=70, corner_radius=0, fg_color=("#343638", "#2B2B2B")) # Slightly different dark color
        self.banner_frame.grid(row=0, column=0, sticky="ew", pady=(0, 0)) # No bottom padding for seamless look
        self.banner_frame.grid_propagate(False) # Prevent children from resizing this frame

        self.banner_label = ctk.CTkLabel(self.banner_frame, text="FFMPEG FILE CONVERTER",
                                         font=ctk.CTkFont(size=24, weight="bold"),
                                         text_color=("gray90", "gray90")) # Ensure good contrast
        self.banner_label.pack(expand=True, fill="both", padx=30, pady=15)


        # --- Main Content Frame (for controls) ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="transparent") # Transparent to use window bg
        self.main_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")

        # Configure grid for the main_frame (more control over internal layout)
        self.main_frame.grid_columnconfigure(1, weight=1) # Allow entry fields to expand
        # Add padding to rows for spacing
        self.main_frame.grid_rowconfigure(0, pad=10)
        self.main_frame.grid_rowconfigure(1, pad=10)
        self.main_frame.grid_rowconfigure(2, pad=20)
        self.main_frame.grid_rowconfigure(3, pad=10)
        self.main_frame.grid_rowconfigure(4, pad=5)


        # --- Input File Selection ---
        self.input_label = ctk.CTkLabel(self.main_frame, text="Fichier d'entrée :", font=ctk.CTkFont(size=14))
        self.input_label.grid(row=0, column=0, padx=(10,5), pady=(10,5), sticky="w")

        self.input_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Sélectionnez ou glissez-déposez un fichier...", height=35, font=ctk.CTkFont(size=13))
        self.input_entry.grid(row=0, column=1, padx=5, pady=(10,5), sticky="ew")

        self.browse_button = ctk.CTkButton(self.main_frame, text="Parcourir...", command=self.select_input_file, width=120, height=35, font=ctk.CTkFont(size=13))
        self.browse_button.grid(row=0, column=2, padx=(5,10), pady=(10,5), sticky="e")

        # --- Output File Selection ---
        self.output_label = ctk.CTkLabel(self.main_frame, text="Fichier de sortie :", font=ctk.CTkFont(size=14))
        self.output_label.grid(row=1, column=0, padx=(10,5), pady=5, sticky="w")

        self.output_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Nom du fichier de sortie (ex: video_convertie.mp4)", height=35, font=ctk.CTkFont(size=13))
        self.output_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="ew")

        # --- Conversion Button ---
        self.convert_button = ctk.CTkButton(
            self.main_frame,
            text="Lancer la Conversion",
            command=self.start_conversion_thread, # Use threading
            height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#4A90E2", # A nice blue
            hover_color="#357ABD"  # Darker blue on hover
        )
        self.convert_button.grid(row=2, column=0, columnspan=3, padx=10, pady=(20,10), sticky="ew")

        # --- Progress Bar ---
        self.progress_bar = ctk.CTkProgressBar(self.main_frame, orientation="horizontal", height=15)
        self.progress_bar.set(0) # Initial value
        self.progress_bar.grid(row=3, column=0, columnspan=3, padx=10, pady=(5,5), sticky="ew")

        # --- Status Label ---
        self.status_label = ctk.CTkLabel(self.main_frame, text="Prêt.", font=ctk.CTkFont(size=12), text_color="gray")
        self.status_label.grid(row=4, column=0, columnspan=3, padx=10, pady=(0,10), sticky="ew")


    def select_input_file(self):
        """Opens a file dialog to select an input file and suggests an output name."""
        file_path = filedialog.askopenfilename(
            title="Sélectionner un fichier à convertir",
            filetypes=(("Tous les fichiers vidéo/audio", "*.*"), # Add more specific types if needed
                       ("MP4 files", "*.mp4"),
                       ("MKV files", "*.mkv"),
                       ("AVI files", "*.avi"),
                       ("MOV files", "*.mov"),
                       ("MP3 files", "*.mp3"),
                       ("WAV files", "*.wav"))
        )
        if file_path:
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, file_path)
            # Suggest an output file name based on input
            base, ext = os.path.splitext(file_path)
            # You might want to allow user to choose output format later
            suggested_output = f"{base}_converted{ext}"
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, suggested_output)
            self.status_label.configure(text=f"Fichier d'entrée: {os.path.basename(file_path)}")

    def update_progress(self, value, status_text=""):
        """
        Updates the progress bar and status label.
        Value should be 0 to 100.
        """
        self.progress_bar.set(float(value) / 100.0)
        if status_text:
            self.status_label.configure(text=status_text)
        self.update_idletasks() # Force UI update

    def conversion_task(self):
        """The actual conversion logic to be run in a thread."""
        input_file = self.input_entry.get().strip()
        output_file = self.output_entry.get().strip()

        if not input_file or not output_file:
            messagebox.showwarning("Attention", "Veuillez sélectionner un fichier d'entrée et spécifier un nom de fichier de sortie.")
            self.convert_button.configure(state="normal", text="Lancer la Conversion")
            self.update_progress(0, "Prêt.")
            return

        # Basic check if output directory exists (convert_file also checks)
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
             messagebox.showerror("Erreur de Répertoire", f"Le dossier de sortie '{output_dir}' n'existe pas. Veuillez le créer ou choisir un autre emplacement.")
             self.convert_button.configure(state="normal", text="Lancer la Conversion")
             self.update_progress(0, "Erreur: Dossier de sortie invalide.")
             return

        self.update_progress(0, f"Conversion de {os.path.basename(input_file)}...")
        success = convert_file(input_file, output_file, self.update_progress) # Pass callback

        if success:
            self.update_progress(100, f"Terminé: {os.path.basename(output_file)}")
        else:
            # Error message already shown by convert_file or here
            self.update_progress(0, "Échec de la conversion.")

        self.convert_button.configure(state="normal", text="Lancer la Conversion")


    def start_conversion_thread(self):
        """Starts the conversion in a new thread to keep the UI responsive."""
        self.convert_button.configure(state="disabled", text="Traitement...")
        self.progress_bar.set(0) # Reset progress bar
        self.status_label.configure(text="Initialisation...")
        self.update_idletasks()

        # Import threading here if you only use it in this method
        import threading
        conversion_thread = threading.Thread(target=self.conversion_task, daemon=True)
        conversion_thread.start()


if __name__ == "__main__":
    app = App()
    app.mainloop()
