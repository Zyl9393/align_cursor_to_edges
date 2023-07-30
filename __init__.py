bl_info = {
    "name": "Align 3D Cursor to Edges",
    "description": "Rotate 3D cursor to align its axes with selected edges.",
    "author": "Zyl",
    "version": (1, 0),
    "blender": (3, 4, 0),
    "category": "3D View"
}

import bpy
import bmesh
import numpy as np
from mathutils import Vector
from mathutils import Matrix

def getSign(x):
    if x >= 0:
        return 1
    return -1

def getMajorAxis(v):
    x = (abs(v[0]), abs(v[1]), abs(v[2]))
    if x[0] >= x[1]:
        if x[0] >= x[2]:
            return (getSign(v[0]), 0, 0)
        return (0, 0, getSign(v[2]))
    if x[1] >= x[2]:
        return (0, getSign(v[1]), 0)
    return (0, 0, getSign(v[2]))

def getNonMajorAxis(v):
    x = (abs(v[0]), abs(v[1]), abs(v[2]))
    if x[0] >= x[1]:
        if x[0] >= x[2]:
            return (0, 1, 0)
        return (1, 0, 0)
    if x[1] >= x[2]:
        return (1, 0, 0)
    return (1, 0, 0)

class VIEW3D_OT_align_cursor_to_edges(bpy.types.Operator):
    """Rotate 3D cursor to align its axes with selected edges. Active edge takes precedence when selected edges are not at a right angle to each other."""
    bl_idname = "view3d.align_cursor_to_edges"
    bl_label = "Align 3D Cursor to Edges"

    @classmethod
    def poll(self, context: bpy.types.Context):
        return context.active_object is not None and context.active_object.mode == 'EDIT'

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event):
        bm = bmesh.from_edit_mesh(context.active_object.data)
        edges = [e for e in bm.edges if e.select]
        if len(edges) == 2:
            mainEdge = (context.active_object.matrix_world @ edges[0].verts[0].co, context.active_object.matrix_world @ edges[0].verts[1].co)
            secondaryEdge = (context.active_object.matrix_world @ edges[1].verts[0].co, context.active_object.matrix_world @ edges[1].verts[1].co)
            if 'EDGE' in bm.select_mode and bm.select_history.active is not None and bm.select_history.active.index != mainEdge.index:
                mainEdge, secondaryEdge = secondaryEdge, mainEdge
            mainAxis = Vector(np.subtract(mainEdge[1], mainEdge[0])).normalized()
            secondaryAxisHint = Vector(np.subtract(secondaryEdge[1], secondaryEdge[0])).normalized()
            secondaryAxis = mainAxis.cross(secondaryAxisHint).normalized()
            mainAxisMajor = getMajorAxis(mainAxis)
            secondaryAxisMajor = getMajorAxis(secondaryAxis)
            if mainAxisMajor[0] == -1 or mainAxisMajor[1] == -1 or mainAxisMajor[2] == -1:
                mainAxis = -1 * mainAxis

            if abs(mainAxisMajor[0]) == 1:
                xAxis = mainAxis
                if abs(secondaryAxisMajor[1]) == 1:
                    if secondaryAxis[1] < 0:
                        secondaryAxis = -1 * secondaryAxis
                    yAxis = secondaryAxis
                    zAxis = xAxis.cross(yAxis)
                else:
                    if secondaryAxis[2] < 0:
                        secondaryAxis = -1 * secondaryAxis
                    zAxis = secondaryAxis
                    yAxis = xAxis.cross(zAxis)
            elif abs(mainAxisMajor[1]) == 1:
                yAxis = mainAxis
                if abs(secondaryAxisMajor[0]) == 1:
                    if secondaryAxis[0] < 0:
                        secondaryAxis = -1 * secondaryAxis
                    xAxis = secondaryAxis
                    zAxis = xAxis.cross(yAxis)
                else:
                    if secondaryAxis[2] < 0:
                        secondaryAxis = -1 * secondaryAxis
                    zAxis = secondaryAxis
                    xAxis = zAxis.cross(yAxis)
            else:
                zAxis = mainAxis
                if abs(secondaryAxisMajor[0]) == 1:
                    if secondaryAxis[0] < 0:
                        secondaryAxis = -1 * secondaryAxis
                    xAxis = secondaryAxis
                    yAxis = xAxis.cross(zAxis)
                else:
                    if secondaryAxis[1] < 0:
                        secondaryAxis = -1 * secondaryAxis
                    yAxis = secondaryAxis
                    xAxis = zAxis.cross(yAxis)

            thereMatrix = Matrix(((xAxis[0], yAxis[0], zAxis[0], 0.0), (xAxis[1], yAxis[1], zAxis[1], 0.0), (xAxis[2], yAxis[2], zAxis[2], 0.0), (0.0, 0.0, 0.0, 1.0)))
            quat = thereMatrix.to_quaternion()
            originalRotationMode = context.scene.cursor.rotation_mode
            context.scene.cursor.rotation_mode = 'QUATERNION'
            context.scene.cursor.rotation_quaternion = quat
            if originalRotationMode != 'QUATERNION':
                context.scene.cursor.rotation_mode = originalRotationMode
        else:
            self.report({'ERROR'}, "Need to select two edges.")
            return {"CANCELLED"}
        return {'FINISHED'}

def unregister():
    bpy.utils.unregister_class(VIEW3D_OT_align_cursor_to_edges)

def register():
    bpy.utils.register_class(VIEW3D_OT_align_cursor_to_edges)
