import flet as ft
import pygame
import os
import asyncio
from mutagen.mp3 import MP3

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 400, 500
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Lista de Canciones")
FONT = pygame.font.Font(None, 30)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)

class Node:
    def __init__(self, song):
        self.song = song
        self.next = None
        self.prev = None

class DoublyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.current = None

    def append(self, song):
        new_node = Node(song)
        if self.head is None:
            self.head = self.tail = self.current = new_node
        else:
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node

    def next_song(self):
        if self.current and self.current.next:
            self.current = self.current.next
        return self.current.song

    def prev_song(self):
        if self.current and self.current.prev:
            self.current = self.current.prev
        return self.current.song

class Song:
    def __init__(self, filename):
        self.filename = filename
        self.title = os.path.splitext(filename)[0]
        self.duration = self.get_duration()

    def get_duration(self):
        audio = MP3(os.path.join("Canciones", self.filename))
        return audio.info.length

async def main(page: ft.Page):
    page.title = "Reproductor de Música"
    page.bgcolor = ft.colors.BLUE_GREY_900
    page.padding = 20

    pygame.mixer.init()
    playlist = DoublyLinkedList()
    for f in os.listdir("Canciones"):
        if f.endswith(".mp3"):
            playlist.append(Song(f))

    def load_song(song):
        pygame.mixer.music.load(os.path.join("Canciones", song.filename))

    def play_pause(e):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            play_button.icon = ft.icons.PLAY_ARROW
        else:
            if pygame.mixer.music.get_pos() == -1:
                load_song(playlist.current.song)
                pygame.mixer.music.play()
            else:
                pygame.mixer.music.unpause()
            play_button.icon = ft.icons.PAUSE
        page.update()

    def change_song(next=True):
        if next:
            song = playlist.next_song()
        else:
            song = playlist.prev_song()
        load_song(song)
        pygame.mixer.music.play()
        update_song_info()
        play_button.icon = ft.icons.PAUSE
        page.update()

    def update_song_info():
        song = playlist.current.song
        song_info.value = f"{song.title}"
        duration.value = format_time(song.duration)
        progress_bar.value = 0.0
        current_time_text.value = "00:00"
        page.update()

    def format_time(seconds):
        minutes, seconds = divmod(int(seconds), 60)
        return f"{minutes:02d}:{seconds:02d}"

    async def update_progress():
        while True:
            if pygame.mixer.music.get_busy():
                current_time = pygame.mixer.music.get_pos() / 1000
                progress_bar.value = current_time / playlist.current.song.duration
                current_time_text.value = format_time(current_time)
                page.update()
            await asyncio.sleep(1)

    def draw_playlist():
        screen.fill((30, 30, 30))
        y_offset = 50
        node = playlist.head
        index = 0

        while node:
            color = WHITE if node == playlist.current else GRAY
            text_surface = FONT.render(node.song.title, True, color)
            screen.blit(text_surface, (50, y_offset + index * 40))
            node = node.next
            index += 1

        pygame.display.flip()

    async def pygame_loop():
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        change_song(True)
                    elif event.key == pygame.K_UP:
                        change_song(False)

            draw_playlist()
            await asyncio.sleep(0.1)

    titulo = ft.Text("RicarMix", size=30, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE)

    song_info = ft.Text(size=20, color=ft.colors.WHITE)
    current_time_text = ft.Text("00:00", color=ft.colors.WHITE60)
    duration = ft.Text("00:00", color=ft.colors.WHITE60)
    progress_bar = ft.ProgressBar(value=0.0, width=300, color="white", bgcolor="red")

    play_button = ft.IconButton(icon=ft.icons.PLAY_ARROW, on_click=play_pause, icon_color=ft.colors.WHITE)
    prev_button = ft.IconButton(icon=ft.icons.SKIP_PREVIOUS, on_click=lambda _: change_song(False), icon_color=ft.colors.WHITE)
    next_button = ft.IconButton(icon=ft.icons.SKIP_NEXT, on_click=lambda _: change_song(True), icon_color=ft.colors.WHITE)

    controls = ft.Row(
        [prev_button, play_button, next_button],
        alignment=ft.MainAxisAlignment.CENTER
    )

    fila_reproductor = ft.Row(
        [current_time_text, progress_bar, duration],
        alignment=ft.MainAxisAlignment.CENTER
    )

    columna = ft.Column(
        [titulo, song_info, fila_reproductor, controls],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20
    )

    page.add(columna)

    if playlist.head:
        load_song(playlist.current.song)
        update_song_info()
        page.update()
        await asyncio.gather(update_progress(), pygame_loop())
    else:
        song_info.value = "No se encontró ninguna canción en la carpeta 'Canciones'"
        page.update()

ft.app(target=main)
