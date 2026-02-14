import pygame
import random
from PIL import Image
import tkinter as tk
from tkinter import filedialog

# ------------------
# НАСТРОЙКИ
# ------------------
WINDOW_SIZE = 800
GRID_SIZE = 7       # Размер кусочка
BACKGROUND_COLOR = (30, 30, 30)
GRID_COLOR = (70, 70, 70)


# ------------------
# ВЫБОР ФАЙЛА
# ------------------
def choose_image():
    selected_file = {"path": None}

    def open_file_dialog():
        file_path = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[("Images", "*.png *.jpg *.jpeg")]
        )
        if file_path:
            selected_file["path"] = file_path
            root.destroy()

    root = tk.Tk()
    root.title("🧩 Puzzle Game 😊")
    root.geometry("350x200")
    root.resizable(False, False)

    label = tk.Label(root, text="🧩 Puzzle Game 😊", font=("Arial", 18))
    label.pack(pady=20)

    button = tk.Button(
        root,
        text="Выберите файл фото",
        font=("Arial", 12),
        command=open_file_dialog
    )
    button.pack(pady=10)

    root.mainloop()

    return selected_file["path"]


# ------------------
# КЛАСС ПАЗЛА
# ------------------
class PuzzlePiece:
    def __init__(self, image, correct_index, current_index, size):
        self.image = image
        self.correct_index = correct_index
        self.current_index = current_index
        self.size = size
        self.rect = pygame.Rect(0, 0, size, size)
        self.update_position()
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0

    def update_position(self):
        row = self.current_index // GRID_SIZE
        col = self.current_index % GRID_SIZE
        self.rect.x = col * self.size
        self.rect.y = row * self.size

    def draw(self, screen):
        screen.blit(self.image, self.rect)


# ------------------
# НАРЕЗКА И МАСШТАБИРОВАНИЕ
# ------------------
def slice_image(path):
    img = Image.open(path)
    img = img.convert("RGB")

    img = img.resize((WINDOW_SIZE, WINDOW_SIZE))
    piece_size = WINDOW_SIZE // GRID_SIZE

    pieces = []

    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            left = col * piece_size
            top = row * piece_size
            right = left + piece_size
            bottom = top + piece_size

            piece = img.crop((left, top, right, bottom))
            mode = piece.mode
            data = piece.tobytes()

            pygame_image = pygame.image.fromstring(data, piece.size, mode)
            pieces.append(pygame_image)

    return pieces, piece_size


# ------------------
# СОЗДАНИЕ ПАЗЛА
# ------------------
def create_puzzle(piece_images, piece_size):
    pieces = []

    indices = list(range(len(piece_images)))
    shuffled = indices.copy()
    random.shuffle(shuffled)

    for i in range(len(piece_images)):
        piece = PuzzlePiece(
            piece_images[i],
            correct_index=i,
            current_index=shuffled[i],
            size=piece_size
        )
        pieces.append(piece)

    return pieces


# ------------------
# ОСНОВНОЙ ЦИКЛ
# ------------------
def main():
    image_path = choose_image()
    if not image_path:
        print("Файл не выбран.")
        return

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
    pygame.display.set_caption("Puzzle Game")

    piece_images, piece_size = slice_image(image_path)
    pieces = create_puzzle(piece_images, piece_size)

    clock = pygame.time.Clock()
    running = True
    selected_piece = None

    while running:
        screen.fill(BACKGROUND_COLOR)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # НАЖАТИЕ
            if event.type == pygame.MOUSEBUTTONDOWN:
                for piece in reversed(pieces):
                    if piece.rect.collidepoint(event.pos):
                        selected_piece = piece
                        piece.dragging = True
                        piece.offset_x = piece.rect.x - event.pos[0]
                        piece.offset_y = piece.rect.y - event.pos[1]
                        pieces.remove(piece)
                        pieces.append(piece)
                        break

            # ОТПУСКАНИЕ
            if event.type == pygame.MOUSEBUTTONUP:
                if selected_piece:
                    selected_piece.dragging = False

                    # Определяем индекс клетки
                    col = selected_piece.rect.centerx // piece_size
                    row = selected_piece.rect.centery // piece_size
                    new_index = row * GRID_SIZE + col

                    # Проверяем границы
                    if 0 <= new_index < len(pieces):
                        # Ищем кусок который стоит там
                        for piece in pieces:
                            if piece.current_index == new_index:
                                # SWAP
                                piece.current_index = selected_piece.current_index
                                piece.update_position()
                                break

                        selected_piece.current_index = new_index

                    selected_piece.update_position()
                    selected_piece = None

            # ПЕРЕТАСКИВАНИЕ
            if event.type == pygame.MOUSEMOTION:
                if selected_piece and selected_piece.dragging:
                    selected_piece.rect.x = event.pos[0] + selected_piece.offset_x
                    selected_piece.rect.y = event.pos[1] + selected_piece.offset_y

        # РИСУЕМ СЕТКУ
        for i in range(GRID_SIZE + 1):
            pygame.draw.line(screen, GRID_COLOR, (0, i * piece_size), (WINDOW_SIZE, i * piece_size))
            pygame.draw.line(screen, GRID_COLOR, (i * piece_size, 0), (i * piece_size, WINDOW_SIZE))

        # РИСУЕМ КУСОЧКИ
        for piece in pieces:
            piece.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
