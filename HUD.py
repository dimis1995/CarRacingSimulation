import pygame

from QLearner import ACTIONS

BG_COLOR      = (20, 20, 25)
TEXT_COLOR    = (230, 230, 230)
CHOSEN_COLOR  = (255, 210, 60)


class HUD:
    """ Debug panel drawn in its own reserved strip (never overlapping the track):
        episode number, per-action Q-values for the current state, and whether the
        last action was chosen by exploring (random) or exploiting (best known Q). """

    def __init__(self, rect, font_size=18):
        self.rect = pygame.Rect( rect )
        self.font = pygame.font.SysFont( None, font_size )

    def draw(self, window, episode, learner, action, episode_score, best_score):
        pygame.draw.rect( window, BG_COLOR, self.rect )

        x = self.rect.left + 10
        y = self.rect.top + 8
        line_height = self.font.get_height() + 4

        mode = "explore (random)" if learner.last_was_random else "exploit (best Q)"
        header = f"Episode {episode}   epsilon={learner.epsilon:.3f}   chosen={action}   [{mode}]"
        self._blit_line( window, header, x, y, TEXT_COLOR )
        y += line_height + 4

        score_line = f"Score: {episode_score:.0f}    Best: {best_score:.0f}"
        self._blit_line( window, score_line, x, y, TEXT_COLOR )
        y += line_height + 4

        for name in ACTIONS:
            q = learner.last_q_values.get( name, 0.0 )
            color = CHOSEN_COLOR if name == action else TEXT_COLOR
            self._blit_line( window, f"{name:>12s}:  Q = {q:+.3f}", x, y, color )
            y += line_height

    def _blit_line(self, window, text, x, y, color):
        surface = self.font.render( text, True, color )
        window.blit( surface, ( x, y ) )
