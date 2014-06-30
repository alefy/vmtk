#!/usr/bin/env python

## Program:   VMTK
## Module:    $RCSfile: vmtkmeshmergetimesteps.py,v $
## Language:  Python
## Date:      $Date: 2013/07/15 12:59:27 $
## Version:   $Revision: 1.6 $

##   Copyright (c) Luca Antiga, David Steinman. All rights reserved.
##   See LICENCE file for details.

##      This software is distributed WITHOUT ANY WARRANTY; without even 
##      the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR 
##      PURPOSE.  See the above copyright notices for more information.

## Note: this class was contributed by 
##       Simone Manini
##       Orobix Srl

import vtk
import sys
import os
    
import vtkvmtk
import vmtkmeshreader
import vmtkmeshvectorfromcomponents
import vmtkmeshcomponentsfromvector
import pypes

vmtkmeshmergetimesteps = 'vmtkMeshMergeTimesteps'

class vmtkMeshMergeTimesteps(pypes.pypeScript):

    def __init__(self):

        pypes.pypeScript.__init__(self)

        self.Mesh = None
        self.InputDirectoryName = None
        self.Pattern = None
        self.FirstTimeStep = None
        self.LastTimeStep = None
        self.IntervalTimeStep = 1
        self.VelocityVector = 0
        self.VelocityFromVector = 0
        self.VectorArrayName = 'velocity'
        self.Pressure = 0
        self.PressureArrayName = 'p'
        self.Wsr = 0
        self.VelocityComponentsArrayNames = 'u v w'
        self.WsrComponentsArrayNames = 'taux tauy tauz'
        self.WsrVector = 0
        self.SetScriptName('vmtkmeshmergetimesteps')
        self.SetScriptDoc('merge multiple mesh files with different timesteps into one')
        
        self.SetInputMembers([
            ['InputDirectoryName','directory','str',1,''],
            ['Pattern','pattern','str',1,''],
            ['FirstTimeStep','firststep','int',1,'(0,)'],
            ['LastTimeStep','laststep','int',1,'(0,)'],
            ['IntervalTimeStep','intervalstep','int',1,'(0,)'],
            ['VelocityComponentsArrayNames','components','str',-1,'',''],
            ['VelocityVector','velocityvector','bool',1,'','velocity vector instead of components'],
            ['VelocityFromVector','velocityfromvector','bool',1,'','Import velocity from velocity vector'],
            ['VectorArrayName','vectorarrayname','str',1,'','name of the velocity vector'],
            ['Pressure','pressure','bool',1,'','pressure array'],
            ['PressureArrayName','pressurearrayname','str',1,'','name of the pressure array'],
            ['Wsr','wallshearrate','bool',1,'','wallshearrate array'],
            ['WsrComponentsArrayNames','components','str',-1,'',''],
            ['WsrVector','wsrvector','bool',1,'','wallshearrate vector instead of components'],
            ])
        self.SetOutputMembers([
            ['Mesh','o','vtkUnstructuredGrid',1,'','the output mesh','vmtkmeshwriter']
            ])

    def Execute(self):

        if (self.InputDirectoryName == None):
            self.PrintError('Error: no directory.')

        if (self.Pattern == None):
            self.PrintError('Error: no pattern.')
        
        if (self.FirstTimeStep == None):
            self.PrintError('Error: no first timestep.')
        
        if (self.LastTimeStep == None):
            self.PrintError('Error: no last timestep.')
        
        if (self.VelocityComponentsArrayNames == None):
            self.PrintError('Error: no VelocityComponentsArrayNames.')
            
        for root, dirs, files in os.walk(self.InputDirectoryName):
            if root == self.InputDirectoryName:
                fileList = [x for x in files if not (x.startswith('.'))]
        
        timeIndexList = range(self.FirstTimeStep,self.LastTimeStep+1,self.IntervalTimeStep)
        reader = vmtkmeshreader.vmtkMeshReader()
        if self.VelocityVector or self.WsrVector:
            vectorFromComponents = vmtkmeshvectorfromcomponents.vmtkMeshVectorFromComponents()
        
        u_name = self.VelocityComponentsArrayNames.split(' ')[0]
        v_name = self.VelocityComponentsArrayNames.split(' ')[1]
        w_name = self.VelocityComponentsArrayNames.split(' ')[2]
        
        if self.Wsr:
            taux_name = self.WsrComponentsArrayNames.split(' ')[0]
            tauy_name = self.WsrComponentsArrayNames.split(' ')[1]
            tauz_name = self.WsrComponentsArrayNames.split(' ')[2]
        
        field = vtk.vtkFieldData()
        field.AllocateArrays(1)
        timesteps = vtk.vtkIntArray()
        timesteps.SetNumberOfComponents(1)
        timesteps.SetName("timesteps")
        i = 0
        for step in timeIndexList:
            print step
            if (self.Pattern%step).replace(' ','0') in fileList:
                timesteps.InsertTuple1(i, step)
                i+=1
                
                fileName = (self.Pattern%step).replace(' ','0')
                print fileName
                timeIndex = step
                reader.InputFileName = os.path.abspath(os.path.join(self.InputDirectoryName,fileName))
                reader.Execute()
                mesh = reader.Mesh

                if step == self.FirstTimeStep:
                    mesh.CopyStructure(mesh)
                    self.Mesh = mesh

                if self.Pressure:
                    p = mesh.GetPointData().GetArray(self.PressureArrayName)
                    p.SetName(self.PressureArrayName+str(step))
                    self.Mesh.GetPointData().AddArray(p)
                
                if self.Wsr:
                    taux = mesh.GetPointData().GetArray(taux_name)
                    taux.SetName(taux_name+str(step))
                    self.Mesh.GetPointData().AddArray(taux)
                    
                    tauy = mesh.GetPointData().GetArray(tauy_name)
                    tauy.SetName(tauy_name+str(step))
                    self.Mesh.GetPointData().AddArray(tauy)
                    
                    tauz = mesh.GetPointData().GetArray(tauz_name)
                    tauz.SetName(tauz_name+str(step))
                    self.Mesh.GetPointData().AddArray(tauz)

                if self.VelocityFromVector:
                    u_comp_name = u_name+"_"+str(step)
                    v_comp_name = v_name+"_"+str(step)
                    w_comp_name = w_name+"_"+str(step)
                    comp_name = [u_comp_name,v_comp_name,w_comp_name]

                    vel = mesh.GetPointData().GetArray(self.VectorArrayName)

                    numberOfComponents = 3

                    for i in range(numberOfComponents):
                        vectorArray = vtk.vtkDoubleArray()
                        vectorArray.SetName(comp_name[i])
                        vectorArray.SetNumberOfComponents(1)
                        vectorArray.SetNumberOfTuples(self.Mesh.GetNumberOfPoints())
                        vectorArray.CopyComponent(0,vel,i)
                        self.Mesh.GetPointData().AddArray(vectorArray)
                                                    
                else:
                    u = mesh.GetPointData().GetArray(u_name)
                    u.SetName(u_name+"_"+str(step))
                    self.Mesh.GetPointData().AddArray(u)

                    v = mesh.GetPointData().GetArray(v_name)
                    v.SetName(v_name+"_"+str(step))
                    self.Mesh.GetPointData().AddArray(v)
                
                    w = mesh.GetPointData().GetArray(w_name)
                    w.SetName(w_name+"_"+str(step))
                    self.Mesh.GetPointData().AddArray(w)

                if self.VelocityVector:
                    vectorFromComponents.Mesh = self.Mesh
                    vectorFromComponents.VectorArrayName = "Velocity_"+str(step)
                    vectorFromComponents.ComponentsArrayNames = [u.GetName(),v.GetName(),w.GetName()]
                    vectorFromComponents.RemoveComponentArrays = True
                    vectorfromcomponents.Execute()
                
                if self.WsrVector:
                    vectorFromComponents.Mesh = self.Mesh
                    vectorFromComponents.VectorArrayName = "Wsr_"+str(step)
                    vectorFromComponents.ComponentsArrayNames = [taux.GetName(),tauy.GetName(),tauz.GetName()]
                    vectorFromComponents.RemoveComponentArrays = True
                    vectorFromComponents.Execute()
    
        field.AddArray(timesteps)
        self.Mesh.SetFieldData(field)
                 
if __name__=='__main__':
    main = pypes.pypeMain()
    main.Arguments = sys.argv
    main.Execute()
