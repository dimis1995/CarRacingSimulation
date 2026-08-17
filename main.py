import pygame

from Agent import RAY_COUNT, Agent
from CarSprite import CarSprite
from HUD import HUD
from NetworkView import NetworkView
from QLearner import QLearner
from Track import CHECKPOINT_BASE, Track
from tracks import TRACKS

# Window size -- WINDOW_WIDTH/HEIGHT describe the track viewing area only.
# The actual pygame window is bigger: HUD_HEIGHT is reserved as its own strip
# above the track, and NETWORK_PANEL_WIDTH as its own strip to the right,
# so neither ever overlaps or shrinks the track itself.
WINDOW_WIDTH    = 1280
WINDOW_HEIGHT   = 720
WINDOW_SURFACE  = pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE

HUD_HEIGHT          = 190
NETWORK_PANEL_WIDTH = 320
SCREEN_WIDTH        = WINDOW_WIDTH + NETWORK_PANEL_WIDTH
SCREEN_HEIGHT       = WINDOW_HEIGHT + HUD_HEIGHT

DEBUG    = True
TRAINING = True   # False switches back to keyboard control (K_UP/K_DOWN/K_LEFT/K_RIGHT)
SAVE_PATH = "weights.json"

# Controls (all work regardless of TRAINING):
#   S  save weights      L  load weights      D  toggle ray debug view
#   R  restart episode    T  switch track

# Reward shaping
TIME_COST_REWARD     = -1
CHECKPOINT_REWARD     = 50
OUT_OF_BOUNDS_REWARD  = -100

# Action tuning
ACCEL_AMOUNT  = 0.3
TURN_DEGREES  = 3

TRACK_NAMES = list( TRACKS.keys() )


def _build_track(track_def):
    """ Build a Track (+ its checkpoint count) from a tracks.py definition,
        centered within the fixed track-viewing area regardless of its grid size. """
    grid      = track_def["grid"]
    cell_size = track_def["cell_size"]
    rows      = len( grid )
    cols      = len( grid[0] )
    origin    = ( ( WINDOW_WIDTH - cols * cell_size ) // 2,
                  HUD_HEIGHT + ( WINDOW_HEIGHT - rows * cell_size ) // 2 )
    new_track = Track( grid, cell_size, origin=origin,
                        start_cell=track_def["start_cell"], start_heading_degrees=track_def["start_heading_degrees"] )
    num_checkpoints = len( { cell for row in grid for cell in row if cell >= CHECKPOINT_BASE } )
    return new_track, num_checkpoints


### initialisation
pygame.init()
pygame.mixer.init()
window = pygame.display.set_mode( ( SCREEN_WIDTH, SCREEN_HEIGHT ), WINDOW_SURFACE )
pygame.display.set_caption("Car Steering")


### Bitmaps
car_image  = pygame.image.load( 'car_128.png' ).convert_alpha()

# Track
current_track_index    = 0
track, NUM_CHECKPOINTS = _build_track( TRACKS[TRACK_NAMES[current_track_index]] )

### Sprites
start = track.get_start_position()
black_car = CarSprite( car_image, start.x, start.y, heading_degrees=track.start_heading_degrees )
car_sprites = pygame.sprite.Group() #Single()
car_sprites.add( black_car )

# Agent
SENSOR_MAX_RANGE = min( WINDOW_WIDTH, WINDOW_HEIGHT ) // 4
agent = Agent( black_car, track, SENSOR_MAX_RANGE, debug=DEBUG )

# Learner
NUM_FEATURES = RAY_COUNT * 2 + 2   # (wall,green) per ray, + in_green flag + speed
learner = QLearner( NUM_FEATURES )

# HUD -- its own reserved strip at the top, never overlapping the track below it
hud = HUD( ( 0, 0, WINDOW_WIDTH, HUD_HEIGHT ) )

# Network diagram -- its own reserved strip on the right, full window height
network_view = NetworkView( ( WINDOW_WIDTH, 0, NETWORK_PANEL_WIDTH, SCREEN_HEIGHT ) )

CHECKPOINT_SCAN_STEPS = 8   # sub-samples along each frame's movement, so a fast-moving car can't skip past a checkpoint cell
STALL_TIMEOUT_FRAMES  = 60 * 60   # 1 minute at the fixed 60fps tick rate, with no checkpoint progress

next_checkpoint_index = 1
episode_count         = 1
episode_score         = 0.0
best_score            = 0.0
frames_since_progress = 0


def apply_action(action):
    if action == "accelerate":
        black_car.accelerate( ACCEL_AMOUNT )
    elif action == "slow_down":
        black_car.brake()
    elif action == "turn_left":
        black_car.turn( -TURN_DEGREES )
    elif action == "turn_right":
        black_car.turn( TURN_DEGREES )


def reset_car():
    restart = track.get_start_position()
    black_car.reset( restart.x, restart.y, track.start_heading_degrees )


def load_track(index):
    global track, NUM_CHECKPOINTS, current_track_index, next_checkpoint_index, frames_since_progress, episode_score
    current_track_index = index % len( TRACK_NAMES )
    track, NUM_CHECKPOINTS = _build_track( TRACKS[TRACK_NAMES[current_track_index]] )
    agent.track = track
    reset_car()
    next_checkpoint_index = 1
    frames_since_progress = 0
    episode_score          = 0.0
    print( f"Switched to track '{TRACK_NAMES[current_track_index]}'" )


manual_restart_requested = False


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
            if ( event.key == pygame.K_s ):
                learner.save( SAVE_PATH )
                print( f"Saved weights to {SAVE_PATH}" )
            elif ( event.key == pygame.K_l ):
                learner.load( SAVE_PATH )
            elif ( event.key == pygame.K_d ):
                agent.debug = not agent.debug
                print( f"Debug view: {'on' if agent.debug else 'off'}" )
            elif ( event.key == pygame.K_r ):
                manual_restart_requested = True
            elif ( event.key == pygame.K_t ):
                load_track( current_track_index + 1 )
            elif not TRAINING:
                if ( event.key == pygame.K_UP ):
                    black_car.accelerate( 0.5 )
                elif ( event.key == pygame.K_DOWN ):
                    black_car.brake( )

    if not TRAINING:
        # Continuous Movement keys
        keys = pygame.key.get_pressed()
        if ( keys[pygame.K_LEFT] ):
            black_car.turn( -1.8 )  # degrees
        if ( keys[pygame.K_RIGHT] ):
            black_car.turn( 1.8 )

    # Sense the world from the car's current (pre-move) position, and pick an action from it
    state = agent.sense()
    car_is_in_green = track.zone( black_car.position ) == 'green'

    action = None
    if TRAINING:
        action = learner.choose_action( state )
        apply_action( action )

    # Move the car
    old_position = pygame.math.Vector2( black_car.position )
    car_sprites.update(car_is_in_green)

    # Work out what happened as a result of this step
    zone          = track.zone( black_car.position )
    episode_done  = False
    end_reason    = None
    reward        = TIME_COST_REWARD
    if zone == 'outside':
        reward       = OUT_OF_BOUNDS_REWARD
        episode_done = True
        end_reason   = "out of bounds"
    else:
        # Scan the path just traveled, not just the final pixel -- a fast-moving car can
        # otherwise step clean over a single checkpoint cell without ever landing on it.
        target_value = CHECKPOINT_BASE + next_checkpoint_index
        for step in range( 1, CHECKPOINT_SCAN_STEPS + 1 ):
            sample = old_position.lerp( black_car.position, step / CHECKPOINT_SCAN_STEPS )
            if track.value_at( sample ) == target_value:
                reward += CHECKPOINT_REWARD
                episode_score += CHECKPOINT_REWARD
                next_checkpoint_index = next_checkpoint_index % NUM_CHECKPOINTS + 1
                frames_since_progress = 0
                break

    frames_since_progress += 1
    if not episode_done and frames_since_progress >= STALL_TIMEOUT_FRAMES:
        reward       = OUT_OF_BOUNDS_REWARD
        episode_done = True
        end_reason   = "stalled (no checkpoint for 60s)"

    if not episode_done and manual_restart_requested:
        reward       = 0   # not a real failure -- just an interruption, so no penalty
        episode_done = True
        end_reason   = "manual restart"
    manual_restart_requested = False

    if episode_done:
        best_score = max( best_score, episode_score )
        episode_count += 1
        reset_car()
        next_checkpoint_index  = 1
        frames_since_progress  = 0
        if TRAINING:
            learner.decay_epsilon()   # once per EPISODE, not per frame -- see QLearner's epsilon_decay
            print( f"Episode {episode_count} ended [{end_reason}]  epsilon={learner.epsilon:.3f}  "
                   f"score={episode_score:.1f}  best={best_score:.1f}" )
        episode_score = 0.0

    # Sense the resulting state and learn from the transition
    next_state = agent.sense()
    if TRAINING:
        learner.update( state, action, reward, next_state, episode_done )

    # Redraw the whole frame -- fill first so nothing from last frame lingers
    # outside the track's own bounds (rays, old sprite positions, etc.)
    window.fill( (0, 0, 0) )
    track.draw(window)
    car_sprites.draw( window )
    agent.draw_debug(window)
    if TRAINING:
        hud.draw( window, episode_count, learner, action, episode_score, best_score )
        network_view.draw( window, learner )
    pygame.display.flip()

    # Clamp FPS
    clock.tick_busy_loop(60)

pygame.quit()
