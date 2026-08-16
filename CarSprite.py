import math

import pygame

GRIP_NORMAL = 0.18   # fraction velocity closes the gap toward heading each frame
GRIP_DRIFT  = 0.04   # lower grip -> velocity lags further behind heading -> car slides


class CarSprite( pygame.sprite.Sprite ):
    """ Car Sprite with basic acceleration, turning, braking and reverse """

    def __init__( self, car_image, x, y, rotations=360, heading_degrees=0 ):
        """ A car Sprite which pre-rotates up to <rotations> lots of
            angled versions of the image.  Depending on the sprite's
            heading-direction, the correctly angled image is chosen.
            The base car-image should be pointing North/Up.          """
        pygame.sprite.Sprite.__init__(self)
        # Pre-make all the rotated versions
        # This assumes the start-image is pointing up-screen
        # Operation must be done in degrees (not radians)
        self.rot_img   = []
        self.min_angle = ( 360 / rotations )
        for i in range( rotations ):
            # This rotation has to match the angle in radians later
            # So offet the angle (0 degrees = "north") by 90° to be angled 0-radians (so 0 rad is "east")
            rotated_image = pygame.transform.rotozoom( car_image, 360-90-( i*self.min_angle ), 1 )
            self.rot_img.append( rotated_image )
        self.min_angle = math.radians( self.min_angle )   # don't need degrees anymore
        # movement
        self.heading   = math.radians( heading_degrees )  # 0 = east, increases clockwise
        self.speed     = 0
        self.velocity  = pygame.math.Vector2( 0, 0 )
        self.position  = pygame.math.Vector2( x, y )
        # define the image used, matching the starting heading
        image_index      = int( self.heading / self.min_angle ) % len( self.rot_img )
        self.image        = self.rot_img[ image_index ]
        self.rect         = self.image.get_rect()
        self.rect.center  = ( x, y )

    def reset( self, x, y, heading_degrees=0 ):
        """ Snap the car back to a given position/heading, e.g. after going out of bounds """
        self.heading  = math.radians( heading_degrees )
        self.speed    = 0
        self.velocity = pygame.math.Vector2( 0, 0 )
        self.position = pygame.math.Vector2( x, y )

        image_index      = int( self.heading / self.min_angle ) % len( self.rot_img )
        self.image        = self.rot_img[ image_index ]
        self.rect         = self.image.get_rect()
        self.rect.center  = ( x, y )

    def turn( self, angle_degrees ):
        """ Adjust the angle the car is heading, if this means using a 
            different car-image, select that here too """
        ### TODO: car shouldn't be able to turn while not moving
        self.heading += math.radians( angle_degrees ) 
        # Decide which is the correct image to display
        image_index = int( self.heading / self.min_angle ) % len( self.rot_img )
        # Only update the image if it's changed
        if ( self.image != self.rot_img[ image_index ] ):
            x,y = self.rect.center
            self.image = self.rot_img[ image_index ]
            self.rect  = self.image.get_rect()
            self.rect.center = (x,y)

    def accelerate( self, amount ):
        """ Increase the speed either forward or reverse """
        self.speed += amount

    def brake( self ):
        """ Slow the car by half """
        self.speed /= 2
        if ( abs( self.speed ) < 0.1 ):
            self.speed = 0

    def update(self, is_in_green=False, drifting=True):
        """ Sprite update function, calcualtes any new position """
        grip = GRIP_DRIFT if drifting else GRIP_NORMAL

        # Where the car WOULD be moving with full grip right now
        target_velocity = pygame.math.Vector2()
        target_velocity.from_polar( ( self.speed, math.degrees( self.heading ) ) )

        # Blend current velocity toward that, instead of snapping to it
        self.velocity = self.velocity.lerp( target_velocity, grip )

        effective_velocity = self.velocity // 2 if is_in_green else self.velocity
        self.position += effective_velocity
        self.rect.center = ( round(self.position[0]), round(self.position[1] ) )