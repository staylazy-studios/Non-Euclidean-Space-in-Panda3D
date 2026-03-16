"""
BEWARE!!!
SPAGHETTI CODE
I'm so sorry
"""


from panda3d.core import Plane, PlaneNode, NodePath, WindowProperties, CollisionTraverser, CollisionRay, CollisionNode, CollideMask, CollisionHandlerQueue, CollisionHandlerPusher, CollisionSphere
from direct.showbase.ShowBase import ShowBase
import sys

CAMERA_HEIGHT = 3
CAMERA_FOV = 90
PLAYER_SPEED = 4

class Scene(ShowBase):
    def clipPlaneStuff(self):
        self.fl.lookAt(self.camera)

        h = self.fl.getH()

        if h < 90 and h > -90:
            self.section = "top_half"
        elif h > 90 and h < 180:
            self.section = "bottom_left"
        elif h < -90 and h > -180:
            self.section = "bottom_right"

        if self.section == "top_half":
            if self.monkey.hasClipPlane(self.plane_np1):
                if self.clockwise:
                    self.monkey.setClipPlaneOff(self.plane_np1)
                else:
                    self.monkey.hide()
                    self.monkeyColNp.stash()
            if self.ring.hasClipPlane(self.plane_np2):
                if not self.clockwise:
                    self.ring.setClipPlaneOff(self.plane_np2)
                else:
                    self.ring.hide()
                    self.ringColNp.stash()
        elif self.section == "bottom_left":
            if self.monkey.hasClipPlane(self.plane_np1) and self.monkey.isHidden() and self.clockwise and self.beforeSection == "bottom_right":
                    self.monkey.show()
                    self.monkeyColNp.unstash()
            elif not self.monkey.hasClipPlane(self.plane_np1):
                if self.clockwise and self.monkey.isHidden():
                    self.monkey.show()
                    self.monkeyColNp.unstash()
                self.monkey.setClipPlane(self.plane_np1)
        else: # bottom_right
            if self.ring.hasClipPlane(self.plane_np2) and self.ring.isHidden() and not self.clockwise and self.beforeSection == "bottom_left":
                self.ring.show()
                self.ringColNp.unstash()
            elif not self.ring.hasClipPlane(self.plane_np2):
                if not self.clockwise and self.ring.isHidden():
                    self.ring.show()
                    self.ringColNp.unstash()
                self.ring.setClipPlane(self.plane_np2)

        self.plane_np1.setH(h)
        
        self.clockwise = h - self.beforeH < 0
        
        self.beforeH = h
        self.beforeSection = self.section

    def __init__(self):
        super().__init__()
        self.disableMouse()
        #self.oobe()

        self.map = self.loader.loadModel("models/map.bam")
        self.showMesh(self.map)
        self.map.reparentTo(self.render)

        self.monkey = self.map.find("**/Monkey")
        self.ring = self.map.find("**/Ring")

        self.monkeyColNp = self.monkey.find("**/+CollisionNode")
        self.ringColNp = self.ring.find("**/+CollisionNode")

        plane1 = Plane((0, 0, -2), (0, 0, 2), (0, -1, 0))
        plane_node1 = PlaneNode("plane", plane1)
        self.plane_np1 = self.render.attachNewNode(plane_node1)
        self.monkey.setClipPlane(self.plane_np1)

        self.pillar = self.map.find("**/Pillar")
        self.fl = NodePath("floater")
        self.fl.setPos(self.pillar.getPos())

        self.plane_np1.reparentTo(self.pillar)

        self.beforeH = 0
        self.clockwise = True
        self.enabled = True
        self.section = "top_half"
        self.beforeSection = self.section

        plane2 = Plane((0, 0, -2), (0, 0, 2), (0, 1, 0))
        plane_node2 = PlaneNode("plane", plane2)
        self.plane_np2 = self.render.attachNewNode(plane_node2)
        self.plane_np2.show()
        self.ring.setClipPlane(self.plane_np2)

        self.plane_np2.reparentTo(self.fl)

        # ===== UNIMPORTANT JUNK START =====
        def start():
            # ----- for camera to walk on
            self.camModel = NodePath("floater")
            self.camModel.reparentTo(self.render)
            self.camera.reparentTo(self.camModel)

            # ----- collisions start
            self.cTrav = CollisionTraverser()

            self.camCol = CollisionNode('player')
            self.camCol.addSolid(CollisionSphere(center=(0, 0, -2), radius=0.5))
            self.camCol.addSolid(CollisionSphere(center=(0, -0.25, 0), radius=0.5))
            #self.camCol.setFromCollideMask(CollideMask.bit(0))
            #self.camCol.setIntoCollideMask(CollideMask.bit(0))
            self.camCol.setFromCollideMask(CollideMask.bit(1))
            self.camCol.setIntoCollideMask(CollideMask.bit(1))
            self.camColNp = self.camModel.attachNewNode(self.camCol)
            #self.camColNp.show()

            self.pusher = CollisionHandlerPusher()
            self.pusher.horizontal = True

            self.pusher.addCollider(self.camColNp, self.camModel)
            self.cTrav.addCollider(self.camColNp, self.pusher)

            self.groundRay = CollisionRay()
            self.groundRay.setOrigin(0, 0, 9)
            self.groundRay.setDirection(0, 0, -1)
            self.groundCol = CollisionNode('groundRay')
            self.groundCol.addSolid(self.groundRay)
            self.groundCol.setFromCollideMask(CollideMask.bit(1))
            self.groundCol.setIntoCollideMask(CollideMask.allOff())
            self.groundColNp = self.camModel.attachNewNode(self.groundCol)
            self.groundHandler = CollisionHandlerQueue()
            self.cTrav.addCollider(self.groundColNp, self.groundHandler)

            self.cTrav.setRespectPrevTransform(True)
            # ----- collisions end


            self.keyMap = {
                'a': False,
                'd': False,
                'w': False,
                's': False,
            }

            self.inGame = False
            self.rotateH, self.rotateP = 0, 0
            self.pitchMax, self.pitchMin = 40, -90
            self.lastMouseX, self.lastMouseY = 0, 0
            self.speed = PLAYER_SPEED
            self.fullscreen = False


            self.accept('a', self.setKey, ['a', True])
            self.accept('d', self.setKey, ['d', True])
            self.accept('w', self.setKey, ['w', True])
            self.accept('s', self.setKey, ['s', True])
            self.accept('a-up', self.setKey, ['a', False])
            self.accept('d-up', self.setKey, ['d', False])
            self.accept('w-up', self.setKey, ['w', False])
            self.accept('s-up', self.setKey, ['s', False])

            self.accept("f11", self.toggleFullscreen)
            self.accept("mouse1", self.mouseClick)
            self.accept("escape", sys.exit)

            self.camModel.setZ(CAMERA_HEIGHT)
            self.camLens.setNear(0.1)
            self.camLens.setFov(CAMERA_FOV)

            self.taskMgr.add(self.update, "update")
        start()
        # ===== UNIMPORTANT JUNK END =====
    
    def update(self, task):
        dt = self.taskMgr.globalClock.getDt()

        self.cameraMovement(dt)

        if self.keyMap['a']:
            self.camModel.setFluidX(self.camera, -self.speed * dt)
        if self.keyMap['d']:
            self.camModel.setFluidX(self.camera, +self.speed * dt)
        if self.keyMap['w']:
            self.camModel.setFluidY(self.camera, +self.speed * dt)
        if self.keyMap['s']:
            self.camModel.setFluidY(self.camera, -self.speed * dt)
        #self.camera.setZ(3)

        
        groundEntries = list(self.groundHandler.entries)
        groundEntries.sort(key=lambda x: x.getSurfacePoint(self.render).getZ())
        
        for entry in groundEntries:
            if entry.getIntoNode().name == 'Ground':
                self.camModel.setFluidZ(entry.getSurfacePoint(self.render).getZ()+CAMERA_HEIGHT)
        
        self.clipPlaneStuff()
        
        return task.cont
    
     # Records the state of the wasd and shift keys
    def setKey(self, key, value):
        self.keyMap[key] = value

    # Toggles fullscreen
    def toggleFullscreen(self):
        self.fullscreen = not self.fullscreen

        wp = WindowProperties()
        wp.fullscreen = self.fullscreen
        if self.fullscreen:
            wp.size = (1920, 1080)
        else:
            wp.size = (1280, 720)
            wp.origin = (-2, -2)
            wp.fixed_size = True
        self.win.requestProperties(wp)
    
    # Toggles if player is in game
    def toggleIngame(self):
        self.inGame = not self.inGame

        wp = WindowProperties()
        wp.setCursorHidden(self.inGame)
        if self.inGame:
            wp.setMouseMode(WindowProperties.M_confined)
        else:
            wp.setMouseMode(WindowProperties.M_absolute)
        self.win.requestProperties(wp)
    
    # Method that gets called every time left mouse button is clicked
    def mouseClick(self):
        if self.inGame:
            pass
        else:
            self.toggleIngame()

    # Recenters the cursor position
    def recenterCursor(self):
        self.win.movePointer(
            0,
            int(self.win.getProperties().getXSize() / 2),
            int(self.win.getProperties().getYSize() / 2)
        )

    def cameraMovement(self, dt):
        if self.inGame:
            mw = self.mouseWatcherNode
            if mw.hasMouse():
                x, y = mw.getMouseX(), mw.getMouseY()
                if self.lastMouseX is not None:
                    dx, dy = x, y
                else:
                    dx, dy = 0, 0
                self.lastMouseX, self.lastMouseY = x, y
            else:
                self.toggleIngame()
                x, y, dx, dy = 0, 0, 0, 0
            self.recenterCursor()
            self.lastMouseX, self.lastMouseY = 0, 0
            
            self.rotateH -= dx * dt * 1500
            self.rotateP += dy * dt * 1000

            if self.rotateP > self.pitchMax:
                self.rotateP -= self.rotateP - self.pitchMax
            elif self.rotateP < self.pitchMin:
                self.rotateP -= self.rotateP - self.pitchMin

            self.camera.setH(self.rotateH)
            self.camera.setP(self.rotateP)
    
    def showMesh(self, model):
        for node in model.findAllMatches("**/+CollisionNode"):
            parent = node.getParent()
            for geomNode in parent.findAllMatches('**/+GeomNode'):
                geomNode.reparentTo(parent)

Scene().run()