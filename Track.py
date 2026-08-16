import pygame

# Cell value codes
WALL             = 0
ASPHALT          = 1
SLOW             = 2
CHECKPOINT_BASE  = 100   # checkpoint N is encoded as CHECKPOINT_BASE + N (101, 102, ...)

COLORS = {
    ASPHALT: (60, 60, 65),    # asphalt gray
    SLOW:    (50, 140, 60),   # green infield
}
CHECKPOINT_COLOR = (230, 200, 40)   # gold, distinct from track/infield


class Track:

    def __init__(self, grid, cell_size, origin=(0, 0), start_cell=None, start_heading_degrees=0):
        """ grid: list of lists of ints (rows of cell values), e.g. WALL/ASPHALT/SLOW/checkpoint codes.
            origin: world-space position of the grid's top-left corner. """
        self.grid       = grid
        self.cell_size  = cell_size
        self.origin     = pygame.Vector2( origin )
        self.rows       = len( grid )
        self.cols       = len( grid[0] )
        self.image      = self._render()

        self.start_cell            = start_cell if start_cell is not None else self._find_first( ASPHALT )
        self.start_heading_degrees = start_heading_degrees

    def _find_first(self, value):
        for row in range( self.rows ):
            for col in range( self.cols ):
                if self.grid[row][col] == value:
                    return ( row, col )
        raise ValueError( f"No cell with value {value} found in grid" )

    def _render(self):
        surface = pygame.Surface( ( self.cols * self.cell_size, self.rows * self.cell_size ) )
        for row in range( self.rows ):
            for col in range( self.cols ):
                value = self.grid[row][col]
                color = COLORS.get( value, CHECKPOINT_COLOR if value >= CHECKPOINT_BASE else None )
                if color is not None:
                    rect = pygame.Rect( col * self.cell_size, row * self.cell_size, self.cell_size, self.cell_size )
                    pygame.draw.rect( surface, color, rect )
        return surface

    def draw(self, window):
        window.blit( self.image, self.origin )

    def cell_at(self, point):
        """ World position -> (row, col) grid indices """
        local = pygame.Vector2( point ) - self.origin
        return int( local.y // self.cell_size ), int( local.x // self.cell_size )

    def value_at(self, point):
        """ Raw cell value at a world position -- needed for checkpoint numbers """
        row, col = self.cell_at( point )
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.grid[row][col]
        return WALL   # off the edge of the grid counts as a wall

    def zone(self, point):
        """ Convenience wrapper for the common gray/green/wall cases """
        value = self.value_at( point )
        if value == WALL:
            return "outside"
        elif value == SLOW:
            return "green"
        else:
            return "gray"   # covers ASPHALT and any checkpoint value

    def get_start_position(self):
        row, col = self.start_cell
        x = self.origin.x + ( col + 0.5 ) * self.cell_size
        y = self.origin.y + ( row + 0.5 ) * self.cell_size
        return pygame.Vector2( x, y )

    def cast_ray(self, origin, angle_degrees, max_range, step=5):
        """ March outward from `origin` at `angle_degrees` (world-space, 0=east),
            returning (distance to first WALL cell, distance to first SLOW cell) --
            both capped at max_range if nothing is hit. Marching continues through
            SLOW cells (they aren't walls), only stopping at WALL or max_range. """
        direction = pygame.Vector2()
        direction.from_polar( ( 1, angle_degrees ) )
        origin = pygame.Vector2( origin )

        green_distance = max_range
        found_green    = False

        distance = step
        while distance <= max_range:
            value = self.value_at( origin + direction * distance )
            if value == WALL:
                return distance, green_distance
            if value == SLOW and not found_green:
                green_distance = distance
                found_green    = True
            distance += step

        return max_range, green_distance
