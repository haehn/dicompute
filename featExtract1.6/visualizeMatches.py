#!/usr/bin/env python

import vtk
import sys


# Function definition is here
def make_vtk_model( filename_input, filename_output ):
        count = 0
        scale = []
        color = []
        points = []
        r_prev = [0,0,0,0]
        with open(filename_input) as f:
                for line in f:
                        r = line.split('\t')
                        print line + "\n"
                        while len(r) > 5:
                                try:
                                        val = float(r[0] )
                                        print "value: " + str(val)
                                        break
                                except ValueError:
                                        print "no good: " + r[0]
                                        del r[0]
                                        print "removed: " + r[0]
                                        
                        if len(r) > 5:
                                if r[1]<>r_prev[1] and r[2]<>r_prev[2] and r[0]<>r_prev[0]: 
                                        count = count + 1
                                scale.append( float(r[3]) )
                                color.append( count ) # this could be disease status, etc
                                points.append( [float(r[0]),float(r[1]),float(r[2])] )
                                r_prev = r
	"""
	this is multi line comment in python

	
	print "abc"
	"""

        print "Items read:", len( scale )


        # output objects
        outpd = vtk.vtkPolyData()
        outpoints = vtk.vtkPoints()
        outpointdata = outpd.GetPointData()

        out_array = vtk.vtkFloatArray()
        out_array.SetNumberOfComponents(1)
        out_array.SetName('ScaleFactor')
        print "Point data array created:", out_array.GetName(), out_array.GetNumberOfComponents()

        outpointdata.AddArray(out_array)
        # active array will cause scaling in glyph 3D
        outpointdata.SetActiveScalars('ScaleFactor')

        out_array2 = vtk.vtkFloatArray()
        out_array2.SetNumberOfComponents(1)
        out_array2.SetName('Color')
        print "Point data array created:", out_array2.GetName(), out_array2.GetNumberOfComponents()
        outpointdata.AddArray(out_array2)

        # fill in some data
        for s, p, c in zip(scale, points, color):
            out_array.InsertNextValue(s)
            out_array2.InsertNextValue(c)
            idx = outpoints.InsertNextPoint(p)
            print "Inserted value", out_array.GetValue(idx), out_array.GetTuple(idx), "at:", outpoints.GetPoint(idx)

        outpd.SetPoints(outpoints)

        # save it as visible spheres
        source1 = vtk.vtkSphereSource()
        source1.SetRadius(1)
        source1.Update()
        #source2 = vtk.vtkSphereSource()
        #source2.SetRadius(1.2)
        #source2.Update()
        appender = vtk.vtkAppendPolyData()
        appender.AddInputData(source1.GetOutput())
        #appender.AddInputData(source2.GetOutput())
        appender.Update()

        glyph = vtk.vtkGlyph3D()
        glyph.ScalingOn()
        glyph.SetInputData(outpd)

        glyph.SetSourceConnection(0, appender.GetOutputPort())
        glyph.Update()

        writer = vtk.vtkPolyDataWriter()
        writer.SetInputData(glyph.GetOutput())

        writer.SetFileName(filename_output)
        writer.Write()

        return;



# look here for various sources and their documentation
# http://www.vtk.org/doc/nightly/html/classvtkPolyDataAlgorithm.html
# geometry = "nested_sphere"

print 'Number of arguments:', len(sys.argv), 'arguments.'
print 'Argument List:', str(sys.argv)

if len(sys.argv) <> 2:
	print "Needs one argument, a keypoint file image.key with accompanying *.matches.img1.txt, .img2.txt,  etc."
        print "Set argument by\n"
        print "  >> sys.argv = ['image.key.matches.img1.txt']"
	exit()

filename_input  = sys.argv[1]

fname1 = sys.argv[1] + ".matches.img1.txt"
fname2 = sys.argv[1] + ".matches.img2.txt"

print 'IO: ', filename_input

make_vtk_model( sys.argv[1] + ".matches.img1.txt", sys.argv[1] + ".matches.img1.txt.vtk" )
make_vtk_model( sys.argv[1] + ".matches.img2.txt", sys.argv[1] + ".matches.img2.txt.vtk" )

