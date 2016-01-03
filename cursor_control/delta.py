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

      LATER:

      ISSUES:
          Bugs:
          Mites:

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
from geometry_utils import *
from cursor_control.operators import *


PRECISION=4



class VIEW3D_PT_ccDelta(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Cursor Delta"
    bl_default_closed = True

    initDone = False

    @classmethod
    def poll(cls, context):
      
        if not VIEW3D_PT_ccDelta.initDone:
            #print ("Cursor Memory draw-callback registration...")
            sce = context.scene
            if context.area.type == 'VIEW_3D':
                for reg in context.area.regions:
                    if reg.type == 'WINDOW':
                        # Register callback for delta-draw
                        reg.callback_add(cursor_delta_draw,(cls,context),'POST_PIXEL')
                        # Flag success
                        VIEW3D_PT_ccDelta.initDone = True
                        # print ("Cursor Memory draw-callback registered")
            #else:
                #print("View3D not found, cannot run operator")
      
        # Display in object or edit mode.
        if (context.area.type == 'VIEW_3D' and
            (context.mode.startswith('EDIT')
            or context.mode == 'OBJECT')):
            cc = context.scene.cursor_control.deltaEnabled[0] = 1
            return 1

        cc = context.scene.cursor_control.deltaEnabled[0] = 0
        return 0

    def draw_header(self, context):
        layout = self.layout
        cc = context.scene.cursor_control
        if cc.deltaLocationDraw:
            GUI.drawIconButton(True, layout, 'RESTRICT_VIEW_OFF', "view3d.cursor_delta_toggledraw", False)
        else:
            GUI.drawIconButton(True, layout, 'RESTRICT_VIEW_ON' , "view3d.cursor_delta_toggledraw", False)
 
    def draw(self, context):
        layout = self.layout
        #sce = context.scene

        cc = context.scene.cursor_control
        (tvs,tes,tfs,edit_mode) = cc.guiStates(context)
        
        row = layout.row()
        col = row.column();
        GUI.drawIconButton(True , col, 'FF'  , "view3d.ccdelta_add")
        GUI.drawIconButton(True , col, 'REW'  , "view3d.ccdelta_sub")
        GUI.drawIconButton(tvs<=2 , col, 'FORWARD'  , "view3d.ccdelta_vvdist")
        
        col = row.column();
        col.prop(cc, "deltaVector")

        col = row.column();
        GUI.drawIconButton(True , col, 'MOD_MIRROR'  , "view3d.ccdelta_invert")
        GUI.drawIconButton(True , col, 'SNAP_NORMAL'  , "view3d.ccdelta_normalize")



def cursor_delta_draw(cls,context):
    cc = context.scene.cursor_control

    draw = 0
    if hasattr(cc, "deltaLocationDraw"):
        draw = cc.deltaLocationDraw
    if hasattr(cc, "deltaEnabled"):
        if(not cc.deltaEnabled[0]):
            draw = 0

    if not draw:
        return
        
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glShadeModel(bgl.GL_FLAT)
    alpha = 1-PHI_INV
    
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

    c = Vector(CursorAccess.getCursor())
    p1 = c + Vector(cc.deltaVector)
    locationC = region3d_get_2d_coordinates(context, c)
    location = region3d_get_2d_coordinates(context, p1)
    bgl.glColor4f(0, 1, 1, alpha)
    bgl.glBegin(bgl.GL_LINE_STRIP)
    bgl.glVertex2f(locationC[0], locationC[1])
    bgl.glVertex2f(location[0], location[1])
    bgl.glEnd()

    #bgl.glColor4f(0, 1, 1, alpha)
    bgl.glBegin(bgl.GL_LINE_LOOP)
    for i in range(14):
        bgl.glVertex2f(location[0]+offset[i][0], location[1]+offset[i][1])
    bgl.glEnd()

    # Crosshair
    offset2 = 20
    offset = 5
    #bgl.glColor4f(0, 1, 1, alpha)
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

    # distance to cursor
    blf.size(0, 10, 72)  # Prevent font size to randomly change.
    d = Vector(cc.deltaVector).length
    blf.position(0, location[0]+10, location[1]+10, 0)
    blf.draw(0, str(round(d,PRECISION)))


