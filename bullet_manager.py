from actor import Actor
from event_bus import bus
from engine_draw import Color
from engine_nodes import Sprite2DNode
from engine_resources import TextureResource
from engine_math import Vector2

class Bullet(Actor):
    def __init__(self, texture: TextureResource, data: dict, position: Vector2 = None, speed: int = 1, charge_level: float = 0):
        super().__init__(texture, data, position, speed)
        self.charge_level = charge_level
        # Adjust speed based on charge level (faster for charged shots)
        self.speed = speed * (1 + charge_level)
        # Adjust size based on charge level (bigger for charged shots)
        self.node.scale = Vector2(1 + charge_level * 0.5, 1 + charge_level * 0.5)

class BulletManager:
    def __init__(self, bullet_texture: TextureResource, bullet_data: dict, pool_size: int = 10):
        
        self._pool = []
        self._active = []
        self._pending_destroy = set()
        for i in range(pool_size):            
            bullet = Bullet(bullet_texture, bullet_data)
            bullet.node.opacity = 0
            self._pool.append(bullet)
        
        bus.subscribe("spawn_bullet", self._on_spawn_bullet)
        
    def tick(self):
        
        for bullet in self._active:
            bullet.tick()
        
            if bullet.node.position.x > 150:
                self._pending_destroy.add(bullet)

        for bullet in self._pending_destroy:
            self.destroy_bullet(bullet)
        self._pending_destroy.clear()
                
    def get_active_bullets(self):
        return self._active
    
    def destroy_bullet(self, bullet):
        bullet.node.opacity = 0
        self._pool.append(bullet)
        self._active.remove(bullet)
        
    def _on_spawn_bullet(self, evt):
        position = evt[0]
        charge_level = evt[1] if len(evt) > 1 else 0
        
        if not self._pool:
            return
    
        bullet = self._pool.pop(0)
        self._active.append(bullet)
       
        bullet.node.opacity = 1
        bullet.charge_level = charge_level
        bullet.speed = 6  # Base speed * charge multiplier
        bullet.input = Vector2(1, 0)
        bulletNode = bullet.node
        bulletNode.opacity = 1
        bulletNode.position.x = position.x
        bulletNode.position.y = position.y
        # Scale the bullet based on charge level
        bulletNode.scale = Vector2(1 + charge_level * 0.5, 1 + charge_level * 0.5)
        
