from ui.settings import *
from datetime import datetime

from ui.base_screen import BaseScreen

class FileDetailScreen(BaseScreen):
    def __init__(self, manager):
        
        # general
        super().__init__(manager)
        self.tag = 'FileDetails'

        self.disp_surf = pygame.display.get_surface()
        self.title_font = get_font(20)
        self.font = get_font(15)

        # components
        self.filepath = None

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                self.manager.go_back()
    
    def format_size(self, size_bytes):
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"

    def get_file_details(self, filepath):
        stat = filepath.stat()
        size_str = self.format_size(stat.st_size)
        mod_str = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
        return {
            "name": filepath.name,
            "size": size_str,
            "modified": mod_str
        }
    
    def truncate_text(self, text, font, max_width):
        if font.size(text)[0] <= max_width:
            return text
        while text and font.size(text + "...")[0] > max_width:
            text = text[:-1]
        return text + "..."

    def draw(self):
        self.disp_surf.fill(GRAY)

        title_surf = self.title_font.render("File details", True, 'white')
        title_rect = title_surf.get_rect(center=(win_w / 2, tb_h/2 + vert_padding))
        self.disp_surf.blit(title_surf, title_rect)

        details = self.get_file_details(self.filepath)

        frame = pygame.Rect(0,0, menu_w, menu_h)
        frame.center = (win_w / 2, win_h - tb_h - menu_h / 2)
        pygame.draw.rect(self.disp_surf, LINE_COLOR, frame, 2, 4)

        lines = [
            f"Name: {self.truncate_text(details['name'], self.font, frame.width - 2 * hori_padding)}",
            f"Size: {self.truncate_text(details['size'], self.font, frame.width - 2 * hori_padding)}",
            f"Modified: {self.truncate_text(details['modified'], self.font, frame.width - 2 * hori_padding)}",
        ]

        for i, line in enumerate(lines):
            line_surf = self.font.render(line, True, "white")
            line_rect = line_surf.get_rect(topleft=(frame.left + hori_padding, frame.top + (2*i + 1) * vert_padding))
            self.disp_surf.blit(line_surf, line_rect)