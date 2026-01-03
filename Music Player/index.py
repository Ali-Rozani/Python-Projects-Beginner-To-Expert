import os
import pickle
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import PhotoImage
from pygame import mixer

class Player(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        mixer.init()
        
        # 1. ALWAYS load pre-kept songs from songs/ folder FIRST
        self.playlist = []
        songs_path = 'songs'
        if os.path.exists(songs_path):
            for root, dirs, files in os.walk(songs_path):
                for file in files:
                    if os.path.splitext(file)[1].lower() == '.mp3':
                        path = os.path.join(root, file).replace('\\', '/')
                        if path not in self.playlist:  # Avoid duplicates
                            self.playlist.append(path)
        
        # 2. THEN load/add user songs from pickle
        if os.path.exists('songs.pickle'):
            try:
                with open('songs.pickle', 'rb') as f:
                    user_songs = pickle.load(f)
                    for song in user_songs:
                        if song not in self.playlist:  # Avoid duplicates
                            self.playlist.append(song)
            except:
                os.remove('songs.pickle')  # Delete corrupted
        
        self.current = 0 if self.playlist else -1
        self.paused = True
        self.played = False
        
        self.create_frames()
        self.track_widgets()
        self.control_widgets()
        self.tracklist_widgets()
        
        self.master.bind('<Left>', self.prev_song)
        self.master.bind('<space>', self.play_pause_song)
        self.master.bind('<Right>', self.next_song)

    def create_frames(self):
        self.track = tk.LabelFrame(self, text='Music Track',
            font=("times new roman",15,"bold"),
            bg="grey",fg="white",bd=5,relief=tk.GROOVE)
        self.track.config(width=410,height=300)
        self.track.grid(row=0, column=0, padx=10)

        self.tracklist = tk.LabelFrame(self, text='PlayList - ' + str(len(self.playlist)),
            font=("times new roman",15,"bold"),
            bg="grey",fg="white",bd=5,relief=tk.GROOVE)
        self.tracklist.config(width=190,height=400)
        self.tracklist.grid(row=0, column=1, rowspan=3, pady=5)

        self.controls = tk.LabelFrame(self,
            font=("times new roman",15,"bold"),
            bg="white",fg="white",bd=2,relief=tk.GROOVE)
        self.controls.config(width=410,height=80)
        self.controls.grid(row=2, column=0, pady=5, padx=10)

    def track_widgets(self):
        global img
        try:
            self.canvas = tk.Label(self.track, image=img)
        except:
            self.canvas = tk.Label(self.track, text="🎵", font=("Arial", 48), bg="lightblue")
        self.canvas.configure(width=400, height=240)
        self.canvas.grid(row=0,column=0)

        self.songtrack = tk.Label(self.track, font=("times new roman",16,"bold"),
            bg="white",fg="dark blue")
        if self.playlist:
            self.songtrack['text'] = os.path.basename(self.playlist[0])
        else:
            self.songtrack['text'] = 'Chill And Vibe To The Music 🎵🎶'
        self.songtrack.config(width=30, height=1)
        self.songtrack.grid(row=1,column=0,padx=10)

    def control_widgets(self):
        self.loadSongs = tk.Button(self.controls, bg='green', fg='white', font=("Arial", 10, "bold"))
        self.loadSongs['text'] = 'Add Songs'  # Changed to "Add"
        self.loadSongs['command'] = self.add_songs  # Changed method
        self.loadSongs.grid(row=0, column=0, padx=10)

        global prev, pause, next_, play
        try:
            self.prev = tk.Button(self.controls, image=prev)
        except:
            self.prev = tk.Button(self.controls, text="⏮", font=("Arial", 16), bg="lightblue", width=3)
        self.prev['command'] = self.prev_song
        self.prev.grid(row=0, column=1, padx=2)

        try:
            self.pause = tk.Button(self.controls, image=pause)
        except:
            self.pause = tk.Button(self.controls, text="⏸", font=("Arial", 16), bg="orange", width=3)
        self.pause['command'] = self.pause_song
        self.pause.grid(row=0, column=2, padx=2)

        try:
            self.next = tk.Button(self.controls, image=next_)
        except:
            self.next = tk.Button(self.controls, text="⏭", font=("Arial", 16), bg="lightblue", width=3)
        self.next['command'] = self.next_song
        self.next.grid(row=0, column=3, padx=2)

        self.volume = tk.DoubleVar(self)
        self.slider = tk.Scale(self.controls, from_=0, to=10, orient=tk.HORIZONTAL)
        self.slider['variable'] = self.volume
        self.slider.set(8)
        mixer.music.set_volume(0.8)
        self.slider['command'] = self.change_volume
        self.slider.grid(row=0, column=4, padx=5)

    def tracklist_widgets(self):
        self.scrollbar = tk.Scrollbar(self.tracklist, orient=tk.VERTICAL)
        self.scrollbar.grid(row=0,column=1, rowspan=5, sticky='ns')

        self.list = tk.Listbox(self.tracklist, selectmode=tk.SINGLE,
            yscrollcommand=self.scrollbar.set, selectbackground='sky blue', font=("Arial", 9))
        self.enumerate_songs()
        self.list.config(height=22)
        self.list.bind('<Double-1>', self.play_song)
        self.scrollbar.config(command=self.list.yview)
        self.list.grid(row=0, column=0, rowspan=5)

    def add_songs(self):  # NEW: Adds songs instead of replacing
        songlist = []
        directory = filedialog.askdirectory()
        if directory:
            for root_, dirs, files in os.walk(directory):
                for file in files:
                    if os.path.splitext(file)[1].lower() == '.mp3':
                        path = (root_ + '/' + file).replace('\\\\','/')
                        if path not in self.playlist:  # Only add non-duplicates
                            songlist.append(path)
            
            # ADD new songs to existing playlist (preserves songs/ folder songs)
            self.playlist.extend(songlist)
            
            # Save FULL playlist to pickle
            with open('songs.pickle', 'wb') as f:
                pickle.dump(self.playlist, f)
            
            self.tracklist['text'] = 'PlayList - ' + str(len(self.playlist))
            self.enumerate_songs()
            messagebox.showinfo("Success", f"Added {len(songlist)} new songs!")

    def enumerate_songs(self):
        self.list.delete(0, tk.END)
        for index, song in enumerate(self.playlist):
            self.list.insert(index, os.path.basename(song))

    def play_pause_song(self, event):
        if self.paused:
            self.play_song()
        else:
            self.pause_song()

    def play_song(self, event=None):
        if not self.playlist:
            messagebox.showinfo("Info", "No songs in playlist! Add MP3s to songs/")
            return
        
        if event is not None:
            self.current = self.list.curselection()[0]
            for i in range(len(self.playlist)):
                self.list.itemconfigure(i, bg="white")
        
        print("Playing:", self.playlist[self.current])
        mixer.music.load(self.playlist[self.current])
        self.songtrack['anchor'] = 'w'
        self.songtrack['text'] = os.path.basename(self.playlist[self.current])
        try:
            self.pause['image'] = play
        except:
            self.pause['text'] = '⏸'
        self.paused = False
        self.played = True
        self.list.activate(self.current)
        self.list.itemconfigure(self.current, bg='sky blue')
        mixer.music.play()

    def pause_song(self):
        if not self.paused:
            self.paused = True
            mixer.music.pause()
            try:
                self.pause['image'] = pause
            except:
                self.pause['text'] = '▶'
        else:
            if not self.played:
                self.play_song()
            self.paused = False
            mixer.music.unpause()
            try:
                self.pause['image'] = play
            except:
                self.pause['text'] = '⏸'

    def prev_song(self, event=None):
        if not self.playlist:
            return
        self.master.focus_set()
        if self.current > 0:
            self.current -= 1
        else:
            self.current = 0
        self.play_song()

    def next_song(self, event=None):
        if not self.playlist:
            return
        self.master.focus_set()
        if self.current < len(self.playlist) - 1:
            self.current += 1
        else:
            self.current = 0
        self.play_song()

    def change_volume(self, event=None):
        self.v = self.volume.get()
        mixer.music.set_volume(self.v / 10)

if __name__ == '__main__':
    root = tk.Tk()
    root.geometry('620x480')
    root.title('Music Player 🎵')
    
    # Safe icon loading
    try:
        img = PhotoImage(file='icons/music.png')
        next_ = PhotoImage(file='icons/next.gif')
        prev = PhotoImage(file='icons/previous.gif')
        play = PhotoImage(file='icons/play.gif')
        pause = PhotoImage(file='icons/pause.gif')
    except:
        img, next_, prev, play, pause = None, None, None, None, None
    
    app = Player(master=root)
    app.mainloop()
