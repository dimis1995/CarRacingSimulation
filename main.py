import pygame

from CarSprite import CarSprite
from Track import Track
from tracks import TRACKS

# Window size
WINDOW_WIDTH    = 1280
WINDOW_HEIGHT   = 720
WINDOW_SURFACE  = pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE

# Track
TRACK_DEF    = TRACKS["ring"]
TRACK_GRID   = TRACK_DEF["grid"]
CELL_SIZE    = TRACK_DEF["cell_size"]
GRID_ROWS    = len( TRACK_GRID )
GRID_COLS    = len( TRACK_GRID[0] )
TRACK_ORIGIN = ( ( WINDOW_WIDTH - GRID_COLS * CELL_SIZE ) // 2, ( WINDOW_HEIGHT - GRID_ROWS * CELL_SIZE ) // 2 )


### initialisation
pygame.init()
pygame.mixer.init()
window = pygame.display.set_mode( ( WINDOW_WIDTH, WINDOW_HEIGHT ), WINDOW_SURFACE )
pygame.display.set_caption("Car Steering")


### Bitmaps
car_image  = pygame.image.load( 'car_128.png' ).convert_alpha()

# Track
track = Track( TRACK_GRID, CELL_SIZE, origin=TRACK_ORIGIN,
               start_cell=TRACK_DEF["start_cell"], start_heading_degrees=TRACK_DEF["start_heading_degrees"] )

### Sprites
start = track.get_start_position()
black_car = CarSprite( car_image, start.x, start.y, heading_degrees=track.start_heading_degrees )
car_sprites = pygame.sprite.Group() #Single()
car_sprites.add( black_car )


def out_of_bounds():
    print("OUT OF BOUNDS")


### Main Loop
clock = pygame.time.Clock()
done = False
while not done:

    # Handle user-input
    for event in pygame.event.get():
        if ( event.type == pygame.QUIT ):
            done = True
        elif ( event.type == pygame.VIDEORESIZE ):
            WINDOW_WIDTH  = event.w
            WINDOW_HEIGHT = event.h
            window = pygame.display.set_mode( ( WINDOW_WIDTH, WINDOW_HEIGHT ), WINDOW_SURFACE )
        elif ( event.type == pygame.MOUSEBUTTONUP ):
            # On mouse-click
            pass
        elif ( event.type == pygame.KEYUP ):
            if ( event.key == pygame.K_UP ):  
                print( 'accelerate' )
                black_car.accelerate( 0.5 )
            elif ( event.key == pygame.K_DOWN ):  
                print( 'brake' )
                black_car.brake( )

    # Continuous Movement keys
    keys = pygame.key.get_pressed()
    if ( keys[pygame.K_LEFT] ):
        black_car.turn( -1.8 )  # degrees
    if ( keys[pygame.K_RIGHT] ):
        black_car.turn( 1.8 )

    # Collision logic
    loc = track.zone(black_car.position)
    car_is_in_green = False
    if loc == 'gray':
        pass
    elif loc == 'green':
        car_is_in_green = True
    else:
        out_of_bounds()        

    # Draw the track
    track.draw(window)

    # Update the car(s)
    car_sprites.update(car_is_in_green)

    # Update the window
    # window.blit( background, ( 0, 0 ) ) # backgorund
    car_sprites.draw( window )
    pygame.display.flip()

    # Clamp FPS
    clock.tick_busy_loop(60)

pygame.quit()
