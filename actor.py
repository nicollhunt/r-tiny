from color_utils import get_colour_from_data
from engine_draw import Color
from engine_resources import TextureResource
from engine_nodes import Sprite2DNode
from engine_math import Vector2
from event_bus import bus
import engine_audio

import engine_io as io
import json

class Actor:
    def __init__(self, texture: TextureResource, data: dict, position: Vector2 = None, speed: int = 1, on_destroy_event: str = None):

        if position is None:
            position = Vector2(0, 0)

        self._on_destroy_event = on_destroy_event
        self.speed = speed
        self.input = Vector2()
        self.frame = 0
        
        self.node = Sprite2DNode(
            position = position,
            texture = texture,
            transparent_color = get_colour_from_data(data, "transparent_color", Color(0, 0, 0)),
            frame_count_x = data.get("frame_count_x", 1),
            frame_count_y = data.get("frame_count_y", 1),
            playing = False
        )
    
    def tick(self):
        self.frame += 1

        position = self.node.position
        
        delta = Vector2(self.input.x * self.speed, self.input.y * self.speed)
        position.x += delta.x
        position.y += delta.y
        
        self.node.position = position

        self.node.frame_current_x = self.frame % self.node.frame_count_x
        
class Module(Actor):
    def __init__(self, texture: TextureResource, data: dict, position: Vector2 = Vector2(), speed: int = 2):
        super().__init__(texture, data, position, speed)
        self.attached = True
        self.reattaching = False
        self.offset = Vector2(22, 1)  # Offset from player when attached

    def attach(self):
        self.reattaching = True
        self.attached = False

    def detach(self):
        self.attached = False
        self.velocity = Vector2(5, 0)  # Speed when detached

    def tick(self, player_position=None):
        
        self.frame += 1
        self.node.frame_current_x = self.frame // 4 % self.node.frame_count_x

        drag = 0.95
        homing_accel = 0.1  # How quickly the module turns towards the player
        reattach_speed = 2.0  # Speed at which the module returns to the player

        if self.reattaching and player_position is not None:
            # Move smoothly towards the front of the player
            target_x = player_position.x + self.offset.x
            target_y = player_position.y + self.offset.y
            dx = target_x - self.node.position.x
            dy = target_y - self.node.position.y
            dist = (dx ** 2 + dy ** 2) ** 0.5
            if dist < 1.0:
                # Snap in place and finish reattaching
                self.node.position.x = target_x
                self.node.position.y = target_y
                self.reattaching = False
                self.attached = True
            else:
                # Move towards the target at a fixed speed
                self.node.position.x += (dx / dist) * min(reattach_speed, dist)
                self.node.position.y += (dy / dist) * min(reattach_speed, dist)
        elif self.attached and player_position is not None:
            # Follow the player with offset
            self.node.position.x = player_position.x + self.offset.x
            self.node.position.y = player_position.y + self.offset.y
        elif not self.attached:
            # Home towards the player if position is provided
            if player_position is not None:
                dx = player_position.x - self.node.position.x
                dy = player_position.y - self.node.position.y

                dist = (dx ** 2 + dy ** 2) ** 0.5

                if dist > 1e-3:
                    # Normalize and apply homing acceleration
                    if abs(dx) > 70:
                        self.velocity.x += (dx / dist) * homing_accel
                        
                    self.velocity.y += (dy / dist) * homing_accel

            # Move forward when detached
            self.node.position.x += self.velocity.x
            self.node.position.y += self.velocity.y

            self.velocity.x = self.velocity.x * drag
            self.velocity.y = self.velocity.y * drag

class Player(Actor):
    def __init__(self, texture: TextureResource, data: dict, charge_shot_texture: TextureResource, charge_shot_data: dict, position: Vector2 = Vector2(), speed: int = 1, on_destroy_event: str = None, module=None):
        super().__init__(texture, data, position, speed, on_destroy_event)
        self.is_exploding = False
        self.explosion_timer = 0
        self.explosion_duration = 22  # Same as enemy explosion duration
        self.module = module  # Reference to the module
        
        # Store charge shot properties
        self.charge_shot_texture = charge_shot_texture
        self.charge_shot_data = charge_shot_data
        
        # Charge shot properties
        self.charge_time = 0
        self.max_charge_time = 60  # 2 seconds at 30fps
        self.is_charging = False
        self.charge_node = None

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

        # Handle charging and shooting
        if io.A.is_pressed and not self.is_exploding:
            if not self.is_charging:
                self.is_charging = True
                self.charge_time = 0
                # Create charge node if it doesn't exist
                if self.charge_node is None:
                    self.charge_node = Sprite2DNode(
                        position=Vector2(self.node.position.x, self.node.position.y),
                        texture=self.charge_shot_texture,
                        transparent_color=Color(255, 0, 255),
                        frame_count_x=self.charge_shot_data.get("frame_count_x", 1),
                        frame_count_y=self.charge_shot_data.get("frame_count_y", 1),
                        fps = 10.0,
                        playing=True,
                        layer=5
                    )
            
            self.charge_time = min(self.charge_time + 1, self.max_charge_time)
            
            # Update charge animation and dispatch charge level
            if self.charge_node:
                charge_level = self.charge_time / self.max_charge_time
                bus.dispatch("charge_level_changed", charge_level)
                
                # Position the charge sprite in front of the player or module
                charge_position = Vector2(self.node.position.x, self.node.position.y)
                if self.module and self.module.attached:
                    charge_position.x += self.module.offset.x
                
                charge_position.x += 14  # Offset to be in front
                charge_position.y += 2   # Center vertically
                
                self.charge_node.position = charge_position
                self.charge_node.opacity = 1

        elif self.is_charging:
            self.is_charging = False
            # Reset charge bar when releasing
            bus.dispatch("charge_level_changed", 0)
            
            # Fire based on charge level
            bullet_position = Vector2(self.node.position.x, self.node.position.y)
            
            if self.module and self.module.attached:
                bullet_position.x += self.module.offset.x

            bullet_position.x += 14
            bullet_position.y += 2
            
            # Calculate charge level (0-1)
            charge_level = self.charge_time / self.max_charge_time
            
            # Always fire from the player
            bus.dispatch("spawn_bullet", bullet_position, charge_level)
            bus.dispatch("play_rumble", 0.1 + charge_level * 0.2, 0.05)
            bus.dispatch("play_laser", None)

            # If module is detached, fire a bullet from the module as well
            if self.module and not self.module.attached and charge_level > 0.5:
                module_bullet_position = Vector2(self.module.node.position.x, self.module.node.position.y)
                module_bullet_position.x += 14
                module_bullet_position.y += 2
                bus.dispatch("spawn_bullet", module_bullet_position, 0)

            # Hide charge node
            if self.charge_node:
                self.charge_node.opacity = 0

        # Attach/detach module with B button
        if self.module:
            if io.B.is_just_pressed:
                if self.module.attached:
                    self.module.detach()
                else:
                    self.module.attach()

            # Always tick the module, always pass player position
            if self.module:
                self.module.tick(self.node.position)

    def start_explosion(self):
        self.is_exploding = True
        self.explosion_timer = self.explosion_duration
        self.node.opacity = 0  # Hide player during explosion
        if self.charge_node:
            self.charge_node.opacity = 0  # Hide charge animation during explosion
        bus.dispatch("charge_level_changed", 0)  # Reset charge bar on explosion
