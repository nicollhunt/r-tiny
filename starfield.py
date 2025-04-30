from engine_draw import Color
from engine_math import Vector2
from engine_nodes import Rectangle2DNode

import color_utils
import random

class StarPrefab:
    def __init__(self, width: int, height: int, velocity):
        self.width = width
        self.height = height
        self.velocity = velocity

class Star:
    def __init__(self):
        self.node = Rectangle2DNode()
        self.prefab = None
        
    def set_prefab(self, prefab):
        self.prefab = prefab
        self.node.width = prefab.width
        self.node.height = prefab.height    
        
    def set_position(self, position):
        self.node.position = position

class Starfield:
    def __init__(self, max_stars: int, star_prefabs, frame_skip = 1, screen_width = 128, screen_height = 128):
        self.stars = []
        self.star_prefabs = star_prefabs
        self.frame_skip = frame_skip
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.frame = 0
        
        for i in range(max_stars):
            star = Star()
            self._setup_star(star)
            self.stars.append(star)
            
    def _setup_star(self, star):
        prefab = self.get_random_prefab()
        star.set_prefab(prefab)
        position = Vector2(random.randint(0, self.screen_width - 1), random.randint(0, self.screen_height - 1))
        star.set_position(position)
    
    def get_random_prefab(self):
        ix = random.randint(0, len(self.star_prefabs) - 1)
        return self.star_prefabs[ix]
    
    def tick(self):
        self.frame += 1
        if (self.frame % self.frame_skip != 0):
            return
        
        for star in self.stars:
            node = star.node
            node.position.x = node.position.x - star.prefab.velocity * self.frame_skip;
            if (node.position.x < 0):
                position = Vector2(self.screen_width, random.randint(0, self.screen_height - 1))
                star.set_position(position)
        
            palette = color_utils.palette_bright
            if (random.randint(0, 4) > 0):
                color_ix = len(palette) - 1
            else:
                color_ix = random.randint(1, len(palette) - 1)
            node.color = Color(palette[color_ix])
