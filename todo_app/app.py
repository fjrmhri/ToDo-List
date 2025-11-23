"""Logika utama aplikasi todo berbasis Pygame."""

import logging
import time
from pathlib import Path

import pygame
from pygame import Rect

from todo_app.animations import Vibration, WaveBackground
from todo_app.models import TodoItem
from todo_app.utils import blur_surface, clip_text_to_width


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TodoApp:
    """Mengelola state, event, dan render aplikasi todo."""

    def __init__(self, width: int = 1080, height: int = 700):
        pygame.init()
        pygame.display.set_caption("Minimalist Todo")
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.running = True

        font_path = Path(__file__).parent / "assets" / "fonts" / "Monocraft.otf"
        try:
            if font_path.exists():
                self.font = pygame.font.Font(font_path.as_posix(), 21)
                self.small_font = pygame.font.Font(font_path.as_posix(), 16)
                self.title_font = pygame.font.Font(font_path.as_posix(), 30)
                self.mono_font = pygame.font.Font(font_path.as_posix(), 15)
            else:
                self.font = pygame.font.SysFont("fira sans", 21) or pygame.font.SysFont(None, 21)
                self.small_font = pygame.font.SysFont("fira sans", 16) or pygame.font.SysFont(None, 16)
                self.title_font = pygame.font.SysFont("fira sans", 30) or pygame.font.SysFont(None, 30)
                self.mono_font = pygame.font.SysFont("jetbrains mono", 15) or self.small_font
        except Exception as exc:  # noqa: BLE001
            logger.exception("Gagal memuat font, menggunakan fallback.", exc_info=exc)
            self.font = pygame.font.SysFont(None, 21)
            self.small_font = pygame.font.SysFont(None, 16)
            self.title_font = pygame.font.SysFont(None, 30)
            self.mono_font = pygame.font.SysFont(None, 15)

        self.palette = {
            "bg": (8, 10, 24),
            "panel": (14, 18, 32),
            "panel_light": (22, 28, 44),
            "accent": (0, 231, 183),
            "accent_alt": (255, 140, 92),
            "text": (236, 242, 255),
            "muted": (148, 160, 185),
            "outline": (58, 76, 112),
        }

        self.todos: list[TodoItem] = []
        self.item_height = 70
        self.item_width = 560
        self.item_spacing = 14
        self.list_origin = (90, 150)

        self.input_text = ""
        self.input_active = False
        self.typing_feedback_timer = 0.0
        self.vibration = Vibration()

        self.alerts: list[dict] = []
        self.modal_item: TodoItem | None = None

        self.wave_background = WaveBackground(self.width, self.height, line_count=8)
        self.elapsed_time = 0.0

    def add_alert(self, text: str, duration: float = 2.4):
        """Menambahkan pesan singkat yang hilang sendiri setelah durasi tertentu."""

        self.alerts.append({"text": text, "timer": duration})

    def add_todo(self):
        cleaned = self.input_text.strip()
        if not cleaned:
            self.add_alert("Cannot add an empty todo.")
            return
        self.todos.append(TodoItem(text=cleaned))
        self.input_text = ""

    def remove_todo(self, todo_id: int):
        """Menghapus todo berdasarkan ID dan memberi log jika tidak ditemukan."""

        before = len(self.todos)
        self.todos = [t for t in self.todos if t.id != todo_id]
        if len(self.todos) == before:
            logger.warning("ID todo tidak ditemukan saat hapus: %s", todo_id)

    def toggle_todo(self, todo_id: int):
        """Membalik status selesai todo tertentu; log peringatan jika ID salah."""

        for todo in self.todos:
            if todo.id == todo_id:
                todo.completed = not todo.completed
                break
        else:
            logger.warning("ID todo tidak ditemukan saat toggle: %s", todo_id)

    def open_modal(self, todo: TodoItem):
        """Menampilkan modal detail untuk todo yang dipilih."""

        self.modal_item = todo

    def close_modal(self):
        """Menutup modal detail aktif bila ada."""

        self.modal_item = None

    def handle_events(self, item_layout):
        """Memproses event keyboard dan mouse, termasuk fokus input serta klik elemen."""

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logger.info("Permintaan keluar diterima, menutup aplikasi.")
                self.running = False
                return

            if event.type == pygame.KEYDOWN:
                if self.modal_item and event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                    self.close_modal()
                    continue

                if self.input_active:
                    self.typing_feedback_timer = 0.35
                    if event.key == pygame.K_RETURN:
                        self.add_todo()
                    elif event.key == pygame.K_BACKSPACE:
                        self.input_text = self.input_text[:-1]
                    else:
                        if event.unicode and event.unicode.isprintable():
                            self.input_text += event.unicode
                elif event.key == pygame.K_RETURN and not self.modal_item:
                    self.input_active = True

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                if self.modal_item:
                    self.close_modal()
                    continue

                input_rect = self.get_input_rect()
                if input_rect.collidepoint(mouse_pos):
                    self.input_active = True
                else:
                    self.input_active = False

                for layout in item_layout:
                    if layout["checkbox"].collidepoint(mouse_pos):
                        self.toggle_todo(layout["todo"].id)
                        break
                    if layout["delete"].collidepoint(mouse_pos):
                        self.remove_todo(layout["todo"].id)
                        break
                    if layout["rect"].collidepoint(mouse_pos):
                        self.open_modal(layout["todo"])
                        break

    def get_item_layout(self):
        """Membuat posisi rectangle untuk kartu, checkbox, dan tombol hapus."""

        layout = []
        x, y_start = self.list_origin
        checkbox_size = 28
        delete_size = 28
        right_padding = 32
        for idx, todo in enumerate(self.todos):
            y = y_start + idx * (self.item_height + self.item_spacing)
            rect = Rect(x, y, self.item_width, self.item_height)
            checkbox = Rect(
                rect.right - right_padding - delete_size - checkbox_size,
                rect.centery - checkbox_size // 2,
                checkbox_size,
                checkbox_size,
            )
            delete = Rect(
                rect.right - right_padding - delete_size,
                rect.centery - delete_size // 2,
                delete_size,
                delete_size,
            )
            layout.append({"todo": todo, "rect": rect, "checkbox": checkbox, "delete": delete})
        return layout

    def draw_items(self, surface: pygame.Surface, layout, mouse_pos):
        """Menggambar kartu todo beserta indikator status dan kontrolnya."""
        for item in layout:
            todo = item["todo"]
            rect = item["rect"]
            checkbox_rect = item["checkbox"]
            delete_rect = item["delete"]

            hovered = rect.collidepoint(mouse_pos)

            card = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            base_boost = 18 if hovered else 0
            base_color = tuple(min(255, c + base_boost) for c in (*self.palette["panel"],))
            corner_radius = 18
            accent_width = 15
            pygame.draw.rect(card, (*base_color, 205), card.get_rect(), border_radius=corner_radius)

            accent = self.palette["accent"] if not todo.completed else self.palette["accent_alt"]
            pygame.draw.rect(card, (*accent, 120), pygame.Rect(0, 0, accent_width, rect.height), border_radius=corner_radius)

            sheen = pygame.Surface((rect.width, rect.height // 2), pygame.SRCALPHA)
            pygame.draw.rect(sheen, (255, 255, 255, 14), sheen.get_rect(), border_radius=corner_radius)
            card.blit(sheen, (0, 0))

            if hovered:
                glint = pygame.Surface((80, rect.height), pygame.SRCALPHA)
                pygame.draw.rect(glint, (255, 255, 255, 22), glint.get_rect(), border_radius=corner_radius)
                glint_x = int((self.elapsed_time * 140 + rect.y) % (rect.width + 120)) - 60
                card.blit(glint, (glint_x, 0))

            text_area_width = rect.width - 170
            clipped = clip_text_to_width(todo.text, self.font, text_area_width)
            text_color = self.palette["muted"] if todo.completed else self.palette["text"]
            text_surface = self.font.render(clipped, True, text_color)
            card.blit(text_surface, (20, (rect.height - text_surface.get_height()) // 2))

            checkbox_rel = checkbox_rect.move(-rect.x, -rect.y)
            delete_rel = delete_rect.move(-rect.x, -rect.y)

            pygame.draw.circle(card, self.palette["outline"], checkbox_rel.center, checkbox_rel.width // 2, 2)
            if todo.completed:
                pygame.draw.circle(card, accent, checkbox_rel.center, checkbox_rel.width // 2 - 4)
            else:
                pygame.draw.circle(card, (*self.palette["text"],), checkbox_rel.center, 4)

            pygame.draw.rect(card, self.palette["outline"], delete_rel, width=2, border_radius=8)
            cross_start = (delete_rel.x + 7, delete_rel.y + 7)
            cross_end = (delete_rel.right - 7, delete_rel.bottom - 7)
            pygame.draw.line(card, self.palette["text"], cross_start, cross_end, 2)
            pygame.draw.line(card, self.palette["text"], (cross_start[0], cross_end[1]), (cross_end[0], cross_start[1]), 2)

            outline_alpha = 150 if hovered else 90
            pygame.draw.rect(card, (*self.palette["outline"], outline_alpha), card.get_rect(), width=1, border_radius=corner_radius)

            surface.blit(card, rect)

    def draw_input(self, surface: pygame.Surface, dt: float):
        """Menggambar area input dengan garis bawah dan kursor berkedip."""
        rect = self.get_input_rect()
        jitter = (0, 0)
        if self.input_active and self.typing_feedback_timer > 0:
            jitter = self.vibration.jitter(dt)
            self.typing_feedback_timer = max(0.0, self.typing_feedback_timer - dt)

        text_color = self.palette["outline"]
        base_x = rect.x + 8
        base_y = rect.y + (rect.height - self.font.get_height()) // 2

        text_width = 0
        if self.input_text:
            text_surface = self.font.render(self.input_text, True, text_color)
            surface.blit(text_surface, (base_x + jitter[0], base_y + jitter[1]))
            text_width = text_surface.get_width()

        caret_visible = int((self.elapsed_time * 2) % 2) == 0
        if self.input_active and caret_visible:
            caret_x = base_x + text_width + 2 + jitter[0]
            caret_y = base_y - 2 + jitter[1]
            pygame.draw.line(surface, text_color, (caret_x, caret_y), (caret_x, caret_y + self.font.get_height() + 4), 2)

        underline_y = rect.bottom - 6
        pygame.draw.line(surface, (*self.palette["outline"], 160), (base_x, underline_y), (rect.x + rect.width - 12, underline_y), 2)

    def get_input_rect(self):
        return Rect(self.list_origin[0], self.height - 86, self.item_width, 52)

    def draw_alerts(self, surface: pygame.Surface, dt: float):
        """Merender pesan alert ringan dan mengurangi timer kedaluwarsa."""

        if not self.alerts:
            return
        y = 12
        for alert in list(self.alerts):
            text_surf = self.small_font.render(alert["text"], True, self.palette["text"])
            background = pygame.Surface((text_surf.get_width() + 26, text_surf.get_height() + 14), pygame.SRCALPHA)
            pygame.draw.rect(background, (*self.palette["panel_light"], 180), background.get_rect(), border_radius=10)
            pygame.draw.rect(background, self.palette["accent"], background.get_rect(), width=1, border_radius=10)
            background.blit(text_surf, (12, 7))
            surface.blit(background, (self.width - background.get_width() - 24, y))
            y += background.get_height() + 10
            alert["timer"] -= dt
            if alert["timer"] <= 0:
                self.alerts.remove(alert)

    def draw_modal(self, surface: pygame.Surface):
        """Menggambar modal detail ketika ada todo yang dipilih."""

        if not self.modal_item:
            return
        # Overlay semi-transparan untuk memisahkan fokus pengguna.
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((4, 6, 14, 180))
        surface.blit(overlay, (0, 0))

        border_color = self.palette["accent"] if not self.modal_item.completed else self.palette["accent_alt"]
        box_width = min(self.width - 200, 540)
        box_height = 200
        rect = Rect((self.width - box_width) // 2, (self.height - box_height) // 2, box_width, box_height)
        panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(panel, (*self.palette["panel_light"], 230), panel.get_rect(), border_radius=18)
        pygame.draw.rect(panel, border_color, panel.get_rect(), width=2, border_radius=18)

        title = self.title_font.render("Todo Details", True, self.palette["text"])
        title_rect = title.get_rect()
        title_rect.centerx = rect.width // 2
        title_rect.y = 20
        panel.blit(title, title_rect)

        body_rect = Rect(24, 72, rect.width - 48, rect.height - 92)
        words = self.modal_item.text
        wrapped = self.wrap_text(words, self.font, body_rect.width)
        y = body_rect.y
        for line in wrapped:
            line_surf = self.font.render(line, True, self.palette["text"])
            panel.blit(line_surf, (body_rect.x, y))
            y += line_surf.get_height() + 6

        surface.blit(panel, rect)

    def draw_header(self):
        title = self.title_font.render("To-Do List", True, self.palette["outline"])
        self.screen.blit(title, (self.list_origin[0], 46))
        credit = self.small_font.render("github.com/fjrmhri", True, self.palette["outline"])
        credit_pos = (self.width - credit.get_width() - 16, self.height - credit.get_height() - 12)
        self.screen.blit(credit, credit_pos)

    def draw_stats(self):
        """Menampilkan ringkasan total, selesai, dan aktif di panel samping."""

        total = len(self.todos)
        completed = len([t for t in self.todos if t.completed])
        pending = total - completed

        stats_rect = Rect(self.list_origin[0] + self.item_width + 48, self.list_origin[1] - 30, 240, 140)
        panel = pygame.Surface((stats_rect.width, stats_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(panel, (*self.palette["panel_light"], 210), panel.get_rect(), border_radius=18)
        pygame.draw.rect(panel, self.palette["outline"], panel.get_rect(), width=1, border_radius=18)

        bar_rect = Rect(16, 20, stats_rect.width - 32, 10)
        pygame.draw.rect(panel, (*self.palette["outline"], 130), bar_rect, border_radius=8)
        if total > 0:
            completion_ratio = completed / total
            fill_width = max(4, int(bar_rect.width * completion_ratio))
            pygame.draw.rect(panel, self.palette["accent"], Rect(bar_rect.x, bar_rect.y, fill_width, bar_rect.height), border_radius=8)

        stat_text = [
            ("total", total, self.palette["text"]),
            ("done", completed, self.palette["accent"]),
            ("active", pending, self.palette["accent_alt"]),
        ]
        y = 44
        for label_text, value, color in stat_text:
            text = self.mono_font.render(f"{label_text.upper():<7} {value}", True, color)
            panel.blit(text, (16, y))
            y += text.get_height() + 6

        self.screen.blit(panel, stats_rect)

    def wrap_text(self, text: str, font: pygame.font.Font, max_width: int):
        """Membungkus teks panjang menjadi beberapa baris agar muat di area modal."""
        words = text.split()
        lines = []
        current = ""
        for word in words:
            test_line = word if not current else f"{current} {word}"
            if font.size(test_line)[0] <= max_width:
                current = test_line
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines or [text]

    def render_base(self, dt: float, layout):
        """Memperbarui animasi dasar lalu menggambar elemen UI utama."""
        self.wave_background.update(dt)
        mouse_pos = pygame.mouse.get_pos()
        self.wave_background.draw(self.screen, mouse_pos)

        self.draw_header()
        self.draw_stats()

        self.draw_items(self.screen, layout, mouse_pos)
        self.draw_input(self.screen, dt)
        self.draw_alerts(self.screen, dt)

    def run(self):
        """Loop utama aplikasi yang menangani event, render, dan timing."""
        last_time = time.time()
        while self.running:
            now = time.time()
            dt = now - last_time
            last_time = now
            self.elapsed_time += dt

            layout = self.get_item_layout()
            try:
                self.handle_events(layout)
            except Exception as exc:  # noqa: BLE001
                logger.exception("Kesalahan saat memproses input.", exc_info=exc)
                self.add_alert("Unexpected input error.")
                continue

            if not self.running:
                break

            try:
                self.render_base(dt, layout)
            except Exception as exc:  # noqa: BLE001
                logger.exception("Kesalahan saat merender frame.", exc_info=exc)
                self.add_alert("Rendering hiccup.")
                continue

            if self.modal_item:
                base_snapshot = self.screen.copy()
                blurred = blur_surface(base_snapshot, scale_factor=0.12)
                self.screen.blit(blurred, (0, 0))
                self.draw_modal(self.screen)

            pygame.display.flip()
            self.clock.tick(60)

        logger.info("Loop utama selesai, aplikasi ditutup.")
        pygame.quit()


def main():
    app = TodoApp()
    app.run()


if __name__ == "__main__":
    main()

