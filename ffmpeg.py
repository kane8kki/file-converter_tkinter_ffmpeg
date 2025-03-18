import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os

def convert_file(input_file, output_file):
    ffmpeg_path = os.path.join(os.getcwd(), "ffmpeg", "bin", "ffmpeg.exe")
    if not os.path.exists(input_file):
        messagebox.showerror("Erreur", f"Le fichier '{input_file}' n'existe pas.")
        return

    command = [ffmpeg_path, "-i", input_file, output_file]
    try:
        subprocess.run(command, check=True)
        messagebox.showinfo("Succès", f"Conversion réussie : '{input_file}' → '{output_file}'")
    except subprocess.CalledProcessError:
        messagebox.showerror("Erreur", "Erreur lors de la conversion.")

def select_input_file():
    file_path = filedialog.askopenfilename()
    input_entry.delete(0, tk.END)
    input_entry.insert(0, file_path)

def convert():
    input_file = input_entry.get().strip()
    output_file = output_entry.get().strip()
    if not input_file or not output_file:
        messagebox.showwarning("Attention", "Veuillez remplir les deux champs.")
        return
    convert_file(input_file, output_file)

# Création de la fenêtre
root = tk.Tk()
root.title("Convertisseur de Fichiers avec FFmpeg")
root.geometry("500x150")

# Widgets
input_label = tk.Label(root, text="Fichier à convertir :")
input_label.pack(anchor="w", padx=10, pady=5)
input_frame = tk.Frame(root)
input_frame.pack(fill="x", padx=10)
input_entry = tk.Entry(input_frame, width=50)
input_entry.pack(side="left", fill="x", expand=True)
input_button = tk.Button(input_frame, text="Parcourir", command=select_input_file)
input_button.pack(side="right")

output_label = tk.Label(root, text="Nom du fichier de sortie :")
output_label.pack(anchor="w", padx=10, pady=5)
output_entry = tk.Entry(root, width=50)
output_entry.pack(fill="x", padx=10)

convert_button = tk.Button(root, text="Convertir", command=convert)
convert_button.pack(pady=10)

# Lancement de l'interface
root.mainloop()
