import socket
import time
import math
import random
from threading import Thread

from classes import *

# Listener constants
UDP_IP = "0.0.0.0"
UDP_PORT = 13377

SERVER_LEVEL = 1 # Current server version

# Game settings
SHOOT_HITRAD = 75
SHOOT_CD = .3
SHOOT_OFFSET = 125
SHOOT_VEL = 100
SHOOT_VELMOD = 10
SHOOT_LS = 13
SHOOT_DMG = 20
SPAWN_RADIUS = 3000
PLAYER_TIMEOUT = 12

players = []
projectiles = []

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet, UDP
sock.bind((UDP_IP, UDP_PORT))

def getPlayerBytes():
  global players
  out = b"\x00"
  for p in players:
    if p != None:
      out += p.getBytes()
  return out

def getProjectileBytes():
  out = b"\x01"
  for p in projectiles:
    if p != None:
      out += p.getBytes()
  return out

def addPlayer(ip):
  for i in range(0, 255):
    if (i >= len(players)):
      players.append(None)
    if players[i] == None:
      players[i] = Player(ip, i, 0, 0, 0, time.time())
      return players[i], i
  return None


def startmessaging():
  global players
  global projectiles
  while True:
    try:
      data, addr = sock.recvfrom(1024) # buffer size 1024 bytes
      # print(f"received message: {data.decode('UTF-8')}, from {addr}")
      if len(data) == 0:
        print("Empty.")
        continue

      if data[0] == 2: # Player moved
        # print(f"Player moved with message {data}")
        pid = data[1]
        posX = int.from_bytes(data[2:4], "little", signed=True)
        posY = int.from_bytes(data[4:6], "little", signed=True)
        rot = int.from_bytes(data[6:8], "little", signed=True)
        sht = data[8]

        if players[pid] == None:
          # players[pid] = Player(addr[0], pid, posX, posY, 100, time.time())
          pass
        else:
          players[pid].setLastUpdate(time.time())
          players[pid].setPosX(posX)
          players[pid].setPosY(posY)
          players[pid].setRotation(rot)
          players[pid].setShooting(sht != 0)
        
        # print(getPlayerBytes())
        sock.sendto(getPlayerBytes(), addr)
        sock.sendto(getProjectileBytes(), addr)

      elif data[0] == 3: # Player tries to join
        ver = int.from_bytes(data[1:len(data)], "little")
        if (ver == SERVER_LEVEL):
          print(f"New player at {addr}")
          # sock.sendto(getPlayerBytes(), addr)
          p, pid = addPlayer(addr[0])
          # print(pid)
          sock.sendto(b"\x04" + int(pid).to_bytes(1, "little"), addr)
        else:
          print(f"Version conflict with {addr} (server: {SERVER_LEVEL}, client: {ver})")
          sock.sendto(b"\x06", addr)

      elif data[0] == 4: # Player ID, this time from dead player
        # print(f"Dead player pinged with message {data}")
        pid = data[1]
        if players[pid] != None:
          players[pid].setLastUpdate(time.time())
        sock.sendto(getPlayerBytes(), addr)
        sock.sendto(getProjectileBytes(), addr)

      elif data[0] == 5: # Player respawn
        print(f"Player respawned with message {data}")
        pid = data[1]
        if (players[pid] != None and players[pid].getHp() <= 0):
          players[pid].setPosX(random.randint(-500, 500))
          players[pid].setPosY(random.randint(-500, 500))
          players[pid].setHp(100)
          players[pid].setLastUpdate(time.time())
      else:
        print(f"Interpreting \"{data.decode('UTF-8')}\" as empty.")
    except Exception as e:
      print(f"Error: {e}")


def startlogic():
  global players
  global projectiles
  lastTick = time.time()
  while True:
    now = time.time()
    deltaTime = now - lastTick
    lastTick = now

    for p in projectiles: # Update existing projectiles
      if p.getLifespan() <= 0:
        projectiles.remove(p)
        del p
        continue

      p.updatePos(deltaTime * SHOOT_VELMOD)
      p.reduceLifespan(10 * deltaTime)

      # PLAYER HIT LOGIC! (oh boy, here comes the O(n^2) if I'm bad)
      for plr in players:
        if plr and plr.getId() != p.getOwner() and plr.getHp() > 0 and (plr.getId() not in p.getHitTargets()) and math.sqrt((plr.getPosX() - p.getPosX())**2 + (plr.getPosY() - p.getPosY())**2) <= SHOOT_HITRAD:
          p.addHitTarget(plr.getId())
          plr.addHp(-SHOOT_DMG)
    # PLAYER SHOOT LOGIC! (should be easy?)
    for pid in range(len(players)):
      plr = players[pid]
      if plr:
        # print(plr.getShooting())
        # print(plr, plr.getShooting())
        time.sleep(0.001) # Sleep to prevent CPU with python GIL black magic schenanigans
        if plr.getShooting() and (now - plr.getLastShot() >= SHOOT_CD):
          xmod = math.cos(math.radians(plr.getRotation()))
          ymod = math.sin(math.radians(plr.getRotation()))
          newId = 0
          for i in range(255):
            isNew = True
            for p in projectiles:
              if p.getId() == i:
                isNew = False
                break
            if isNew:
              newId = i
              break
          projectiles.append(Projectile(plr.getId(), newId, plr.getPosX() + SHOOT_OFFSET * xmod, plr.getPosY() + SHOOT_OFFSET * ymod, SHOOT_VEL * xmod, SHOOT_VEL * ymod, SHOOT_LS))
          # print(f"Projectile spawned with id {newId}.")
          plr.setLastShot(now)

        if (now - plr.getLastUpdate() > PLAYER_TIMEOUT):
          print(f"Player {plr.getId()} ({plr.getIp()}) timed out.")
          players[pid] = None

if __name__ == "__main__": # parallel Python stuff yey!

  msg = Thread(target=startmessaging)
  lgc = Thread(target=startlogic)
  msg.start()
  lgc.start()
  msg.join()
  lgc.join()
