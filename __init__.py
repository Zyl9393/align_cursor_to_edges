bl_info = {
    "name": "Align 3D Cursor to Edges",
    "description": "Rotate 3D cursor to align its axes with selected edges.",
    "author": "Zyl",
    "version": (1, 1),
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

    moveCursor: bpy.props.BoolProperty(name="Move Cursor", default=True)

    @classmethod
    def poll(self, context: bpy.types.Context):
        return context.active_object is not None and context.active_object.mode == 'EDIT'

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event):
        bm = bmesh.from_edit_mesh(context.active_object.data)
        edges = [e for e in bm.edges if e.select]
        if len(edges) == 2:
            i0, i1 = 0, 1
            if 'EDGE' in bm.select_mode and bm.select_history.active is not None and bm.select_history.active.index != edges[i0].index:
                i0, i1 = i1, i0
            edgeImportant = (context.active_object.matrix_world @ edges[i0].verts[0].co, context.active_object.matrix_world @ edges[i0].verts[1].co)
            edgeSecondary = (context.active_object.matrix_world @ edges[i1].verts[0].co, context.active_object.matrix_world @ edges[i1].verts[1].co)
            if edges[i0].verts[1] == edges[i1].verts[0] or edges[i0].verts[1] == edges[i1].verts[1]:
                coCursorNew = edgeImportant[1]
            else:
                coCursorNew = edgeImportant[0]
            axisImportant = Vector(np.subtract(edgeImportant[1], edgeImportant[0])).normalized()
            axisSecondaryHint = Vector(np.subtract(edgeSecondary[1], edgeSecondary[0])).normalized()
            axisSecondary = axisImportant.cross(axisSecondaryHint).normalized()
            axisImportantMajor = getMajorAxis(axisImportant)
            axisSecondaryMajor = getMajorAxis(axisSecondary)
            if axisImportantMajor[0] == -1 or axisImportantMajor[1] == -1 or axisImportantMajor[2] == -1:
                axisImportant = -1 * axisImportant

            if abs(axisImportantMajor[0]) == 1:
                xAxis = axisImportant
                if abs(axisSecondaryMajor[1]) == 1:
                    if axisSecondary[1] < 0:
                        axisSecondary = -1 * axisSecondary
                    yAxis = axisSecondary
                    zAxis = xAxis.cross(yAxis)
                else:
                    if axisSecondary[2] < 0:
                        axisSecondary = -1 * axisSecondary
                    zAxis = axisSecondary
                    yAxis = xAxis.cross(zAxis)
            elif abs(axisImportantMajor[1]) == 1:
                yAxis = axisImportant
                if abs(axisSecondaryMajor[0]) == 1:
                    if axisSecondary[0] < 0:
                        axisSecondary = -1 * axisSecondary
                    xAxis = axisSecondary
                    zAxis = xAxis.cross(yAxis)
                else:
                    if axisSecondary[2] < 0:
                        axisSecondary = -1 * axisSecondary
                    zAxis = axisSecondary
                    xAxis = zAxis.cross(yAxis)
            else:
                zAxis = axisImportant
                if abs(axisSecondaryMajor[0]) == 1:
                    if axisSecondary[0] < 0:
                        axisSecondary = -1 * axisSecondary
                    xAxis = axisSecondary
                    yAxis = xAxis.cross(zAxis)
                else:
                    if axisSecondary[1] < 0:
                        axisSecondary = -1 * axisSecondary
                    yAxis = axisSecondary
                    xAxis = zAxis.cross(yAxis)

            matrixCursorNew = Matrix(((xAxis[0], yAxis[0], zAxis[0], 0.0), (xAxis[1], yAxis[1], zAxis[1], 0.0), (xAxis[2], yAxis[2], zAxis[2], 0.0), (0.0, 0.0, 0.0, 1.0)))
            rotationCursorNew = matrixCursorNew.to_quaternion()
            rotationModeOriginal = context.scene.cursor.rotation_mode
            if context.scene.cursor.rotation_mode != 'QUATERNION':
                context.scene.cursor.rotation_mode = 'QUATERNION'
            if self.moveCursor:
                context.scene.cursor.location = coCursorNew
            context.scene.cursor.rotation_quaternion = rotationCursorNew
            if rotationModeOriginal != 'QUATERNION':
                context.scene.cursor.rotation_mode = rotationModeOriginal
        else:
            self.report({'ERROR'}, "Need to select two edges.")
            return {"CANCELLED"}
        return {'FINISHED'}

def unregister():
    bpy.utils.unregister_class(VIEW3D_OT_align_cursor_to_edges)

def register():
    bpy.utils.register_class(VIEW3D_OT_align_cursor_to_edges)
