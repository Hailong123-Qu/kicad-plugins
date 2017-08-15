#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#

from __future__ import division
import pcbnew

import HelpfulFootprintWizardPlugin as HFPW
import FootprintWizardDrawingAids
import OutlineDrawingAids
import PadArray as PA


class SFM10Wizard(HFPW.HelpfulFootprintWizardPlugin):
    pad_num_pads_vert_key = 'vertical pads count'
    pad_num_pads_horz_key = 'horizontal pads count'
    pad_width_key = 'pad width'
    pad_length_key = 'pad length'
    pad_pitch_key = 'pad pitch'
    pad_handsolder_key = 'hand solder margin'
    
    pad_horz_row_spacing_key = 'horizontal row spacing'
    pad_vert_row_spacing_key = 'vertical row spacing from center'

    body_width_key = 'width'
    body_horz_offset_key = 'horizontal body offset'
    body_length_key = 'length'
    body_x_margin_key = 'x margin'
    body_y_margin_key = 'y margin'
    body_clearance_key = 'pad clearance'
    body_minlength_key = 'segment min length'
    
    def GetName(self):
        return "SFM10"

    def GetDescription(self):
        return "SFM10 footprint wizard"

    def GetValue(self):
        return "SFM10"

    def GenerateParameterList(self):
        self.AddParam("Pads", self.pad_num_pads_vert_key, self.uNatural, 7)
        self.AddParam("Pads", self.pad_num_pads_horz_key, self.uNatural, 24)
        self.AddParam("Pads", self.pad_width_key, self.uMM, 0.7)
        self.AddParam("Pads", self.pad_length_key, self.uMM, 1)
        self.AddParam("Pads", self.pad_pitch_key, self.uMM, 1.1)
        self.AddParam("Pads", self.pad_handsolder_key, self.uMM, 0)
        
        self.AddParam("Pads", self.pad_horz_row_spacing_key, self.uMM, 11.72)
        self.AddParam("Pads", self.pad_vert_row_spacing_key, self.uMM, 6.86)
        
        self.AddParam("Body", self.body_width_key, self.uMM, 13)
        self.AddParam("Body", self.body_horz_offset_key, self.uMM, 0)
        self.AddParam("Body", self.body_length_key, self.uMM, 15)
        self.AddParam("Body", self.body_x_margin_key, self.uMM, 0.1)
        self.AddParam("Body", self.body_y_margin_key, self.uMM, 0.1)
        self.AddParam("Body", self.body_clearance_key, self.uMM, 0.2)
        self.AddParam("Body", self.body_minlength_key, self.uMM, 0.2)

    def CheckParameters(self):
        self.CheckParamInt(
            "Pads", '*' + self.pad_num_pads_horz_key,
            is_multiple_of=2)
    
    def GetPad(self, rot_degree=0):
        pad_length = self.parameters["Pads"][self.pad_length_key]
        pad_width = self.parameters["Pads"][self.pad_width_key]
        pad_handsolder = self.parameters["Pads"][self.pad_handsolder_key]
        
        pad_length_hansolder = pad_length+pad_handsolder
        return PA.PadMaker(self.module).SMDPad(
            pad_length_hansolder, pad_width, 
            shape=pcbnew.PAD_SHAPE_RECT, rot_degree=rot_degree)

    def BuildThisFootprint(self):
                
        pads = self.parameters["Pads"]
        body = self.parameters["Body"]
        
        pad_num_vert_pads = pads['*'+self.pad_num_pads_vert_key] 
        pad_num_horz_pads = pads['*'+self.pad_num_pads_horz_key] 
        pad_width = pads[self.pad_width_key]
        pad_length = pads[self.pad_length_key]
        pad_pitch = pads[self.pad_pitch_key]
        pad_handsolder = pads[self.pad_handsolder_key]

        pad_horz_row_spacing = pads[self.pad_horz_row_spacing_key]
        pad_vert_row_spacing = pads[self.pad_vert_row_spacing_key]
        
        body_width = body[self.body_width_key]
        body_horz_offset = body[self.body_horz_offset_key]
        body_length = body[self.body_length_key]
        body_x_margin = body[self.body_x_margin_key]
        body_y_margin = body[self.body_y_margin_key]
        body_clearance = body[self.body_clearance_key]
        body_minlength = body[self.body_minlength_key]
        
        #bottom row
        pin1Pos = pcbnew.wxPoint(0, pad_horz_row_spacing/2+pad_handsolder/2)
        array = PA.PadLineArray(self.GetPad(), pad_num_horz_pads/2, pad_pitch, False, pin1Pos)
        array.SetFirstPadInArray(1)
        array.AddPadsToModule(self.draw)

        #right row
        pin1Pos = pcbnew.wxPoint(pad_vert_row_spacing+pad_handsolder/2, 0)
        array = PA.PadLineArray(self.GetPad(90), pad_num_vert_pads, -pad_pitch, True, pin1Pos)
        array.SetFirstPadInArray(int(pad_num_horz_pads/2+1))
        array.AddPadsToModule(self.draw)

        #top row
        pin1Pos = pcbnew.wxPoint(0, -pad_horz_row_spacing/2-pad_handsolder/2)
        array = PA.PadLineArray(self.GetPad(), pad_num_horz_pads/2, -pad_pitch, False, pin1Pos)
        array.SetFirstPadInArray(int(pad_num_horz_pads/2+pad_num_vert_pads+1))
        array.AddPadsToModule(self.draw)
        
        # body size
        ssx = body_length+body_x_margin*2
        ssy = body_width+body_y_margin*2

        # Courtyard
        self.draw.SetLayer(pcbnew.F_CrtYd)
        self.draw.Box(body_horz_offset, 0, ssx, ssy)

        # draw silk screen
        self.draw.SetLayer(pcbnew.F_SilkS)
        outline = OutlineDrawingAids.OutlineDrawingAids(self)
        outline.Box(x=body_horz_offset, y=0, w=ssx, h=ssy, 
                    clearance=body_clearance, minlength=body_minlength)        

        #reference and value
        text_size = self.GetTextSize()  # IPC nominal
        self.draw.Value(0, -ssy/2-text_size, text_size)
        self.draw.Reference(0, ssy/2+text_size, text_size)

        
SFM10Wizard().register()
