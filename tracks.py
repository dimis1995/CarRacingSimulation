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


def _with_checkpoints( grid, checkpoints ):
    """ checkpoints: ordered list of (row, col) cells, numbered 101, 102, ... in sequence """
    for index, ( row, col ) in enumerate( checkpoints, start=1 ):
        grid[row][col] = CHECKPOINT_BASE + index
    return grid


# --- Ring: rectangular loop, one checkpoint per straight, in travel order ---
RING = {
    "grid": _with_checkpoints(
        _ring_grid( rows=16, cols=30, ring_thickness=3 ),
        checkpoints=[ (14, 5), (7, 1), (1, 15), (7, 28) ],
    ),
    "cell_size":             40,
    "start_cell":            (14, 15),   # middle of the bottom straight
    "start_heading_degrees": 180,        # facing west/left
}


# --- L-Bend: hand-authored, non-rectangular, no infield hole -- proves the grid isn't limited to loops ---
L_BEND = {
    "grid": _with_checkpoints(
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
        checkpoints=[ (5, 1), (1, 8) ],
    ),
    "cell_size":             40,
    "start_cell":            (8, 1),   # bottom of the vertical arm
    "start_heading_degrees": 270,      # facing north/up
}


TRACKS = {
    "ring":   RING,
    "l_bend": L_BEND,
}
