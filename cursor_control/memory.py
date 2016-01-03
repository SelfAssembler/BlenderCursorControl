# -*- coding: utf-8 -*-
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####



"""
  TODO:

      IDEAS:
	  Add/Subtract
	  
      LATER:

      ISSUES:
          Bugs:
          Mites:
	      CTRL-Z forces memory to world origin (0,0,0)... why??
		  Happens only if undo reaches 'default world state'
		  How to Reproduce:
		      1. File->New
		      2. Move 3D-cursor
		      3. Set memory
		      4. Move cube
		      5. CTRL-Z

      QUESTIONS:
  
  
"""



import bpy
import bgl
import blf
import math
from mathutils import Vector, Matrix
from mathutils import geometry
from misc_utils import *
from constants_utils import *
from cursor_utils import *
from ui_utils import *
#from cursor_control import history



PRECISION = 4



class CursorMemoryData(bpy.types.PropertyGroup):

    savedLocationEnabled = [0]
    savedLocationDraw = bpy.props.BoolProperty(description="Draw SL cursor in 3D view",default=1)
    savedLocation = bpy.props.FloatVectorProperty(name="",description="Saved Location",precision=PRECISION)


class VIEW3D_OT_cursor_memory_save(bpy.types.Operator):
    '''Save cursor location'''
    bl_idname = "view3d.cursor_memory_save"
    bl_label = "Save cursor location"
    bl_options = {'REGISTER'}

    def modal(self, context, event):
        return {'FINISHED'}

    def execute(self, context):
        cc = context.scene.cursor_memory
        cc.savedLocation = CursorAccess.getCursor()
        CursorAccess.setCursor(cc.savedLocation)
        return {'FINISHED'}



class VIEW3D_OT_cursor_memory_swap(bpy.types.Operator):
    '''Swap cursor location'''
    bl_idname = "view3d.cursor_memory_swap"
    bl_label = "Swap cursor location"
    bl_options = {'REGISTER'}

    def modal(self, context, event):
        return {'FINISHED'}

    def execute(self, context):
        location = CursorAccess.getCursor().copy()
        cc = context.scene.cursor_memory
        CursorAccess.setCursor(cc.savedLocation)
        cc.savedLocation = location
        #history.VIEW3D_OT_CursorTracker.track(context)
        return {'FINISHED'}



class VIEW3D_OT_cursor_memory_recall(bpy.types.Operator):
    '''Recall cursor location'''
    bl_idname = "view3d.cursor_memory_recall"
    bl_label = "Recall cursor location"
    bl_options = {'REGISTER'}

    def modal(self, context, event):
        return {'FINISHED'}

    def execute(self, context):
        cc = context.scene.cursor_memory
        CursorAccess.setCursor(cc.savedLocation)
        #history.VIEW3D_OT_CursorTracker.track(context)
        return {'FINISHED'}



#class VIEW3D_OT_cursor_memory_show(bpy.types.Operator):
    #'''Show cursor memory'''
    #bl_idname = "view3d.cursor_memory_show"
    #bl_label = "Show cursor memory"
    #bl_options = {'REGISTER'}

    #def modal(self, context, event):
        #return {'FINISHED'}

    #def execute(self, context):
        #cc = context.scene.cursor_memory
        #cc.savedLocationDraw = True
        #BlenderFake.forceRedraw()
        #return {'FINISHED'}



#class VIEW3D_OT_cursor_memory_hide(bpy.types.Operator):
    #'''Hide cursor memory'''
    #bl_idname = "view3d.cursor_memory_hide"
    #bl_label = "Hide cursor memory"
    #bl_options = {'REGISTER'}

    #def modal(self, context, event):
        #return {'FINISHED'}

    #def execute(self, context):
        #cc = context.scene.cursor_memory
        #cc.savedLocationDraw = False
        #BlenderFake.forceRedraw()
        #return {'FINISHED'}



class VIEW3D_OT_cursor_memory_toggledraw(bpy.types.Operator):
    '''Toggle cursor memory'''
    bl_idname = "view3d.cursor_memory_toggledraw"
    bl_label = "Toggle cursor memory"
    bl_options = {'REGISTER'}

    def modal(self, context, event):
        return {'FINISHED'}

    def execute(self, context):
        cc = context.scene.cursor_memory
        cc.savedLocationDraw = not cc.savedLocationDraw
        BlenderFake.forceRedraw()
        return {'FINISHED'}



class VIEW3D_PT_cursor_memory(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Cursor Memory"
    bl_default_closed = True

    initDone = False
    
    @classmethod
    def poll(cls, context):
      
        if not VIEW3D_PT_cursor_memory.initDone:
            #print ("Cursor Memory draw-callback registration...")
            sce = context.scene
            if context.area.type == 'VIEW_3D':
                for reg in context.area.regions:
                    if reg.type == 'WINDOW':
                        # Register callback for SL-draw
                        reg.callback_add(cursor_memory_draw,(cls,context),'POST_PIXEL')
                        # Flag success
                        VIEW3D_PT_cursor_memory.initDone = True
                        # print ("Cursor Memory draw-callback registered")
            #else:
                #print("View3D not found, cannot run operator")
      
        # Display in object or edit mode.
        if (context.area.type == 'VIEW_3D' and
            (context.mode.startswith('EDIT')
            or context.mode == 'OBJECT')):
            cc = context.scene.cursor_memory.savedLocationEnabled[0] = 1
            return 1

        cc = context.scene.cursor_memory.savedLocationEnabled[0] = 0
        return 0

    def draw_header(self, context):
        layout = self.layout
        cc = context.scene.cursor_memory
        if cc.savedLocationDraw:
            GUI.drawIconButton(True, layout, 'RESTRICT_VIEW_OFF', "view3d.cursor_memory_toggledraw", False)
        else:
            GUI.drawIconButton(True, layout, 'RESTRICT_VIEW_ON' , "view3d.cursor_memory_toggledraw", False)
        #layout.prop(sce, "cursor_memory.savedLocationDraw")

    def draw(self, context):
        layout = self.layout
        sce = context.scene
        cc = context.scene.cursor_memory

        row = layout.row()
        col = row.column()
        row2 = col.row()
        GUI.drawIconButton(True, row2, 'FORWARD', "view3d.cursor_memory_save")
        row2 = col.row()
        GUI.drawIconButton(True, row2, 'FILE_REFRESH', "view3d.cursor_memory_swap")
        row2 = col.row()
        GUI.drawIconButton(True, row2, 'BACK'        , "view3d.cursor_memory_recall")
        col = row.column()
        col.prop(cc, "savedLocation")



def cursor_memory_draw(cls,context):
    cc = context.scene.cursor_memory

    draw = 0
    if hasattr(cc, "savedLocationDraw"):
        draw = cc.savedLocationDraw
    if hasattr(cc, "savedLocationEnabled"):
        if(not cc.savedLocationEnabled[0]):
            draw = 0

    if(draw):
        bgl.glEnable(bgl.GL_BLEND)
        bgl.glShadeModel(bgl.GL_FLAT)
        p1 = Vector(cc.savedLocation)
        location = region3d_get_2d_coordinates(context, p1)
        alpha = 1-PHI_INV
        # Circle
        color = ([0.33, 0.33, 0.33],
            [1, 1, 1],
            [0.33, 0.33, 0.33],
            [1, 1, 1],
            [0.33, 0.33, 0.33],
            [1, 1, 1],
            [0.33, 0.33, 0.33],
            [1, 1, 1],
            [0.33, 0.33, 0.33],
            [1, 1, 1],
            [0.33, 0.33, 0.33],
            [1, 1, 1],
            [0.33, 0.33, 0.33],
            [1, 1, 1])
        offset = ([-4.480736161291701, -8.939966636005579],
            [-0.158097634992133, -9.998750178787843],
            [4.195854066857877, -9.077158622037636],
            [7.718765411993642, -6.357724476147943],
            [9.71288060283854, -2.379065025383466],
            [9.783240669628, 2.070797430975971],
            [7.915909938224691, 6.110513059466902],
            [4.480736161291671, 8.939966636005593],
            [0.15809763499209872, 9.998750178787843],
            [-4.195854066857908, 9.077158622037622],
            [-7.718765411993573, 6.357724476148025],
            [-9.712880602838549, 2.379065025383433],
            [-9.783240669627993, -2.070797430976005],
            [-7.915909938224757, -6.110513059466818])
        bgl.glBegin(bgl.GL_LINE_LOOP)
        for i in range(14):
            bgl.glColor4f(color[i][0], color[i][1], color[i][2], alpha)
            bgl.glVertex2f(location[0]+offset[i][0], location[1]+offset[i][1])
        bgl.glEnd()

        # Crosshair
        offset2 = 20
        offset = 5
        bgl.glColor4f(0, 0, 0, alpha)
        bgl.glBegin(bgl.GL_LINE_STRIP)
        bgl.glVertex2f(location[0]-offset2, location[1])
        bgl.glVertex2f(location[0]- offset, location[1])
        bgl.glEnd()
        bgl.glBegin(bgl.GL_LINE_STRIP)
        bgl.glVertex2f(location[0]+ offset, location[1])
        bgl.glVertex2f(location[0]+offset2, location[1])
        bgl.glEnd()
        bgl.glBegin(bgl.GL_LINE_STRIP)
        bgl.glVertex2f(location[0], location[1]-offset2)
        bgl.glVertex2f(location[0], location[1]- offset)
        bgl.glEnd()
        bgl.glBegin(bgl.GL_LINE_STRIP)
        bgl.glVertex2f(location[0], location[1]+ offset)
        bgl.glVertex2f(location[0], location[1]+offset2)
        bgl.glEnd()

        # Distance to cursor
        blf.size(0, 10, 72)  # Prevent font size to randomly change.
        p1 = Vector(cc.savedLocation)
        p2 = Vector(CursorAccess.getCursor())
        d = (p2-p1).length
        bgl.glColor4f(0, 0, 0, alpha)
        blf.position(0, location[0]+9, location[1]+9, 0)
        blf.draw(0, str(round(d,PRECISION)))
        bgl.glColor4f(1, 1, 1, alpha)
        blf.position(0, location[0]+10, location[1]+10, 0)
        blf.draw(0, str(round(d,PRECISION)))

        
       
