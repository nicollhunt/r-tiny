import sys

root_path = '/Games/R-Tiny'

# Append root to sys.path so we can import relative modules
sys.path.append(root_path)

import engine_main
import engine

from event_bus import bus
from starfield import StarPrefab, Starfield
from actor import Actor, Player
from bullet_manager import BulletManager
from hud import HUD
from rumble_controller import RumbleController

from engine_draw import Color
import engine_io as io
from engine_resources import TextureResource as txtr
from engine_math import Vector2, Vector3
from engine_nodes import CameraNode, Sprite2DNode, Text2DNode, Rectangle2DNode

import json
import random

shipTxtr = txtr(f"{root_path}/ship.bmp")

def load_json_data(filename: str) -> dict:
    try:
        with open(f"{root_path}/ship.bmp.json", 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error: {e}")
        return None
        
shipData = load_json_data(f"{root_path}/ship.bmp.json")

enemyTxtr = txtr(f"{root_path}/enemy.bmp")

bullet_filename = f"{root_path}/projectile.bmp"
bullet_texture = txtr(bullet_filename)
bullet_data = load_json_data(f"{bullet_filename}.json")

explodeTxtr = txtr(f"{root_path}/explode.bmp")

#
# Main Player Ship
#
player = Player(shipTxtr, shipData, position = Vector2(26, 28), speed = 2)

bullet_manager = BulletManager(bullet_texture, bullet_data)

screen_width = 128
screen_height = 128

enemySpeed = 1.25

explodePool = []
activeExplodes = []
for i in range(10):
    explode = {
        "node": Sprite2DNode(position = Vector2(64, 64),
                 texture = explodeTxtr,
                 transparent_color = Color(255, 0, 255),
                 opacity = 0,
                 frame_count_x = 4,
                 frame_count_y = 2,
                 fps = 10,
                 playing = True,
                 layer = 6)
    }
    explodePool.append(explode)
    
def spawnExplode(position):
    if len(explodePool) == 0:
        return
    
    explode = explodePool.pop(0)
    activeExplodes.append(explode)
   
    node = explode["node"]
    node.opacity = 1
    node.frame_current_x = 0
    node.position.x = position.x
    node.position.y = position.y
    
    explode["timer"] = 22
    return

def despawnExplode(explode):
    explode["node"].opacity = 0
    activeExplodes.remove(explode)
    explodePool.append(explode)

#
# Starfield initialisation
#
num_stars = 20

starfield_prefabs = [
    StarPrefab(1, 1, 1),
    StarPrefab(1, 2, 1.5),
    StarPrefab(2, 2, 2),
]

starfield = Starfield(num_stars, starfield_prefabs, frame_skip = 2)

rumble_controller = RumbleController()

cam = CameraNode(position = Vector3(64, 64, 0))


enemyPool = []
activeEnemies = []
for i in range(5):
    enemy = {
        "node": Sprite2DNode(position = Vector2(83, 64),
                 texture = enemyTxtr,
                 transparent_color = Color(255, 0, 255),
                 opacity = 0,
                 frame_count_x = 3,
                 playing = False,
                 layer = 6)
    }
    enemyPool.append(enemy)
    
def spawnEnemy(position):
    if len(enemyPool) == 0:
        return
    
    item = enemyPool.pop(0)
    activeEnemies.append(item)
   
    node = item["node"]
    node.opacity = 1
    node.position.x = position.x
    node.position.y = position.y
    return

def despawnEnemy(item):
    pool = enemyPool
    active = activeEnemies
    item["node"].opacity = 0
    active.remove(item)
    pool.append(item)


frame = 0
engine.fps_limit(30)

paused = False

def spawnRandomEnemy():
    spawnEnemy(Vector2(screen_width + 26, random.randint(5, screen_height -5)))


def checkCollision(node1, node2):
    
    xMin1 = node1.position.x - node1.texture.width / (node1.frame_count_x * 2)
    xMin2 = node2.position.x - node2.texture.width / (node2.frame_count_x * 2)
    xMax1 = node1.position.x + node1.texture.width / (node1.frame_count_x * 2)
    xMax2 = node2.position.x + node2.texture.width / (node2.frame_count_x * 2)
    
    if xMax1 < xMin2 or xMin1 > xMax2:
        return False

    yMin1 = node1.position.y - node1.texture.height / (node1.frame_count_y * 2)
    yMin2 = node2.position.y - node2.texture.height / (node2.frame_count_y * 2)
    yMax1 = node1.position.y + node1.texture.height / (node1.frame_count_y * 2)
    yMax2 = node2.position.y + node2.texture.height / (node2.frame_count_y * 2)

    if yMax1 < yMin2 or yMin1 > yMax2:
        return False

    return True

def checkEnemyCollision(bulletNode):
    enemiesToDespawn = []
    for enemy in activeEnemies:
        enemyNode = enemy["node"]
                
        if checkCollision(enemyNode, bulletNode):
            spawnExplode(enemyNode.position)
            enemiesToDespawn.append(enemy)
            
    for enemy in enemiesToDespawn:
        bus.dispatch("enemy_destroyed", enemy)
        despawnEnemy(enemy)
        spawnRandomEnemy()
        
    return len(enemiesToDespawn) > 0
        

spawnRandomEnemy()

hud = HUD()

while True:
        
    if not engine.tick():
        continue

    if io.LB.is_pressed and io.RB.is_pressed and io.MENU.is_pressed:
        engine.reset(True)

    if io.MENU.is_just_pressed:
        paused = not paused
        
    if paused:
        continue

    frame = frame + 1
    
    for explode in activeExplodes:
        explode["timer"] = explode["timer"] - 1
        if explode["timer"] == 0:
            despawnExplode(explode)

    for enemy in activeEnemies:
        node = enemy["node"]
        
        node.position.x -= enemySpeed
        
        if (node.position.x <= 0):
            despawnEnemy(enemy)
            spawnRandomEnemy()
    
        enemyFrame = (int)(frame / 2) % 5
        if (enemyFrame > 2):
            enemyFrame = 4 - enemyFrame
        node.frame_current_x = enemyFrame

    bullet_manager.tick()

    for bullet in bullet_manager.get_active_bullets():
        bulletNode = bullet.node
        
        if checkEnemyCollision(bulletNode):
            bullet_manager.destroy_bullet(bullet)
            bus.dispatch("play_rumble", 0.15, 0.05)

    starfield.tick()
    player.tick()

    hud.draw()
    
    # Rumble keps cutting out - disabling for now
    #rumble_controller.tick()
    