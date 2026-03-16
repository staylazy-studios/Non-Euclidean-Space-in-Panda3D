"""
BEWARE!!!
SPAGHETTI CODE
I'm so sorry
"""


from panda3d.core import Plane, PlaneNode, NodePath, WindowProperties, CollisionTraverser, CollisionRay, CollisionNode, CollideMask, CollisionHandlerQueue, CollisionHandlerPusher, CollisionSphere, PointLight, AmbientLight, Shader
from direct.showbase.ShowBase import ShowBase
import sys

CAMERA_HEIGHT = 3
CAMERA_FOV = 90
PLAYER_SPEED = 4

RIGHT_SIDE = 0
LEFT_SIDE = 1
BOTTOM = 2

class Scene(ShowBase):
    def setupClipPlaneStuff(self):
        self.room1 = self.map.find("**/Room1")
        self.room1.reparentTo(self.render)
        
        self.room2 = self.map.find("**/Room2")
        self.room2.reparentTo(self.render)
        
        self.room1ColNp = self.room1.find("**/+CollisionNode")
        self.room2ColNp = self.room2.find("**/+CollisionNode")
        
        self.floater = self.map.find("**/PivotPoint")
        self.floater.reparentTo(self.render)

        plane1 = Plane((0, 0, -2), (0, 0, 2), (0, -1, 0))
        plane_node1 = PlaneNode("plane", plane1)
        self.plane_np1 = self.render.attachNewNode(plane_node1)
        self.room1.setClipPlane(self.plane_np1)

        plane2 = Plane((0, 0, -2), (0, 0, 2), (0, 1, 0))
        plane_node2 = PlaneNode("plane", plane2)
        self.plane_np2 = self.render.attachNewNode(plane_node2)
        self.room2.setClipPlane(self.plane_np2)

        self.section = BOTTOM
        self.beforeSection = self.section
    
    def clipPlaneStuff(self):
        self.floater.lookAt(self.camera)

        h = self.floater.getH()
        
        if h < 0 and h > -90:
            self.section = RIGHT_SIDE
        elif h > 90 and h < 180:
            self.section = LEFT_SIDE
        elif h < -90 and h > -180:
            self.section = BOTTOM

        if self.section == RIGHT_SIDE:
            if self.beforeSection == BOTTOM:
                self.room1.hide()
                self.room1ColNp.stash()
                self.room2.setClipPlaneOff(self.plane_np2)
        elif self.section == LEFT_SIDE:
            if self.beforeSection == BOTTOM:
                self.room2.hide()
                self.room2ColNp.stash()
                self.room1.setClipPlaneOff(self.plane_np1)
        elif self.section == BOTTOM:
            if self.beforeSection == RIGHT_SIDE:
                self.room1.show()
                self.room1ColNp.unstash()
                self.room2.setClipPlane(self.plane_np2)
            elif self.beforeSection == LEFT_SIDE:
                self.room2.show()
                self.room2ColNp.unstash()
                self.room1.setClipPlane(self.plane_np1)

        self.plane_np1.setH(h)
        self.plane_np2.setH(h)
        
        self.beforeSection = self.section

    def __init__(self):
        super().__init__()
        self.disableMouse()
        #self.oobe()

        self.map = self.loader.loadModel("models/new_map.bam")
        self.showMesh(self.map)
        self.map.reparentTo(self.render)

        self.setupClipPlaneStuff()

        plight = PointLight("plight")
        plnp = self.render.attachNewNode(plight)
        plnp.setPos(0, -5, 8)
        self.render.setLight(plnp)

        alight = AmbientLight("alight")
        alight.setColor((0.2, 0.2, 0.2, 1))
        alnp = self.render.attachNewNode(alight)
        self.render.setLight(alnp)


        # ----- shaders
        #shader = Shader.load(
        #    Shader.SL_GLSL,
        #    "simplepbr.vert",
        #    "simplepbr.frag"
        #)
        #self.render.setShader(shader)


        # ===== UNIMPORTANT JUNK START =====
        def start():
            # ----- for camera to walk on
            self.camModel = NodePath("floater")
            self.camModel.reparentTo(self.render)
            self.camera.reparentTo(self.camModel)

            self.camModel.setPos(5, -5, 0)

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