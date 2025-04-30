from event_bus import bus
from engine_nodes import Text2DNode
from engine_math import Vector2
from engine_resources import FontResource
import engine_save

import math

class HUD:
    def __init__(self):
        self._score = 0
        self._score_position = Vector2(127, 1)
        self._score_label = Text2DNode()
        
        # High score setup
        self._high_score = engine_save.load("high_score", 0)
        self._high_score_position = Vector2(1, 1)
        self._high_score_label = Text2DNode()
        self._update_high_score_label()
        
        self._update_label()
        bus.subscribe("enemy_destroyed", self.on_enemy_destroyed)
        
    def on_enemy_destroyed(self, evt):
        self._set_score(self._score + 10)

    def _set_score(self, score: int):
        if self._score == score:
            return
        self._score = score
        self._update_label()
        
        # Update high score if needed
        if score > self._high_score:
            self._high_score = score
            self._update_high_score_label()
            engine_save.save("high_score", self._high_score)

    def _update_label(self):
        self._score_label.text = str(self._score)
        
    def _update_high_score_label(self):
        self._high_score_label.text = f"HI: {self._high_score}"
        
    def reset(self):
        """Reset the HUD to its initial state"""
        self._set_score(0)
        
    def draw(self):
        # Update score position
        self._score_label.position = Vector2(
            self._score_position.x - self._score_label.width // 2,
            self._score_position.y + self._score_label.height // 2)
            
        # Update high score position
        self._high_score_label.position = Vector2(
            self._high_score_position.x + self._high_score_label.width // 2,
            self._high_score_position.y + self._high_score_label.height // 2)