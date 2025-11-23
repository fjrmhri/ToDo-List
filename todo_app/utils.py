import pygame


def clip_text_to_width(text: str, font: pygame.font.Font, max_width: int) -> str:
    """Memotong teks agar pas ke lebar piksel maksimum dengan menambahkan elipsis jika perlu."""
    if font.size(text)[0] <= max_width:
        return text

    ellipsis_width = font.size(".")[0]
    available_width = max_width - ellipsis_width
    clipped = text
    while clipped and font.size(clipped)[0] > available_width:
        clipped = clipped[:-1]
    return f"{clipped}." if clipped else "."


def blur_surface(surface: pygame.Surface, scale_factor: float = 0.15) -> pygame.Surface:
    """Membuat efek blur sederhana dengan mengecilkan lalu membesarkan kembali permukaan."""
    if scale_factor <= 0 or scale_factor >= 1:
        return surface.copy()

    width, height = surface.get_size()
    scaled_size = (max(1, int(width * scale_factor)), max(1, int(height * scale_factor)))
    small = pygame.transform.smoothscale(surface, scaled_size)
    blurred = pygame.transform.smoothscale(small, (width, height))
    return blurred
