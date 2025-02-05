from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    CollisionTraverser,
    CollisionNode,
    CollisionRay,
    CollisionHandlerQueue,
    BitMask32,
    Vec3,
    WindowProperties,
)
from direct.task import Task
import sys, math


def clamp(value, min_val, max_val):
    return max(min(value, max_val), min_val)


class VoxelGame(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        # Disable the default mouse-based camera control.
        self.disableMouse()

        # Hide the mouse cursor.
        props = WindowProperties()
        props.setCursorHidden(True)
        self.win.requestProperties(props)

        # Set initial camera position and orientation.
        self.camera.setPos(0, -10, 2)
        self.camera.setHpr(0, 0, 0)

        # Dictionary to keep track of blocks.
        # Keys are (x, y, z) tuples and values are the NodePaths for each block.
        self.blocks = {}

        # Load a cube model. Panda3D comes with a built-in cube in the "models/box" file.
        self.block_model = loader.loadModel("models/box")
        # Scale the cube so that each block is 1x1x1 (the default cube is 2x2x2).
        self.block_model.setScale(0.5)
        self.block_model.flattenLight()

        # Build a simple flat world (e.g. a 21x21 grid centered at (0,0,0)).
        for x in range(-10, 11):
            for y in range(-10, 11):
                self.addBlock(x, y, 0)

        # Setup collision detection for mouse picking.
        self.picker = CollisionTraverser()
        self.pq = CollisionHandlerQueue()
        self.picker_node = CollisionNode("mouseRay")
        self.picker_np = self.camera.attachNewNode(self.picker_node)
        # Set this node to collide with blocks (we use bit 1 for blocks).
        self.picker_node.setFromCollideMask(BitMask32.bit(1))
        self.picker_ray = CollisionRay()
        self.picker_node.addSolid(self.picker_ray)
        self.picker.addCollider(self.picker_np, self.pq)

        # Accept mouse button events.
        self.accept("mouse1", self.removeBlockAtMouse)
        self.accept("mouse3", self.addBlockAtMouse)

        # Set up key controls for basic first-person movement.
        self.keyMap = {
            "forward": False,
            "backward": False,
            "left": False,
            "right": False,
        }
        self.accept("w", self.setKey, ["forward", True])
        self.accept("w-up", self.setKey, ["forward", False])
        self.accept("s", self.setKey, ["backward", True])
        self.accept("s-up", self.setKey, ["backward", False])
        self.accept("a", self.setKey, ["left", True])
        self.accept("a-up", self.setKey, ["left", False])
        self.accept("d", self.setKey, ["right", True])
        self.accept("d-up", self.setKey, ["right", False])
        self.accept("escape", sys.exit)

        # Add the update task to move the camera and process mouse look.
        self.taskMgr.add(self.updateCamera, "updateCamera")

        # Center the mouse pointer.
        self.centerMouse()

    def setKey(self, key, value):
        self.keyMap[key] = value

    def addBlock(self, x, y, z):
        """Adds a block at the specified integer grid coordinate if one isn't already present."""
        if (x, y, z) in self.blocks:
            return
        block = self.block_model.copyTo(render)
        block.setPos(x, y, z)
        # Enable collision on the block.
        block.setCollideMask(BitMask32.bit(1))
        self.blocks[(x, y, z)] = block

    def removeBlock(self, x, y, z):
        """Removes a block at the specified coordinate, if present."""
        if (x, y, z) in self.blocks:
            self.blocks[(x, y, z)].removeNode()
            del self.blocks[(x, y, z)]

    def addBlockAtMouse(self):
        """Casts a ray from the camera to where the mouse is pointing and adds a block adjacent to the hit face."""
        if not self.mouseWatcherNode.hasMouse():
            return
        mpos = self.mouseWatcherNode.getMouse()
        self.picker_ray.setFromLens(self.camNode, mpos.getX(), mpos.getY())
        self.picker.traverse(render)
        if self.pq.getNumEntries() > 0:
            self.pq.sortEntries()
            entry = self.pq.getEntry(0)
            hitPos = entry.getSurfacePoint(render)
            normal = entry.getSurfaceNormal(render)
            # Compute the position for the new block by offsetting half a unit in the direction of the hit normal.
            newPos = hitPos + normal * 0.5
            newBlockPos = (
                int(round(newPos.getX())),
                int(round(newPos.getY())),
                int(round(newPos.getZ())),
            )
            self.addBlock(*newBlockPos)

    def removeBlockAtMouse(self):
        """Casts a ray from the camera to the mouse and removes the block hit."""
        if not self.mouseWatcherNode.hasMouse():
            return
        mpos = self.mouseWatcherNode.getMouse()
        self.picker_ray.setFromLens(self.camNode, mpos.getX(), mpos.getY())
        self.picker.traverse(render)
        if self.pq.getNumEntries() > 0:
            self.pq.sortEntries()
            entry = self.pq.getEntry(0)
            # The hit position approximates the center of the block.
            hitPos = entry.getSurfacePoint(render)
            blockPos = (
                int(round(hitPos.getX())),
                int(round(hitPos.getY())),
                int(round(hitPos.getZ())),
            )
            self.removeBlock(*blockPos)

    def updateCamera(self, task):
        dt = globalClock.getDt()
        # Mouse look: get the pointer's movement and update the camera heading and pitch.
        if self.mouseWatcherNode.hasMouse():
            md = self.win.getPointer(0)
            x = md.getX()
            y = md.getY()
            winProps = self.win.getProperties()
            centerX = winProps.getXSize() / 2
            centerY = winProps.getYSize() / 2
            deltaX = x - centerX
            deltaY = y - centerY
            sensitivity = 0.2
            self.camera.setH(self.camera.getH() - deltaX * sensitivity)
            # Clamp the pitch to avoid flipping.
            self.camera.setP(clamp(self.camera.getP() - deltaY * sensitivity, -90, 90))
            self.centerMouse()

        # Movement: determine the direction based on key presses.
        direction = Vec3(0, 0, 0)
        if self.keyMap["forward"]:
            direction += self.camera.getQuat(render).getForward()
        if self.keyMap["backward"]:
            direction -= self.camera.getQuat(render).getForward()
        if self.keyMap["left"]:
            direction -= self.camera.getQuat(render).getRight()
        if self.keyMap["right"]:
            direction += self.camera.getQuat(render).getRight()
        direction.setZ(0)
        if direction.length() != 0:
            direction.normalize()
        speed = 5  # Movement speed units per second.
        self.camera.setPos(self.camera.getPos() + direction * speed * dt)
        return Task.cont

    def centerMouse(self):
        """Re-centers the mouse pointer to the window center."""
        winProps = self.win.getProperties()
        centerX = int(winProps.getXSize() / 2)
        centerY = int(winProps.getYSize() / 2)
        self.win.movePointer(0, centerX, centerY)


if __name__ == "__main__":
    game = VoxelGame()
    game.run()
