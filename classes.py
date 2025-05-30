class Player:
  def __init__(self, ip, pid, posX, posY, hp, update):
    self._ip = ip # Server only; may remove
    self._id = pid
    self._posX = posX
    self._posY = posY
    self._rot = 0
    self._hp = hp
    self._sht = False
    self._lastShot = 0 # Server only
    self.lastUpdate = update # Server only

  def getIp(self):
    return self._ip
  
  def getId(self):
    return self._id
  
  def getPosX(self):
    return self._posX
  
  def setPosX(self, posX):
    self._posX = posX
  
  def getPosY(self):
    return self._posY
  
  def setPosY(self, posY):
    self._posY = posY
  
  def getRotation(self):
    return self._rot
  
  def setRotation(self, rot):
    self._rot = rot
  
  def getHp(self):
    return self._hp
  
  def setHp(self, hp):
    self._hp = hp

  def addHp(self, amount):
    self._hp += amount
    if self._hp > 100:
      self._hp = 100
  
  def getShooting(self):
    return self._sht
  
  def setShooting(self, shooting):
    self._sht = shooting

  def getLastShot(self):
    return self._lastShot
  
  def setLastShot(self, lastShot):
    self._lastShot = lastShot

  def getLastUpdate(self):
    return self.lastUpdate
  
  def setLastUpdate(self, lastUpdate):
    self.lastUpdate = lastUpdate

  def getBytes(self):
    # print(self.getId(), self.getPosX(), self.getPosY(), self.getRotation(), self.getHp())
    pid = self.getId().to_bytes(1, 'little')
    posX = self.getPosX().to_bytes(2, 'little', signed=True) # BREAKS!
    posY = self.getPosY().to_bytes(2, 'little', signed=True)
    rot = self.getRotation().to_bytes(2, 'little', signed=True)
    hp = self.getHp().to_bytes(1, 'little', signed=True)
    shooting = int(self._sht).to_bytes(1, 'little')

    return pid + posX + posY + rot + hp + shooting

class Projectile:
  def __init__(self, owner, ID, posX, posY, velX, velY, ls):
    self._owner = owner
    self._id = ID
    self._posX = posX
    self._posY = posY
    self._velX = velX
    self._velY = velY
    self._ls = ls
    self._hit = [] # Server only
  
  def getOwner(self):
    return self._owner
  
  def setOwner(self, owner):
    self._owner = owner

  def getId(self):
    return self._id
  
  def getPosX(self):
    return self._posX
  
  def setPosX(self, posX):
    self._posX = posX
  
  def getPosY(self):
    return self._posY
  
  def setPosY(self, posY):
    self._posY = posY
  
  def getVelX(self):
    return self._velX

  def setVelX(self, velX):
    self._velX = velX

  def getVelY(self):
    return self._velY
  
  def setVel(self, velY):
    self._velY = velY

  def getLifespan(self):
    return self._ls
  
  def setLifespan(self, ls):
    self._ls = ls

  def reduceLifespan(self, amount):
    self._ls -= amount

  def updatePos(self, modifier=1):
    self._posX += modifier * self.getVelX()
    self._posY += modifier * self.getVelY()

  def getHitTargets(self):
    return self._hit

  def addHitTarget(self, target):
    self._hit.append(target)

  def hitPlayer(self, target):
    if target == self.getOwner():
      return False
    for hit in self.getHitTargets():
      if hit == target:
        return False
    return True

  def getBytes(self):
    # SOMETHING TOO BIG TO CONVERT! PLZ FIXXX!
    owner = self.getOwner().to_bytes(1, 'little')
    ID = self.getId().to_bytes(1, 'little')
    posX = round(self.getPosX()).to_bytes(2, 'little', signed=True)
    posY = round(self.getPosY()).to_bytes(2, 'little', signed=True)
    velX = round(self.getVelX()).to_bytes(1, 'little', signed=True)
    velY = round(self.getVelY()).to_bytes(1, 'little', signed=True)
    ls = round(self.getLifespan()).to_bytes(1, 'little')

    return owner + ID + posX + posY + velX + velY + ls