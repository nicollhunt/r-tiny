from event_bus import bus
from engine_nodes import Text2DNode
from engine_math import Vector2
from engine_resources import FontResource

import math

class HUD:
    def __init__(self):
        self._score = 0
        self._score_position = Vector2(127, 1)
        self._score_label = Text2DNode()
        self._update_label()
        bus.subscribe("enemy_destroyed", self.on_enemy_destroyed)
        
    def on_enemy_destroyed(self, evt):
        self._set_score(self._score + 10)

    def _set_score(self, score: int):
        if self._score == score:
            return
        self._score = score
        self._update_label()

    def _update_label(self):
        self._score_label.text = str(self._score)
        
    def draw(self):
        # Update position
        self._score_label.position = Vector2(
            self._score_position.x - self._score_label.width // 2,
            self._score_position.y + self._score_label.height // 2)