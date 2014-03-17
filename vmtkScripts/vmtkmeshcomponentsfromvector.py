#!/usr/bin/env python

## Program:   VMTK
## Module:    $RCSfile: vmtkmeshcomponentsfromvector.py,v $
## Language:  Python
## Date:      $Date: 2014/02/20 09:49:59 $
## Version:   $Revision: 1.6 $
## Author:    Adrien Lefieux

##   Copyright (c) Luca Antiga, David Steinman. All rights reserved.
##   See LICENCE file for details.

##      This software is distributed WITHOUT ANY WARRANTY; without even 
##      the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR 
##      PURPOSE.  See the above copyright notices for more information.

import vtk
import sys

import pypes

vmtkmeshcomponentsfromvector = 'vmtkMeshComponentsFromVector'

class vmtkMeshComponentsFromVector(pypes.pypeScript):

    def __init__(self):

        pypes.pypeScript.__init__(self)

        self.Mesh = None

        self.VectorArrayName = 'velocity'
        self.ComponentsArrayNames = 'u v w'

        self.RemoveVectorArray = False

        self.SetScriptName('vmtkmeshcomponentsfromvector')
        self.SetScriptDoc('create components array from one vector array')
        self.SetInputMembers([
            ['Mesh','i','vtkUnstructuredGrid',1,'','the input mesh','vmtkmeshreader'],
            ['VectorArrayName','vector','str',1,'',''],
            ['ComponentsArrayNames','components','str',-1,'',''],
            ['RemoveVectorArray','removevector','bool',1,'','']
            ])
        self.SetOutputMembers([
            ['Mesh','o','vtkUnstructuredGrid',1,'','the output mesh','vmtkmeshwriter']
            ])

    def Execute(self):

        if (self.Mesh == None):
            self.PrintError('Error: no Mesh.')

        numberOfComponents = 3

        vel = self.Mesh.GetPointData().GetArray(self.VectorArrayName)

        for i in range(numberOfComponents):
            vectorArray = vtk.vtkDoubleArray()
            vectorArray.SetName(self.ComponentsArrayNames.split(' ')[i])
            vectorArray.SetNumberOfComponents(1)
            vectorArray.SetNumberOfTuples(self.Mesh.GetNumberOfPoints())
            vectorArray.CopyComponent(0,vel,i)
            self.Mesh.GetPointData().AddArray(vectorArray)
            if self.RemoveVectorArray:
                self.Mesh.GetPointData().RemoveArray(self.VectorArrayName)

if __name__=='__main__':
    main = pypes.pypeMain()
    main.Arguments = sys.argv
    main.Execute()
