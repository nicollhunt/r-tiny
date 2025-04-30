from color_utils import get_colour_from_data
from engine_draw import Color
from engine_resources import TextureResource
from engine_nodes import Sprite2DNode
from engine_math import Vector2
from event_bus import bus

import engine_io as io
import json

class Actor:
    def __init__(self, texture: TextureResource, data: dict, position: Vector2 = Vector2(), speed: int = 1, on_destroy_event: str = None):
        self._on_destroy_event = on_destroy_event
        self.speed = speed
        self.input = Vector2()
        
        self.node = Sprite2DNode(
            position = Vector2(position.x, position.y),
            texture = texture,
            transparent_color = get_colour_from_data(data, "transparent_color", Color(0, 0, 0)),
            frame_count_x = data.get("frame_count_x", 1),
            frame_count_y = data.get("frame_count_y", 1),
        )
    
    def tick(self):
        position = self.node.position
        
        delta = Vector2(self.input.x * self.speed, self.input.y * self.speed)
        position.x += delta.x
        position.y += delta.y
        
        self.node.position = position
        
class Player(Actor):
    def __init__(self, texture: TextureResource, data: dict, position: Vector2 = Vector2(), speed: int = 1, on_destroy_event: str = None):
        super().__init__(texture, data, position, speed, on_destroy_event)
        self.is_exploding = False
        self.explosion_timer = 0
        self.explosion_duration = 22  # Same as enemy explosion duration
    
    def tick(self):
        if self.is_exploding:
            self.explosion_timer -= 1
            if self.explosion_timer <= 0:
                self.is_exploding = False
                bus.dispatch("player_explosion_finished")
            return
                
        self.input = Vector2()

        if io.UP.is_pressed:
            self.input.y -= 1
        if io.DOWN.is_pressed:
            self.input.y += 1
        if io.LEFT.is_pressed:
            self.input.x -= 1
        if io.RIGHT.is_pressed:
            self.input.x += 1

        super().tick()

        # Clamp position to screen boundaries
        half_width = self.node.texture.width / (self.node.frame_count_x * 2)
        half_height = self.node.texture.height / (self.node.frame_count_y * 2)
        
        # Screen boundaries (using the same screen dimensions as main.py)
        screen_width = 128
        screen_height = 128
        
        self.node.position.x = max(half_width, min(screen_width - half_width, self.node.position.x))
        self.node.position.y = max(half_height, min(screen_height - half_height, self.node.position.y))

        if io.A.is_just_pressed and not self.is_exploding:
            bullet_position = Vector2(self.node.position.x, self.node.position.y)
            bullet_position.x += 14
            bullet_position.y += 2
            bus.dispatch("spawn_bullet", bullet_position)
            bus.dispatch("play_rumble", 0.1, 0.05)
            
    def start_explosion(self):
        self.is_exploding = True
        self.explosion_timer = self.explosion_duration
        self.node.opacity = 0  # Hide player during explosion

