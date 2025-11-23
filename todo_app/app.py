import sys
import time
import pygame
from pygame import Rect

from todo_app.animations import Vibration, WaveBackground
from todo_app.models import TodoItem
from todo_app.utils import blur_surface, clip_text_to_width


class TodoApp:
    def __init__(self, width: int = 960, height: int = 640):
        pygame.init()
        pygame.display.set_caption("Minimalist Todo")
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont("fira sans", 20) or pygame.font.SysFont(None, 20)
        self.small_font = pygame.font.SysFont("fira sans", 16) or pygame.font.SysFont(None, 16)
        self.title_font = pygame.font.SysFont("fira sans", 28) or pygame.font.SysFont(None, 28)

        self.todos: list[TodoItem] = []
        self.item_height = 60
        self.item_width = 360
        self.item_spacing = 12
        self.list_origin = (40, 60)

        self.input_text = ""
        self.input_active = False
        self.typing_feedback_timer = 0.0
        self.vibration = Vibration()

        self.alerts: list[dict] = []
        self.modal_item: TodoItem | None = None

        self.wave_background = WaveBackground(self.width, self.height, line_count=7)

    def add_alert(self, text: str, duration: float = 2.4):
        self.alerts.append({"text": text, "timer": duration})

    def add_todo(self):
        cleaned = self.input_text.strip()
        if not cleaned:
            self.add_alert("Cannot add an empty todo.")
            return
        self.todos.append(TodoItem(text=cleaned))
        self.input_text = ""

    def remove_todo(self, todo_id: int):
        self.todos = [t for t in self.todos if t.id != todo_id]

    def toggle_todo(self, todo_id: int):
        for todo in self.todos:
            if todo.id == todo_id:
                todo.completed = not todo.completed
                break

    def open_modal(self, todo: TodoItem):
        self.modal_item = todo

    def close_modal(self):
        self.modal_item = None

    def handle_events(self, item_layout):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

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
                    # quick focus
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
        layout = []
        x, y_start = self.list_origin
        for idx, todo in enumerate(self.todos):
            y = y_start + idx * (self.item_height + self.item_spacing)
            rect = Rect(x, y, self.item_width, self.item_height)
            checkbox = Rect(rect.right - 68, rect.centery - 12, 24, 24)
            delete = Rect(rect.right - 34, rect.centery - 12, 24, 24)
            layout.append({"todo": todo, "rect": rect, "checkbox": checkbox, "delete": delete})
        return layout

    def draw_items(self, surface: pygame.Surface, layout):
        for item in layout:
            todo = item["todo"]
            rect = item["rect"]
            checkbox_rect = item["checkbox"]
            delete_rect = item["delete"]

            color = (255, 255, 255)
            border_color = (80, 80, 80)
            pygame.draw.rect(surface, color, rect, width=1, border_radius=8)

            text_area_width = rect.width - 120
            clipped = clip_text_to_width(todo.text, self.font, text_area_width)
            text_color = (220, 220, 220) if todo.completed else (255, 255, 255)
            text_surface = self.font.render(clipped, True, text_color)
            surface.blit(text_surface, (rect.x + 14, rect.y + (rect.height - text_surface.get_height()) // 2))

            pygame.draw.rect(surface, border_color, checkbox_rect, width=1, border_radius=4)
            if todo.completed:
                pygame.draw.rect(surface, color, checkbox_rect.inflate(-8, -8))

            pygame.draw.rect(surface, border_color, delete_rect, width=1, border_radius=4)
            cross_start = (delete_rect.x + 6, delete_rect.y + 6)
            cross_end = (delete_rect.right - 6, delete_rect.bottom - 6)
            pygame.draw.line(surface, color, cross_start, cross_end, 2)
            pygame.draw.line(surface, color, (cross_start[0], cross_end[1]), (cross_end[0], cross_start[1]), 2)

    def draw_input(self, surface: pygame.Surface, dt: float):
        rect = self.get_input_rect()
        underline_color = (255, 255, 255) if self.input_active else (80, 80, 80)
        text_color = (255, 255, 255)
        min_width = 220
        underline_width = max(min_width, self.font.size(self.input_text or " ")[0] + 18)

        underline_start = (rect.x, rect.bottom)
        underline_end = (rect.x + underline_width, rect.bottom)
        pygame.draw.line(surface, underline_color, underline_start, underline_end, 2)

        jitter = (0, 0)
        if self.input_active and self.typing_feedback_timer > 0:
            jitter = self.vibration.jitter(dt)
            self.typing_feedback_timer = max(0.0, self.typing_feedback_timer - dt)

        text_surface = self.font.render(self.input_text or "Type a new todo", True, text_color if self.input_text else (150, 150, 150))
        text_position = (rect.x + 2 + jitter[0], rect.y - text_surface.get_height() + jitter[1])
        surface.blit(text_surface, text_position)

    def get_input_rect(self):
        return Rect(self.list_origin[0], self.height - 70, self.item_width, 28)

    def draw_alerts(self, surface: pygame.Surface, dt: float):
        if not self.alerts:
            return
        y = 12
        for alert in list(self.alerts):
            text_surf = self.small_font.render(alert["text"], True, (255, 255, 255))
            background = pygame.Surface((text_surf.get_width() + 20, text_surf.get_height() + 12), pygame.SRCALPHA)
            pygame.draw.rect(background, (255, 255, 255, 30), background.get_rect(), border_radius=6)
            background.blit(text_surf, (10, 6))
            surface.blit(background, (self.width - background.get_width() - 20, y))
            y += background.get_height() + 8
            alert["timer"] -= dt
            if alert["timer"] <= 0:
                self.alerts.remove(alert)

    def draw_modal(self, surface: pygame.Surface):
        if not self.modal_item:
            return
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        surface.blit(overlay, (0, 0))

        box_width = min(self.width - 200, 520)
        box_height = 180
        rect = Rect((self.width - box_width) // 2, (self.height - box_height) // 2, box_width, box_height)
        pygame.draw.rect(surface, (255, 255, 255), rect, width=1, border_radius=12)

        title = self.title_font.render("Todo Details", True, (255, 255, 255))
        surface.blit(title, (rect.x + 24, rect.y + 20))

        body_rect = Rect(rect.x + 24, rect.y + 70, rect.width - 48, rect.height - 90)
        words = self.modal_item.text
        wrapped = self.wrap_text(words, self.font, body_rect.width)
        y = body_rect.y
        for line in wrapped:
            line_surf = self.font.render(line, True, (255, 255, 255))
            surface.blit(line_surf, (body_rect.x, y))
            y += line_surf.get_height() + 6

    def wrap_text(self, text: str, font: pygame.font.Font, max_width: int):
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
        self.wave_background.update(dt)
        self.wave_background.draw(self.screen, pygame.mouse.get_pos())

        header = self.title_font.render("Your Todos", True, (255, 255, 255))
        self.screen.blit(header, (self.list_origin[0], 20))

        pygame.draw.rect(self.screen, (255, 255, 255, 20), Rect(self.list_origin[0] - 10, self.list_origin[1] - 10, self.item_width + 20, self.height - 130), width=1, border_radius=12)

        self.draw_items(self.screen, layout)
        self.draw_input(self.screen, dt)
        self.draw_alerts(self.screen, dt)

    def run(self):
        last_time = time.time()
        while True:
            now = time.time()
            dt = now - last_time
            last_time = now

            layout = self.get_item_layout()
            try:
                self.handle_events(layout)
            except Exception as exc:  # noqa: BLE001
                print("Input error:", exc)
                self.add_alert("Unexpected input error.")
                continue

            try:
                self.render_base(dt, layout)
            except Exception as exc:  # noqa: BLE001
                print("Render error:", exc)
                self.add_alert("Rendering hiccup.")
                continue

            if self.modal_item:
                base_snapshot = self.screen.copy()
                blurred = blur_surface(base_snapshot, scale_factor=0.12)
                self.screen.blit(blurred, (0, 0))
                self.draw_modal(self.screen)

            pygame.display.flip()
            self.clock.tick(60)


def main():
    app = TodoApp()
    app.run()


if __name__ == "__main__":
    main()

