from event_bus import bus
from engine_nodes import Text2DNode, Rectangle2DNode
from engine_math import Vector2
from engine_resources import FontResource
from engine_draw import Color
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
        
        # Charge bar setup
        self._charge_level = 0
        self._charge_bar_bg = Rectangle2DNode(
            position=Vector2(64, 128),  # Bottom center of screen
            width=100,
            height=4,
            color=Color(0, 0, 0),  # Dark gray background
            opacity=1.0,
            outline=False,
            layer=10
        )
        
        self._charge_bar = Rectangle2DNode(
            position=Vector2(64, 128),  # Same position as background
            width=0,  # Will be updated based on charge
            height=4,
            color=Color(0, 255, 0),  # Green for charge
            opacity=1.0,
            outline=False,
            layer=11
        )
        
        self._update_label()
        bus.subscribe("enemy_destroyed", self.on_enemy_destroyed)
        bus.subscribe("charge_level_changed", self.on_charge_level_changed)
        
    def on_enemy_destroyed(self, evt):
        self._set_score(self._score + 10)

    def on_charge_level_changed(self, evt):
        charge_level = evt[0]
        self._charge_level = charge_level
        # Update charge bar width based on charge level
        self._charge_bar.width = 128 * charge_level
        # Update color based on charge level
        if charge_level >= 0.8:
            self._charge_bar.color = Color(255, 255, 255)  # White for max charge
        elif charge_level >= 0.4:
            self._charge_bar.color = Color(255, 255, 0)  # Yellow for medium charge
        else:
            self._charge_bar.color = Color(0, 255, 0)  # Green for low charge

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
        self._charge_level = 0
        self._charge_bar.width = 0
        
    def draw(self):
        # Update score position
        self._score_label.position = Vector2(
            self._score_position.x - self._score_label.width // 2,
            self._score_position.y + self._score_label.height // 2)
            
        # Update high score position
        self._high_score_label.position = Vector2(
            self._high_score_position.x + self._high_score_label.width // 2,
            self._high_score_position.y + self._high_score_label.height // 2)
            
        # Update charge bar position (center it horizontally)
        self._charge_bar.position.x = 64#ß - (self._charge_bar.width / 2)