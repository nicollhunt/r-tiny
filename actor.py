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
    def tick(self):
                
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

        if io.A.is_just_pressed:
            bullet_position = Vector2(self.node.position.x, self.node.position.y)
            bullet_position.x += 14
            bullet_position.y += 2
            bus.dispatch("spawn_bullet", bullet_position)
            bus.dispatch("play_rumble", 0.1, 0.05)

