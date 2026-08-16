import pygame

from QLearner import ACTIONS

BG_COLOR    = (15, 15, 20)
NODE_COLOR  = (200, 200, 205)
LABEL_COLOR = (180, 180, 185)
POS_COLOR   = (70, 130, 255)    # weight pushes this action's Q-value up
NEG_COLOR   = (255, 90, 70)     # weight pushes this action's Q-value down

# Must match the exact order Agent.sense() builds the state vector in:
# (wall, green) per ray, for each of the 8 rays, then in_green, then speed.
FEATURE_LABELS = [ f"R{i}{'w' if j == 0 else 'g'}" for i in range( 8 ) for j in range( 2 ) ] + [ "Grn", "Spd" ]


class NetworkView:
    """ Draws the linear Q-function as a graph: one circle per input feature,
        one circle per action, one line per weight connecting them. """

    def __init__(self, rect):
        self.rect = pygame.Rect( rect )
        self.font = pygame.font.SysFont( None, 14 )

    def draw(self, window, learner):
        pygame.draw.rect( window, BG_COLOR, self.rect )

        input_x  = self.rect.left + 55
        output_x = self.rect.right - 110

        input_positions  = self._layout_positions( len( FEATURE_LABELS ), input_x )
        output_positions = self._layout_positions( len( ACTIONS ), output_x )

        max_weight = max(
            ( abs( w ) for weights in learner.weights.values() for w in weights ),
            default=0.0,
        )
        max_weight = max( max_weight, 1e-6 )   # avoid divide-by-zero before any training has happened

        for action_index, action in enumerate( ACTIONS ):
            ox, oy = output_positions[action_index]
            for feature_index, (ix, iy) in enumerate( input_positions ):
                w = learner.weights[action][feature_index]
                strength = min( abs( w ) / max_weight, 1.0 )
                color    = POS_COLOR if w >= 0 else NEG_COLOR
                width    = max( 1, round( strength * 3 ) )
                pygame.draw.line( window, color, ( ix, iy ), ( ox, oy ), width )

        for (x, y), label in zip( input_positions, FEATURE_LABELS ):
            pygame.draw.circle( window, NODE_COLOR, ( x, y ), 5 )
            self._blit_label( window, label, x - 10, y - 6, align='right' )

        for (x, y), action in zip( output_positions, ACTIONS ):
            pygame.draw.circle( window, NODE_COLOR, ( x, y ), 7 )
            self._blit_label( window, action, x + 10, y - 6, align='left' )

    def _layout_positions(self, count, x):
        top    = self.rect.top + 20
        bottom = self.rect.bottom - 20
        if count == 1:
            return [ ( x, ( top + bottom ) // 2 ) ]
        step = ( bottom - top ) / ( count - 1 )
        return [ ( x, round( top + i * step ) ) for i in range( count ) ]

    def _blit_label(self, window, text, anchor_x, y, align):
        surface = self.font.render( text, True, LABEL_COLOR )
        if align == 'right':
            window.blit( surface, ( anchor_x - surface.get_width(), y ) )
        else:
            window.blit( surface, ( anchor_x, y ) )
