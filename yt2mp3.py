import tkinter as tk
from tkinter import messagebox
from pytubefix import YouTube
from moviepy.editor import AudioFileClip
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1
import os
import re
import threading

# Folder tujuan download
DOWNLOAD_FOLDER = r"C:\Users\FuadSajaa\Music"

# Fungsi untuk menghapus karakter ilegal pada nama file
def sanitize_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "", filename)

# Fungsi untuk mengunduh dan mengonversi video menjadi MP3
def download_mp3():
    url = url_entry.get()
    if not url:
        messagebox.showwarning("Peringatan", "Masukkan URL YouTube terlebih dahulu.")
        return

    # Menampilkan status memproses
    status_label.config(text="Memproses...")
    download_button.config(state=tk.DISABLED)

    # Menjalankan fungsi unduh di thread baru agar GUI tetap responsif
    threading.Thread(target=process_download, args=(url,)).start()

# Fungsi yang di-thread untuk download dan konversi
def process_download(url):
    try:
        yt = YouTube(url)
        title = yt.title
        channel = yt.author
        sanitized_title = sanitize_filename(title)

        # Mengunduh audio
        stream = yt.streams.filter(only_audio=True).first()
        temp_filename = stream.download(filename="temp.mp4")

        # Path file output
        output_filename = os.path.join(DOWNLOAD_FOLDER, f"{sanitized_title}.mp3")

        # Konversi ke MP3
        audio_clip = AudioFileClip(temp_filename)
        audio_clip.write_audiofile(output_filename, codec="libmp3lame")
        audio_clip.close()

        # Menambahkan metadata menggunakan Mutagen
        audio = MP3(output_filename, ID3=ID3)
        audio["TIT2"] = TIT2(encoding=3, text=title)
        audio["TPE1"] = TPE1(encoding=3, text=channel)
        audio.save()

        # Menghapus file sementara
        os.remove(temp_filename)

        # Update status dan notifikasi
        status_label.config(text="Selesai")
        messagebox.showinfo("Sukses", f"'{output_filename}' berhasil diunduh dan disimpan di {DOWNLOAD_FOLDER}")

    except Exception as e:
        status_label.config(text="Gagal")
        messagebox.showerror("Error", f"Gagal mengunduh: {e}")

    # Mengaktifkan kembali tombol download
    download_button.config(state=tk.NORMAL)

# Fungsi untuk menampilkan info video
def cek_link():
    url = url_entry.get()
    if not url:
        messagebox.showwarning("Peringatan", "Masukkan URL YouTube terlebih dahulu.")
        return

    try:
        yt = YouTube(url)
        title = yt.title
        channel = yt.author

        # Menampilkan info video
        video_info_label.config(text=f"Channel: {channel}\nJudul: {title}")
        download_button.config(state=tk.NORMAL)

    except Exception as e:
        messagebox.showerror("Error", f"Gagal memproses URL: {e}")

# GUI menggunakan Tkinter
app = tk.Tk()
app.title("YouTube to MP3 Converter")
app.geometry("400x300")
app.resizable(False, False)

# Label dan Entry untuk URL
url_label = tk.Label(app, text="Masukkan URL YouTube:")
url_label.pack(pady=10)
url_entry = tk.Entry(app, width=50)
url_entry.pack()

# Tombol Cek Link
cek_button = tk.Button(app, text="Cek Link", command=cek_link)
cek_button.pack(pady=5)

# Label untuk menampilkan info video
video_info_label = tk.Label(app, text="")
video_info_label.pack(pady=10)

# Label Status Proses
status_label = tk.Label(app, text="")
status_label.pack(pady=10)

# Tombol Download
download_button = tk.Button(app, text="Download MP3", command=download_mp3, state=tk.DISABLED)
download_button.pack(pady=10)

# Menjalankan GUI
app.mainloop()
