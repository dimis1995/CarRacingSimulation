from Track import ASPHALT, CHECKPOINT_BASE, SLOW


def _ring_grid( rows, cols, ring_thickness ):
    return [
        [
            ASPHALT if ( row < ring_thickness or row >= rows - ring_thickness or
                         col < ring_thickness or col >= cols - ring_thickness )
            else SLOW
            for col in range( cols )
        ]
        for row in range( rows )
    ]


def _with_checkpoint_gates( grid, gates ):
    """ Paint each checkpoint as a full-width line across the road (a "gate"), not a
        single cell -- so crossing it anywhere across the track's width counts, rather
        than needing to drive through one exact lane position.
        gates: ordered list of (orientation, fixed_index, span_start, span_end).
          'v': fixed_index is a column, span is a row range    -- a vertical gate across a horizontal straight
          'h': fixed_index is a row,    span is a column range -- a horizontal gate across a vertical straight """
    for index, ( orientation, fixed, span_start, span_end ) in enumerate( gates, start=1 ):
        value = CHECKPOINT_BASE + index
        for pos in range( span_start, span_end + 1 ):
            if orientation == 'v':
                grid[pos][fixed] = value
            else:
                grid[fixed][pos] = value
    return grid


# --- Ring: rectangular loop, gates spanning the full track width, in travel order ---
RING = {
    "grid": _with_checkpoint_gates(
        _ring_grid( rows=16, cols=30, ring_thickness=3 ),
        gates=[
            ( 'v', 10, 13, 15 ),   # bottom straight, first segment (heading west from start)
            ( 'v',  5, 13, 15 ),
            ( 'h', 10,  0,  2 ),   # left straight (heading north)
            ( 'h',  5,  0,  2 ),
            ( 'v', 10,  0,  2 ),   # top straight (heading east)
            ( 'v', 20,  0,  2 ),
            ( 'h',  5, 27, 29 ),   # right straight (heading south)
            ( 'h', 10, 27, 29 ),
            ( 'v', 20, 13, 15 ),   # bottom straight, second segment (heading west back to start)
        ],
    ),
    "cell_size":             40,
    "start_cell":            (14, 15),   # middle of the bottom straight
    "start_heading_degrees": 180,        # facing west/left
}


# --- L-Bend: hand-authored, non-rectangular, no infield hole -- proves the grid isn't limited to loops ---
L_BEND = {
    "grid": _with_checkpoint_gates(
        [
            [0,0,0,0,0,0,0,0,0,0,0,0],
            [0,1,1,1,1,1,1,1,1,1,1,0],
            [0,1,1,1,1,1,1,1,1,1,1,0],
            [0,1,1,0,0,0,0,0,0,0,0,0],
            [0,1,1,0,0,0,0,0,0,0,0,0],
            [0,1,1,0,0,0,0,0,0,0,0,0],
            [0,1,1,0,0,0,0,0,0,0,0,0],
            [0,1,1,0,0,0,0,0,0,0,0,0],
            [0,1,1,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0],
        ],
        gates=[
            ( 'h', 5, 1, 2 ),   # vertical arm (heading north)
            ( 'v', 8, 1, 2 ),   # horizontal arm (heading east)
        ],
    ),
    "cell_size":             40,
    "start_cell":            (8, 1),   # bottom of the vertical arm
    "start_heading_degrees": 270,      # facing north/up
}


TRACKS = {
    "ring":   RING,
    "l_bend": L_BEND,
}
