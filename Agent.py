import math

import pygame

RAY_COUNT = 8
MAX_SPEED = 15.0   # used only to scale the speed feature into roughly the same range as the ray features

RAY_COLOR      = (255, 255, 0)
GREEN_COLOR    = (0, 255, 0)
WALL_HIT_COLOR = (220, 40, 40)


class Agent:
    """ Wraps a car + track pair and exposes the sensory state an RL agent would see:
        RAY_COUNT heading-relative rays (wall distance + green-start distance each),
        whether the car is currently in green, and its speed. """

    def __init__(self, car, track, max_range, debug=False, print_interval=15):
        self.car            = car
        self.track          = track
        self.max_range      = max_range
        self.debug          = debug
        self.print_interval = print_interval
        self._frame         = 0
        self.ray_hits       = []   # [(angle_degrees, wall_distance, green_distance), ...]

    def sense(self):
        heading_degrees = math.degrees( self.car.heading )
        self.ray_hits = []
        for i in range( RAY_COUNT ):
            angle = heading_degrees + i * ( 360 / RAY_COUNT )
            wall_distance, green_distance = self.track.cast_ray( self.car.position, angle, self.max_range )
            self.ray_hits.append( ( angle, wall_distance, green_distance ) )

        in_green = self.track.zone( self.car.position ) == 'green'

        state = []
        for _, wall_distance, green_distance in self.ray_hits:
            state.append( wall_distance / self.max_range )
            state.append( green_distance / self.max_range )
        state.append( 1.0 if in_green else 0.0 )
        state.append( self.car.speed / MAX_SPEED )

        if self.debug:
            self._frame += 1
            if self._frame % self.print_interval == 0:
                rays_str = ", ".join( f"({w:.0f},{g:.0f})" for _, w, g in self.ray_hits )
                print( f"speed={self.car.speed:.2f}  in_green={in_green}  rays(wall,green)=[{rays_str}]" )

        return state

    def draw_debug(self, window):
        if not self.debug:
            return
        origin = self.car.position
        for angle, wall_distance, green_distance in self.ray_hits:
            direction = pygame.Vector2()
            direction.from_polar( ( 1, angle ) )
            end_point = origin + direction * wall_distance
            pygame.draw.line( window, RAY_COLOR, origin, end_point, 1 )
            if wall_distance < self.max_range:
                pygame.draw.circle( window, WALL_HIT_COLOR, ( round( end_point.x ), round( end_point.y ) ), 3 )
            if green_distance < self.max_range:
                green_point = origin + direction * green_distance
                pygame.draw.circle( window, GREEN_COLOR, ( round( green_point.x ), round( green_point.y ) ), 3 )
