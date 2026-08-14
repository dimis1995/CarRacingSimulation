import pygame


class Track:

    def __init__(self, margin: int, width: int, height: int, track_width: int, surface: pygame.Surface):
        self.background_color = "green"
        self.font_color = "gray"
        self.border_radius = 80
        self.track_width = track_width
        self.outer_rect = pygame.Rect(margin, margin, width - 2*margin, height - 2*margin)
        self.inner_rect = self.outer_rect.inflate(-2*track_width, -2*track_width)
        self.surface = surface

    @property
    def get_start_position_x(self):
        return self.outer_rect.centerx

    @property
    def get_start_position_y(self):
        return (self.outer_rect.bottom + self.inner_rect.bottom) / 2


    def zone(self, point: pygame.Vector2):
        if self.inner_rect.collidepoint(point):
            return "green"
        elif self.outer_rect.collidepoint(point):
            return "gray"
        else:
            return "outside"


    def draw(self):
        pygame.draw.rect(self.surface, self.font_color, self.outer_rect)
        pygame.draw.rect(self.surface, self.background_color, self.inner_rect)