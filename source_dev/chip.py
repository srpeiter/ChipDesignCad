import numpy as np
import gdsCAD as cad
import time
#import gdspy


class Base_Chip():

    """
    This object represent a single chip and can be considered as the parentobject.
    The reference position is the center of the chip, that is (0,0)
    Reserved layers: 20, 21, 22, 23
    Options for wafer:
        False (Default) --> rectangular chip
        1 --> 1" wafer
        2 --> 2" wafer etc
    Options for label location: By default slightly to the right of x=0 and 700um below upper edge. Can be adjusted by labelloc=(xpos,ypos)
    Options for label linewidth: labelwidth=5 by default
    """
    def __init__(self, name, xdim=1000, ydim=1000, frame=True, label=True, wafer=False, labelloc=(0,0), labelwidth=5):
        
        self.name = name
        self.xdim = xdim
        self.ydim = ydim
        self.wafer = wafer
        wafer_d = [0, 25.4e3, 50.8e3, 76.2e3, 100e3, 125e3, 150e3]  # wafer diameters in um
        
        if xdim < 1001 and ydim < 1001:
            self.boxwidth = 10
        else:
            self.boxwidth = 100
        
            
        self.layer_label = 20
        self.layer_box = 21
        self.layer_alignment = 22
        self.layer_testpads = 23
        
        self.cell = cad.core.Cell(name)
        if frame==True or label==True:
            if wafer==False:
                if labelloc==(0,0):
                    labelloc=(-200.,self.ydim/2. - 2*self.boxwidth-700.)
                self.make_layout(frame,label,labelloc,labelwidth)
            else:
                self.make_wafer(wafer_d[wafer]/2,frame,label,labelloc,labelwidth)


    def make_layout(self,frame,label,labelloc,labelwidth):
        """
        Generate chip with dimensions xdim,ydim
        """
        box=cad.shapes.Box((-self.xdim/2, -self.ydim/2), (self.xdim/2, self.ydim/2),
                         width=self.boxwidth, layer =self.layer_box)

        date = time.strftime("%d/%m/%Y")
        # The label is added 100 um on top of the main cell
        label_grid_chip = cad.shapes.LineLabel( self.name + "  " +\
                                         date,self.boxwidth,
                                         position=labelloc,
                                         line_width=labelwidth,
                                         layer=self.layer_label)


        if frame==True:
            self.cell.add(box)
        if label==True:
            self.cell.add(label_grid_chip)
        
        
    def make_wafer(self,wafer_r,frame,label,labelloc,labelwidth):
        """
        Generate wafer with primary flat on the left. From https://coresix.com/products/wafers/ I estimated that the angle defining the wafer flat to arctan(flat/2 / radius)
        """
        angled = 18
        angle = angled*np.pi/180
        circ = cad.shapes.Circle((0,0), wafer_r, width=self.boxwidth, initial_angle=180+angled, final_angle=360+180-angled, layer=self.layer_box)
        flat = cad.core.Path([(-wafer_r*np.cos(angle),wafer_r*np.sin(angle)),(-wafer_r*np.cos(angle),-wafer_r*np.sin(angle))], width=self.boxwidth, layer=self.layer_box)

        date = time.strftime("%d/%m/%Y")
        if labelloc==(0,0):
                    labelloc=(-2e3,wafer_r-1e3)
        # The label is added 100 um on top of the main cell
        label_grid_chip = cad.shapes.LineLabel( self.name + "  " +\
                                         date,500,position=labelloc,
                                         line_width=labelwidth,
                                         layer=self.layer_label)


        if frame==True:
            self.cell.add(circ)
            self.cell.add(flat)
        if label==True:
            self.cell.add(label_grid_chip)


    def add_component(self,cell_obj, pos):
        """
        params cell_obj : cell object to add to maincell
        params pos : tuple of positions
        """
        if pos[0]> self.xdim/2 or pos[0]<-self.xdim/2:
            raise ValueError(" component lies out of layout") 

        if pos[1]> self.ydim/2 or pos[1]<-self.ydim/2:
            raise ValueError(" component lies out of layout") 

        self.cell.add(cell_obj,origin=pos)

    
    def add_ebpg_marker(self, pos=(-3310,-1560), size=20, spacing=200, number=4, duplicate=True):
        """
        4 ebeam marker each 20um rectangular and 200um spaced apart
        params pos : tuple of positions
        number: How many markers (up to four)
        duplicate: set of four groups or just one at this position
        """
        marker = [cad.core.Cell('EBEAM')] * 4
        x = [pos[0], pos[0] + spacing, pos[0] + spacing, pos[0]]
        y = [pos[1], pos[1], pos[1] + spacing, pos[1] + spacing]
        for i in range(number):
            box = cad.shapes.Rectangle((x[i]-size/2,y[i]-size/2),(x[i]+size/2,y[i]+size/2),
                                        layer = self.layer_alignment)
            marker[0].add(box)
        if duplicate==True:
            marker[1] = cad.core.CellReference(marker[0], origin=(-2*pos[0]-spacing,-2*pos[1]-spacing))
            marker[2] = cad.core.CellReference(marker[0], origin=(0,-2*pos[1]-spacing))
            marker[3] = cad.core.CellReference(marker[0], origin=(-2*pos[0]-spacing,0))
        self.cell.add(marker)


    def save_to_gds(self, loc = 'examples/', save = True, show = False):
        """
        Save and show gds file
        Default location in testing/, can be adjusted via loc
        """
        layout = cad.core.Layout('MAIN_CHIP')
        layout.add(self.cell)
        if save:
            layout.save(loc + self.name + '.gds')
        if show:
            layout.show()


    def add_bond_testpads(self, pos=(-2000,-2000), dim=(300,300), num=4):
        """
        value(num) bonding pads with dimension dim (tuple) at position pos (tuple)
        """
        pads = cad.core.Cell('TESTPADS')
        x = [pos[0], -pos[0], -pos[0], pos[0]]
        y = [pos[1], pos[1], -pos[1], -pos[1]]
        for i in range(num):
            box = cad.shapes.Rectangle((x[i]-dim[0]/2,y[i]-dim[1]/2),(x[i]+dim[0]/2,y[i]+dim[1]/2), layer = self.layer_testpads)
            pads.add(box)
        self.cell.add(pads)


    def add_photolitho_marker(self, pos=(0,0), layer=(1,2)):
        """
        Add alignment marker for photolithography
        """
        marker = cad.core.Cell('PHOTO')
        amarks0 = cad.templates.AlignmentMarks(('A','C'),layer)
        amarks = cad.core.CellReference(amarks0).translate(pos)
        marker.add(amarks)
        self.cell.add(amarks)
    
    
    def add_photolitho_vernier(self, pos=(-500,-500), layer=(1,2)):
        """
        Add vernier structures for determining alignment precision
        """
        verniers = cad.core.Cell('VERNIER')
        vmarks0 = cad.templates.Verniers(('A','B'),layer)
        vmarks = cad.core.CellReference(vmarks0).translate(pos)
        verniers.add(vmarks)
        self.cell.add(verniers)
        
        
    def add_dicing_marker(self, pos=(0,0), hor=True, vert=True, span=False, length=1000):
        """
        Add rectangular dicing marks across the entire chip/wafer
        """
        marker = cad.core.Cell('DICING')
        hmarks0 = cad.shapes.Rectangle((0,-125),(length,125))
        vmarks0 = cad.shapes.Rectangle((-125,0),(125,length))
        if span==False:
            x0 = -self.xdim/4
            x1 = -x0 + 1
            y0 = -self.ydim/4
            y1 = -y0 + 1
        else:
            x0 = span[0][0]/4
            x1 = span[0][1]/4
            y0 = span[1][0]/4
            y1 = span[1][1]/4
        for xx,yy in zip(np.arange(x0,x1,length),np.arange(y0,y1,length)):
            if hor==True:
                hmarks = cad.utils.translate(hmarks0, (2*xx+pos[0],pos[1]))
                marker.add(hmarks)
            if vert==True:
                vmarks = cad.utils.translate(vmarks0, (pos[0],2*yy+pos[1]))
                marker.add(vmarks)

        self.cell.add(marker)
    '''           
    def chip_not(self):
        """
        *** BROKEN
        Negate everything on this chip
        """
        #n_box = cad.core.Cell('NOT')
        #not_box = cad.core.CellReference(n_box)
        box = gdspy.Rectangle((-self.xdim/2, -self.ydim/2), (self.xdim/2, self.ydim/2))
        #not_box.add(box)
        original = cad.core.CellReference(self.cell)
        not_chip = gdspy.fast_boolean(box, original, 'not')
        result_cell = gdspy.Cell('NOT_CELL')
        result_cell.add(not_chip)
        self.cell = result_cell
    '''
       
    def add_TUlogo(self, pos=(0,100)):
        """
        *** BROKEN
        Issue with dxfImport
        """
        # logo is added 100um below bottom edge of chip
        logo = cad.core.DxfImport('examples/cad_files/TU_Delft_logo_Black.dxf',scale=1.0)
        #logo.layer=self.layer_label
        self.cell.add(logo)
    
