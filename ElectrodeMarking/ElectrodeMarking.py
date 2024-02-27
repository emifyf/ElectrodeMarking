import logging
import os,sys,io
from typing import Annotated, Optional
import json
import SimpleITK as sitk
import nibabel as nib
import numpy as np
import vtk,qt
import time
import slicer

from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
from slicer.parameterNodeWrapper import (
    parameterNodeWrapper,
    WithinRange,
)

from slicer import vtkMRMLScalarVolumeNode
from slicer import vtkMRMLMarkupsFiducialNode
from slicer import vtkMRMLMarkupsLineNode
from slicer import vtkMRMLSegmentationNode


#
# ElectrodeMarking sadasd
print("gatoooooo")
try:
    import nibabel as nib
    print("Nibabel library was imported y las otras")
    #Probando el commit en electrode marking rama maaster

except ModuleNotFoundError:
    if slicer.util.confirmOkCancelDisplay("This module requires 'nibabel, PyPDF2, reportlab' Python package. Click OK to install it now."):
        slicer.util.pip_install("nibabel")

import nibabel as nib






# slicer.app.pythonConsole().clear()   borrar consola python en slicer

rutaGuardado= os.path.join(os.path.dirname(__file__), 'Resources\\Files')
print(f"The files will be automatically saved in: {rutaGuardado}")

class ElectrodeMarking(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "Electrode Marking"  # TODO: make this more human readable by adding spaces
        self.parent.categories = ["SESP"]  # TODO: set categories (folders where the module shows up in the module selector)
        self.parent.dependencies = []  # TODO: add here list of module names that this module requires
        self.parent.contributors = ["Ferre y Ferre, Emiliano (UNAJ)","Dr. Ing. Collavini, Santiago (UNAJ)"]  # TODO: replace with "Firstname Lastname (Organization)"
        # TODO: update with short description of the module and a link to online module documentation
        self.parent.helpText = """Stereo Epilepsy Surgery Planning.
        <br><br>Mark your electrodes and model them, then adjust the current level with fiduciaries and plan your surgery. Module's information will be appear in Python Console
        
        <br><br> For reference please visit ...
        
        
        <br><br><br><br><br>
        """
       

        # TODO: replace with organization, grant and thanks
        self.parent.acknowledgementText = """
            Emiliano Ferre y Ferre developed this module for his final project of Bioengineering studies ​at UNAJ under the supervision and advice of PhD. Santiago Collavini.             
            
            
            <br><br><br><i>Icon by <a class="link_pro" href="https://freeicons.io/undefined/ai-robotics-brain-technology-artificial-intelligence-icon-442363">Artificial Intelligence icon set</a> on <a href="https://freeicons.io">freeicons.io</a></i>
            
            """
        # Additional initialization step after application startup is complete
        slicer.app.connect("startupCompleted()", registerSampleData)
        

#
# Register sample data sets in Sample Data module
#

def registerSampleData():
    """
    Add data sets to Sample Data module.
    """
    # It is always recommended to provide sample data for users to make it easy to try the module,
    # but if no sample data is available then this method (and associated startupCompeted signal connection) can be removed.

    import SampleData
    iconsPath = os.path.join(os.path.dirname(__file__), 'Resources/Icons')
    
    # To ensure that the source code repository remains small (can be downloaded and installed quickly)
    # it is recommended to store data sets that are larger than a few MB in a Github release.

    # ElectrodeMarking1
    SampleData.SampleDataLogic.registerCustomSampleDataSource(
        # Category and sample name displayed in Sample Data module
        category='ElectrodeMarking',
        sampleName='ElectrodeMarking',
        # Thumbnail should have size of approximately 260x280 pixels and stored in Resources/Icons folder.
        # It can be created by Screen Capture module, "Capture all views" option enabled, "Number of images" set to "Single".
        thumbnailFileName=os.path.join(iconsPath, 'ElectrodeMarking1.png'),
        # Download URL and target file name
        uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95",
        fileNames='ElectrodeMarking1.nrrd',
        # Checksum to ensure file integrity. Can be computed by this command:
        #  import hashlib; print(hashlib.sha256(open(filename, "rb").read()).hexdigest())
        checksums='SHA256:998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95',
        # This node name will be used when the data set is loaded
        nodeNames='ElectrodeMarking1'
        
    )

    # ElectrodeMarking2
    SampleData.SampleDataLogic.registerCustomSampleDataSource(
        # Category and sample name displayed in Sample Data module
        category='ElectrodeMarking',
        sampleName='ElectrodeMarking2',
        thumbnailFileName=os.path.join(iconsPath, 'ElectrodeMarking2.png'),
        # Download URL and target file name
        uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97",
        fileNames='ElectrodeMarking2.nrrd',
        checksums='SHA256:1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97',
        # This node name will be used when the data set is loaded
        nodeNames='ElectrodeMarking2'
    )


#
# ElectrodeMarkingParameterNode
#

@parameterNodeWrapper
class ElectrodeMarkingParameterNode:
    """
    The parameters needed by module.

    inputVolume - The volume to threshold.
    imageThreshold - The value at which to threshold the input volume.
    invertThreshold - If true, will invert the threshold.
    thresholdedVolume - The output volume that will contain the thresholded volume.
    invertedVolume - The output volume that will contain the inverted thresholded volume.
    """

    inputLine1: vtkMRMLMarkupsLineNode
    inputVolume4: vtkMRMLScalarVolumeNode #input threshold automatico
    inputFiducial1: vtkMRMLMarkupsFiducialNode #input modelizar
    inputSegmentation1: vtkMRMLMarkupsFiducialNode #input modelizar
    


#
# ElectrodeMarkingWidget
#

class ElectrodeMarkingWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent=None) -> None:
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.__init__(self, parent)
        VTKObservationMixin.__init__(self)  # needed for parameter node observation
        self.logic = None
        self._parameterNode = None
        self._parameterNodeGuiTag = None
        
        self.elec = 1
        self.rs=1
        self.eLibre=1
        
        self.listaFidus=[]

        self.contacto = 1
        self.plastico = 1

        # Obtener el nodo seleccionado en el árbol de jerarquía


        

    def setup(self) -> None:
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.setup(self)

        # Load widget from .ui file (created by Qt Designer).
        # Additional widgets can be instantiated manually and added to self.layout.
        uiWidget = slicer.util.loadUI(self.resourcePath('UI/ElectrodeMarking.ui'))
        self.layout.addWidget(uiWidget)
        self.ui = slicer.util.childWidgetVariables(uiWidget)

        # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
        # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
        # "setMRMLScene(vtkMRMLScene*)" slot.
        uiWidget.setMRMLScene(slicer.mrmlScene)

        # Create logic class. Logic implements all computations that should be possible to run
        # in batch mode, without a graphical user interface.
        self.logic = ElectrodeMarkingLogic()

        # Connections

        # These connections ensure that we update parameter node when scene is closed
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)

        # Buttons en desuso

        self.ui.rsButton.connect('clicked(bool)', self.onRsButton2)  #genera fiduciario o modelo RS segun funcion
        self.ui.mappingButton.connect('clicked(bool)',self.onMappingButton) #genera lineas
       
        #Acciones en uso
        self.ui.modelButton.connect('clicked(bool)',self.reformat_image) #aca   self.onModelButton2   -   val  #modeliza fiduciarios
        self.ui.elecModelButton.connect('clicked(bool)',self.onElecModelButton) #modeliza electrodos 
        self.ui.lineButton.connect('clicked(bool)',self.onLineButton) #genera lineas
        self.ui.fiduButton.connect('clicked(bool)', self.onFiduButton2)  #genera fiduciarios de diametro variable
        
        self.ui.zonaCerebralButton.connect('clicked(bool)',self.localizarZonaCerebral)
        self.ui.exportarButton.connect('clicked(bool)',self.exportarPDF)
        self.ui.spinBox.connect('valueChanged(int)', self.onSpinBoxChanged)


        electrodePath = os.path.join(os.path.dirname(__file__), 'Resources\\Electrodos\\electrodos.txt')


        with open(electrodePath, 'r') as file:
            lines = file.readlines()
        for line in lines:
            self.ui.listaElectrodos.addItem(line.strip())
        


        # Make sure parameter node is initialized (needed for module reload)
        self.initializeParameterNode()
        

    def cleanup(self) -> None:
        """
        Called when the application closes and the module widget is destroyed.
        """
        self.removeObservers()

    def enter(self) -> None:
        """
        Called each time the user opens this module.
        """
        # Make sure parameter node exists and observed
        self.initializeParameterNode()

    def exit(self) -> None:
        """
        Called each time the user opens a different module.
        """
        # Do not react to parameter node changes (GUI will be updated when the user enters into the module)


    def onSceneStartClose(self, caller, event) -> None:
        """
        Called just before the scene is closed.
        """
        # Parameter node will be reset, do not use it anymore
        self.setParameterNode(None)

    def onSceneEndClose(self, caller, event) -> None:
        """
        Called just after the scene is closed.
        """
        # If this module is shown while the scene is closed then recreate a new parameter node immediately
        if self.parent.isEntered:
            self.initializeParameterNode()

    def initializeParameterNode(self) -> None:
        """
        Ensure parameter node exists and observed.
        """
        # Parameter node stores all user choices in parameter values, node selections, etc.
        # so that when the scene is saved and reloaded, these settings are restored.

        self.setParameterNode(self.logic.getParameterNode())

 

    def setParameterNode(self, inputParameterNode: Optional[ElectrodeMarkingParameterNode]) -> None:
        """
        Set and observe parameter node.
        Observation is needed because when the parameter node is changed then the GUI must be updated immediately.
        """

        self._parameterNode = inputParameterNode
        if self._parameterNode:
            # Note: in the .ui file, a Qt dynamic property called "SlicerParameterName" is set on each
            # ui element that needs connection.
            self._parameterNodeGuiTag = self._parameterNode.connectGui(self.ui)
            
            self.addObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self._checkCanModel)
            self._checkCanModel()
            
            self.addObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self._checkCanElecModel)
            self._checkCanElecModel()            
                      

    def _checkCanModel(self, caller=None, event=None) -> None:
        if self._parameterNode and self._parameterNode.inputFiducial1:
            self.ui.modelButton.toolTip = "Compute output model"
            self.ui.modelButton.enabled = True
        else:
            self.ui.modelButton.toolTip = "Select input fiducial node"
            self.ui.modelButton.enabled = False
    def _checkCanElecModel(self, caller=None, event=None) -> None:
        if self._parameterNode and self._parameterNode.inputLine1:
            self.ui.elecModelButton.toolTip = "Compute output model"
            self.ui.elecModelButton.enabled = True
        else:
            self.ui.elecModelButton.toolTip = "Select input fiducial node"
            self.ui.elecModelButton.enabled = False           



    #Obsoleto
    def onRsButton(self):
        '''  markups_node = slicer.mrmlScene.GetFirstNodeByClass('vtkMRMLMarkupsFiducialNode')
        if not markups_node:
            markups_node = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsFiducialNode', 'nodoElectrodo')
        nombre_deseado = f'Elctrodo {self.i}'
        markups_node.SetName(nombre_deseado)            
            
            '''
        nombre_deseado = f'Electrodo RS {self.rs}'
        self.listaFidus.append(nombre_deseado)
        fiduNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsFiducialNode',nombre_deseado)
        # Establecer el nombre deseado para los fiduciarios
        
              
        slicer.util.getNode(nombre_deseado).GetDisplayNode().SetGlyphSize(15)
        slicer.util.getNode(nombre_deseado).GetDisplayNode().SetSelectedColor(0,1,0)
        # Configurar la clase de referencia para el modo de colocación
        selection_node = slicer.mrmlScene.GetNodeByID("vtkMRMLSelectionNodeSingleton")
        selection_node.SetReferenceActivePlaceNodeClassName("vtkMRMLMarkupsFiducialNode")

        # Configurar el modo de colocación y persistencia
        interaction_node = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
        place_mode_persistence = 1
        interaction_node.SetPlaceModePersistence(place_mode_persistence)
        interaction_node.SetCurrentInteractionMode(1)  # 1 corresponde al modo de colocación
        self.rs+=1   
   
   #Obsoleto
    def onRsButton2(self):
        indice=self.ui.listaElectrodos.currentIndex
        self.logic.modelizarRs(self.ui.markupSelector2.currentNode(),rutaGuardado,indice)


     
   #Obsoleto 
    def onMappingButton(self):
        
        indice=self.ui.listaElectrodos.currentIndex
        self.logic.modelizarMapping(self.ui.markupSelector2.currentNode(),rutaGuardado,indice)        
    
    # 
    def exportarPDF(self):
        self.logic.exportarPDF()
        
    def localizarZonaCerebral(self):
        self.logic.localizarZonaCerebralLogic()
  
  
   #Uso
    def onFiduButton2(self):

        nombre_deseado = f'E. Libre {self.eLibre}'
        self.listaFidus.append(nombre_deseado)
        fiduNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsFiducialNode',nombre_deseado)
        # Establecer el nombre deseado para los fiduciarios
              
        slicer.util.getNode(nombre_deseado).GetDisplayNode().SetGlyphSize(self.ui.SliderWidget.value)
        slicer.util.getNode(nombre_deseado).GetDisplayNode().SetSelectedColor(0,0,1)
        slicer.util.getNode(nombre_deseado).GetDisplayNode().SetOpacity(0.50)
        # Configurar la clase de referencia para el modo de colocación
        selection_node = slicer.mrmlScene.GetNodeByID("vtkMRMLSelectionNodeSingleton")
        selection_node.SetReferenceActivePlaceNodeClassName("vtkMRMLMarkupsFiducialNode")

        # Configurar el modo de colocación y persistencia
        interaction_node = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
        place_mode_persistence = 1
        interaction_node.SetPlaceModePersistence(place_mode_persistence)
        interaction_node.SetCurrentInteractionMode(1)  # 1 corresponde al modo de colocación
        self.eLibre+=1   
          
  
    
    #uso
    def onSpinBoxChanged(self,value):
        self.logic.cambioNumeroCarpeta(value)
     
    #uso
    def onLineButton(self):

       self.logic.agregarLineas() 
    
    #Uso 
    def onElecModelButton(self) -> None:
        '''
        dialogoSeleccionArchivo = qt.QFileDialog()
        dialogoSeleccionArchivo.setFileMode(qt.QFileDialog.Directory)
        dialogoSeleccionArchivo.setOption(qt.QFileDialog.ShowDirsOnly, True)

        # Mostrar el diálogo y obtener la ruta seleccionada
        if dialogoSeleccionArchivo.exec_() == qt.QFileDialog.Accepted:
            rutaArchivo = dialogoSeleccionArchivo.selectedFiles()[0]
            
            # Aquí puedes usar la ruta del archivo como desees
            print("Carpeta seleccionada:", rutaArchivo) 
        '''
 
            
        markupsNode=self.ui.markupSelector2.currentNode()
        indice=self.ui.listaElectrodos.currentIndex
        slicer.util.saveNode(markupsNode, f"{rutaGuardado}\\{markupsNode.GetName()}.json")
        time.sleep(1)       
        self.logic.modelizarElectrodo(self.ui.markupSelector2.currentNode(),rutaGuardado,indice)    
    
    #uso      
    
    
    def reformat_image(self):
        sliceNode = slicer.app.layoutManager().sliceWidget("Red").mrmlSliceNode()
        sliceToRas = sliceNode.GetSliceToRAS()
        transform=vtk.vtkTransform()
        transform.SetMatrix(sliceToRas)
        transform.RotateWXYZ()
        transform.RotateY(15)
        transform.RotateZ(20)
        sliceToRas.DeepCopy(transform.GetMatrix())
        sliceNode.UpdateMatrices()
        pass  
    def onModelButton2(self):
        
        '''
        dialogoSeleccionArchivo = qt.QFileDialog()
        dialogoSeleccionArchivo.setFileMode(qt.QFileDialog.Directory)
        dialogoSeleccionArchivo.setOption(qt.QFileDialog.ShowDirsOnly, True)

        # Mostrar el diálogo y obtener la ruta seleccionada
        if dialogoSeleccionArchivo.exec_() == qt.QFileDialog.Accepted:
            rutaArchivo = dialogoSeleccionArchivo.selectedFiles()[0]
            
            # Aquí puedes usar la ruta del archivo como desees
            print("Carpeta seleccionada:", rutaArchivo) 
        '''    
        
        
        #markupsNode = slicer.util.getNode('Electrodo 1')
        markupsNode=self.ui.markupSelector1.currentNode()
        
        #slicer.util.saveNode(markupsNode, f"{rutaArchivo}\\{markupsNode.GetName()}.json")
        slicer.util.saveNode(markupsNode, f"{rutaGuardado}\\{markupsNode.GetName()}.json")
        time.sleep(1)
        #self.logic.modelizar_mm()
        #ACA ABAJO BA MODELIZAR_´PX
        self.logic.modelizar_px(self.ui.markupSelector1.currentNode(),rutaGuardado)
        print("---------------------------")        
        
        
        
        #################################################

# Actualizar la vista
#
# ElectrodeMarkingLogic
#

class ElectrodeMarkingLogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual
    computation done by your module.  The interface
    should be such that other python code can import
    this class and make use of the functionality without
    requiring an instance of the Widget.
    Uses ScriptedLoadableModuleLogic base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self) -> None:
        """
        Called when the logic class is instantiated. Can be used for initializing member variables.
        """
        ScriptedLoadableModuleLogic.__init__(self)
        self.carpeta=1
        self.elec=1
        self.listaFidus=[]
        self.datosFiduciarios=[]
        
    def getParameterNode(self):
        return ElectrodeMarkingParameterNode(super().getParameterNode())

    def getTransformation(self,markup: vtkMRMLMarkupsFiducialNode, rutaArchivo,nombreTransformacion,nroComponente):
        
        with open(f'{rutaArchivo}\\{markup.GetName()}.json', 'r') as file:
            data = json.load(file)
            centros = data

        fiduciarios=centros["markups"][0]["controlPoints"]
        diametro=centros["markups"][0]["display"]["glyphSize"]
        
        listaCentros=[]
        for pepe in range(0,len(fiduciarios)):
            listaCentros.append(fiduciarios[pepe]["position"])
       
     
        # Puntos en el espacio
        point1 = np.array([-listaCentros[0][0],-listaCentros[0][1],listaCentros[0][2]])
        point2 = np.array([-listaCentros[1][0],-listaCentros[1][1],listaCentros[1][2]])
       
       # Calcular la dirección y la distancia entre los dos puntos  
        direccion = point2 - point1
        distancia = np.linalg.norm(direccion)

        # Normalizar la dirección para obtener el vector unitario
        direccion_unitaria = direccion / distancia
        
        # Calcular el ángulo de rotación en grados
        angulo_rotacion = np.degrees(np.arccos(direccion_unitaria[2]))

        # Calcular el eje de rotación como el producto cruz entre el vector unitario y el eje Z
        eje_rotacion = np.cross([0,0, 1], direccion_unitaria)

        # Crear la transformación
        transform = vtk.vtkTransform()
        transform.Translate(point1)
        transform.RotateWXYZ(angulo_rotacion, eje_rotacion)

        # Obtener el nodo de transformación en 3D Slicer
        transformNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLLinearTransformNode')
        transformNode.SetName(f'Transformacion{nombreTransformacion} {nroComponente}')

        
        # Establecer la transformación en el nodo de transformación
        transformNode.SetMatrixTransformToParent(transform.GetMatrix())
        
        
        #prueba cambio angulo vista rojo
        # Definir la matriz de rotación (por ejemplo, rotación en el eje z)
        # cos_theta = np.cos(angulo_rotacion)
        # sin_theta = np.sin(angulo_rotacion)
        
        # rotation_matrix = np.array([[cos_theta, sin_theta, 0],
        #                             [-sin_theta, cos_theta, 0],
        #                             [0, 0, 1]])
            
        # rotated_coordinatesZ = np.dot(rotation_matrix, eje_rotacion)


        # rotation_matrix = np.array([[cos_theta, 0,sin_theta],
        #                             [0, 1, 0],
        #                             [-sin_theta, 0,cos_theta]])
      
        # rotated_coordinatesI = np.dot(rotation_matrix, eje_rotacion)

        # rotation_matrix = np.array([[1, 0, 0],
        #                             [0,cos_theta,sin_theta],
        #                             [0,-sin_theta,cos_theta]])
            
        # rotated_coordinatesX = np.dot(rotation_matrix, eje_rotacion)
        
        # print(f"pepito {eje_rotacion}")
        
        
        # #prueba cambio angulo vista rojo

        # sliceNode = slicer.app.layoutManager().sliceWidget("Red").mrmlSliceNode()
        # sliceToRas = sliceNode.GetSliceToRAS()
        # transformPrueba=vtk.vtkTransform()
        # transformPrueba.Translate(point1)
        # transformPrueba.RotateWXYZ(angulo_rotacion, rotated_coordinatesI)

        # sliceToRas.DeepCopy(transformPrueba.GetMatrix())
        # sliceNode.UpdateMatrices()
        
        
        # sliceNode2 = slicer.app.layoutManager().sliceWidget("Green").mrmlSliceNode()
        # sliceToRas2 = sliceNode2.GetSliceToRAS()
        # transformPrueba2=vtk.vtkTransform()
        # transformPrueba2.Translate(point1)
        # transformPrueba.RotateX( rotated_coordinatesX[0])
        # transformPrueba.RotateY( rotated_coordinatesX[1])
        # transformPrueba.RotateZ( rotated_coordinatesX[2])
        # sliceToRas2.DeepCopy(transformPrueba2.GetMatrix())
        # sliceNode2.UpdateMatrices()
        
        
        # sliceNode3 = slicer.app.layoutManager().sliceWidget("Yellow").mrmlSliceNode()
        # sliceToRas3 = sliceNode3.GetSliceToRAS()
        # transformPrueba3=vtk.vtkTransform()
        # transformPrueba3.Translate(point1)
        # transformPrueba3.RotateWXYZ(angulo_rotacion, rotated_coordinatesI)
        # sliceToRas3.DeepCopy(transformPrueba3.GetMatrix())
        # sliceNode3.UpdateMatrices()
        
        sliceNode = slicer.app.layoutManager().sliceWidget("Red").mrmlSliceNode()
        sliceToRas = sliceNode.GetSliceToRAS()
        transformPrueba=vtk.vtkTransform()
        '''transformPrueba.Translate(point1)
        transformPrueba.SetMatrix(sliceToRas)'''
        transformPrueba.Translate(point1)
        
        angulo_rotacion2=angulo_rotacion
        angulo_rotacion3=angulo_rotacion

        angulo_rotacion+=90
        transformPrueba.RotateWXYZ(angulo_rotacion, eje_rotacion)
        transformPrueba.RotateZ( angulo_rotacion2)
        sliceToRas.DeepCopy(transformPrueba.GetMatrix())
        print(sliceToRas)
        sliceNode.UpdateMatrices()


        sliceNode2 = slicer.app.layoutManager().sliceWidget("Green").mrmlSliceNode()
        sliceToRas2 = sliceNode2.GetSliceToRAS()
        transformPrueba2=vtk.vtkTransform()
        '''transformPrueba.Translate(point1)
        transformPrueba.SetMatrix(sliceToRas)'''
        transformPrueba2.Translate(point1)
        transformPrueba2.RotateZ( angulo_rotacion2)
        sliceToRas2.DeepCopy(transformPrueba2.GetMatrix())
        print(sliceToRas2)
        sliceNode2.UpdateMatrices()
        
        
        sliceNode3 = slicer.app.layoutManager().sliceWidget("Yellow").mrmlSliceNode()
        sliceToRas3 = sliceNode3.GetSliceToRAS()
        transformPrueba3=vtk.vtkTransform()
        '''transformPrueba.Translate(point1)
        transformPrueba.SetMatrix(sliceToRas)'''
        transformPrueba3.Translate(point1)
        transformPrueba3.RotateY( angulo_rotacion3)
        sliceToRas2.DeepCopy(transformPrueba3.GetMatrix())
        print(sliceToRas3)
        sliceNode3.UpdateMatrices()
        ####
        
        
        
        
        
        
        return transformNode
    
    
    #obtiene imagenes para el pdf
    #Uso
    def createImages(self):
        import ScreenCapture
       
        capturasPath = os.path.join(os.path.dirname(__file__), 'Resources\\Capturas')
        # Obtener las posiciones de los fiduciarios activos en la vista 
        fiducialNodes = slicer.util.getNodesByClass('vtkMRMLMarkupsFiducialNode')
        activeFiducials = [node for node in fiducialNodes if node.GetDisplayVisibility()]
        fiducialPositions = [node.GetNthControlPointPosition(i) for node in activeFiducials for i in range(node.GetNumberOfControlPoints())]

        # Ordenar las posiciones según la coordenada Z (profundidad)
        #fiducialPositions.sort(key=lambda pos: pos[2])
        print('los fiduposition son', fiducialPositions)
        
        sliceWidgetColors = ['Yellow','Green','Red']
        for node in activeFiducials:
            node.SetDisplayVisibility(False)
            
        #ubicamos los fiduciarios y sacamos foto
        layoutManager = slicer.app.layoutManager()
       
        for i,(fidu,node) in enumerate(zip(fiducialPositions,activeFiducials),start=1):
            node.SetDisplayVisibility(True)
            
            cYellow, cGreen, cRed =fidu
            for color in sliceWidgetColors:
                sliceWidget = layoutManager.sliceWidget(color)
                sliceWidgetLogic = sliceWidget.sliceLogic()
                sliceNode = sliceWidgetLogic.GetSliceNode()
                sliceNode.JumpSlice(cYellow,cGreen,cRed)

                cap = ScreenCapture.ScreenCaptureLogic()
                cap.showViewControllers(False)
                cap.captureImageFromView(None, f"{capturasPath}\\test{i}.png")
                cap.showViewControllers(True)
            node.SetDisplayVisibility(False)
        
        for node in activeFiducials:
            node.SetDisplayVisibility(True)
       
    #estructura del pdf
    #Uso        
    def getPDF2(self,datosFiduciarios):
        membretePath = os.path.join(os.path.dirname(__file__), 'Resources\\PlantillaPDF\\membrete.jpg')
        reportePdfPath=os.path.join(rutaGuardado,"reporte.pdf")
        capturasPath = os.path.join(os.path.dirname(__file__), 'Resources\\Capturas')
        
        slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpView)
        printer = qt.QPrinter(qt.QPrinter.PrinterResolution)
        printer.setOutputFormat(qt.QPrinter.PdfFormat)
        printer.setPaperSize(qt.QPrinter.A4)
        printer.setOutputFileName(reportePdfPath)

        
        doc = qt.QTextDocument()
        _html = f"""
                <head>
                
                <title>Report</title>
                <style>
                    .page {{
                        page-break-before: always;
                        height: 297mm; /* Altura para tamaño A4 en milímetros */
                        width: 210mm; /* Ancho para tamaño A4 en milímetros */
                        margin: 0; /* Eliminar márgenes predeterminados */
                    }}

                </style>
                </head>  
                <body>
                <div style="text-align: center;">
                    <img src="{membretePath}" width="450"/>
                    <h1>Stereo Epilepsy Surgical Planinng</h1>
                </div>
                
                <br>
                <h2>Electrode Marking</h2>
                <table>
                <tr>
                <td>Patient last name:</td>
                <td></td>
                </tr>
                <tr>
                <td>Patient first name:</td>
                <td></td>
                </tr>
                <tr>
                <td>Date of birth:</td>
                <td></td>
                </tr>
                <tr>
                <td>Date of examination:</td>
                <td></td>
                
                </tr>
                </table>
            
                """
        
        self.createImages()
        
        archivos_en_carpeta = os.listdir(capturasPath)
        
        # Filtrar solo los archivos de imagen (puedes ajustar esto según los tipos de archivos que tengas)
        archivos_imagen = [archivo for archivo in archivos_en_carpeta if archivo.endswith(('.png', '.jpg', '.jpeg'))]
        for nombre in archivos_imagen:
            print(nombre)
        
        j=2
        aux=1
        for i,(nombre,datos) in enumerate(zip(archivos_imagen,datosFiduciarios), start=1):
            numeroElectrodo=""

            if i%2!=0:
                _html+=f"""
                    <div id="page{j}" class="page" style="height: 297mm; width: 210mm; page-break-before: always;">
                        <div height= 8% style="text-align: center;">
                        <img src="{membretePath}" width="450"/>
                    </div>
                    
                    """
            if datos[0].startswith("1"):
                numeroElectrodo="Electrodo 1"
            elif datos[0].startswith("2"):
                numeroElectrodo="Electrodo 2"
            elif datos[0].startswith("3"):
                numeroElectrodo="Electrodo 3"
            elif datos[0].startswith("4"):
                numeroElectrodo="Electrodo 4"
            elif datos[0].startswith("5"):
                numeroElectrodo="Electrodo 5"                                
            elif datos[0].startswith("6"):
                numeroElectrodo="Electrodo 6"
            elif datos[0].startswith("7"):
                numeroElectrodo="Electrodo 7"
            elif datos[0].startswith("8"):
                numeroElectrodo="Electrodo 8"                
            elif datos[0].startswith("9"):
                numeroElectrodo="Electrodo 9"
            elif datos[0].startswith("10"):
                numeroElectrodo="Electrodo 10"
            elif datos[0].startswith("11"):
                numeroElectrodo="Electrodo 11"
            elif datos[0].startswith("12"):
                numeroElectrodo="Electrodo 12"
            elif datos[0].startswith("13"):
                numeroElectrodo="Electrodo 13"
            elif datos[0].startswith("14"):
                numeroElectrodo="Electrodo 14"                                                                                                
                        
            _html+=f"""
                    <div height=40% style="text-align: center;">
                        <h6>{numeroElectrodo}</h6>
                        <br>
                        <img src="{capturasPath}/test{i}.png" width="500" />
                        <div style="text-align: left;">
                        <br>
                        Nombre en escena: {datos[0]} Referencia anatómica: {datos[1]} 
                        <br> 
                        Coordenada R:{round(datos[2],4)} Coordenada A:{round(datos[3],4)} Coordenada S:{round(datos[4],4)}
                        <br>
                    </div>    
                    </div> 
      
            """
            j+=1    
           
           
           
            
        doc.setHtml(_html)
        doc.setPageSize(qt.QSizeF(printer.pageRect().size()))  # hide the page number
        doc.print(printer)

        # Abrir el informe en el visor de PDF de 3D Slicer
        logging.info("Starting '"+reportePdfPath+"' ...")
        #slash/backlash replacements because of active directory
        
          
        print(f"Nuevo documento generado en: {rutaGuardado}")
        for archivo in archivos_imagen:
            ruta_completa = os.path.join(capturasPath, archivo)
            os.remove(ruta_completa)
            print(f"Capturas temporales eliminada: {ruta_completa}")

        self.datosFiduciarios=[]
        
    #Obtengo el valor en el punto apr asociar la zona cerebral
    #En uso
    def indices(self,imagen_wmparc,datos_wmparc,puntoRs):
        orientacion = imagen_wmparc.affine[:3, :3]  # Obtener la matriz de orientación
        indices_imagen = np.linalg.inv(orientacion).dot(np.subtract(puntoRs, imagen_wmparc.affine[:3, 3])) / [1,1,1]
        #print(f"Coordenadas en términos de índices de la imagen: {indices_imagen}")
        # Redondear a enteros para obtener los índices de píxeles o voxels
        indices_imagen_enteros = np.round(indices_imagen).astype(int)
        valor_en_punto = datos_wmparc[indices_imagen_enteros[0], indices_imagen_enteros[1], indices_imagen_enteros[2]]
        return valor_en_punto
    #Obtengo la zona cerebral segun freesurfer color lut
    #En uso
    def zonaCerebral(self,archivo_aseg_label,datos_wmparc,valorDelPunto,node):
                
        # Leer el archivo aseg.label
        with open(archivo_aseg_label, 'r') as file:
            lines = file.readlines()
        mapeo_valores = {}

        # Procesar las líneas del archivo
        for line in lines:
            # Ignorar líneas que comienzan con '#' (comentarios)
            if not line.startswith('#'):
                # Dividir la línea en columnas
                columns = line.split()

                # Verificar que haya al menos dos columnas
                if len(columns) >= 2:
                    # Obtener el valor y el significado
                    valor = int(columns[0])
                    significado = ' '.join(columns[1:-4])

                    # Agregar al diccionario
                    mapeo_valores[valor] = significado
                else:
                    pass
                    #print(f"Advertencia: La línea no tiene suficientes columnas: {line}")


        # Obtener valores únicos y sus conteos
        valores_unicos, conteos = np.unique(datos_wmparc, return_counts=True)


        # Imprimir los resultados y el total de píxeles en la imagen
        total_pixeles_imagen = np.sum(conteos)
        #print(f"Total de voxels en la imagen: {total_pixeles_imagen}")

        significado = mapeo_valores.get(valor, "Desconocido")


        # Imprimir los resultados
        for valor, conteo in zip(valores_unicos, conteos):
            significado = mapeo_valores.get(valor, "Desconocido")
            
            #print(f"Valor: {valor}, Significado: {significado}, Cantidad de Voxels: {conteo}")
        significado = mapeo_valores.get(valorDelPunto, "Desconocido")
        print(f"El centro del RS se encuentra ubicado en la zona {significado}\n")
        node.SetName(f"{significado}")
        return significado

    #localiza zona cerebral
    #Uso
    def localizarZonaCerebralLogic(self):
                    # Obtener todos los nodos fiduciarios en la escena
        fiducial_nodes = slicer.util.getNodesByClass('vtkMRMLMarkupsFiducialNode')
        # Ruta al archivo wmparc.nii.gz
        
        dialogoSeleccionArchivo = qt.QFileDialog()
        dialogoSeleccionArchivo.setFileMode(qt.QFileDialog.ExistingFile)
        dialogoSeleccionArchivo.setNameFilter("Volumen (*.mgz);;Volumen (*.nii)")  # Filtros de extensión

        dialogoSeleccionArchivo.setOption(qt.QFileDialog.ShowDirsOnly, True)

        # Mostrar el diálogo y obtener la ruta seleccionada
        if dialogoSeleccionArchivo.exec_() == qt.QFileDialog.Accepted:
            rutaArchivo = dialogoSeleccionArchivo.selectedFiles()[0]
            
            # Aquí puedes usar la ruta del archivo como desees
            print(f"Ruta del volumen seleccionadao {rutaArchivo}\n") 

        # Obtiene la ruta del archivo seleccionado
        archivo_wmparc = rutaArchivo
     
        # Ruta al archivo codificacion de colores
        labelPath = os.path.join(os.path.dirname(__file__), 'Resources\\FreeSurfer\\labels.txt')
        archivo_aseg_label = labelPath
        imagen_wmparc = nib.load(archivo_wmparc)
        datos_wmparc = imagen_wmparc.get_fdata()
        
        
        # Filtrar nodos fiduciarios visibles
        fiducial_nodes_visibles = [node for node in fiducial_nodes if node.GetDisplayVisibility()]

        
        # Obtener información de los nodos fiduciarios visibles
        for node in fiducial_nodes_visibles:
            nombreViejo=node.GetName()
            print(f'Nodo Fiduciario activo: {nombreViejo}')
            
            # Aquí puedes acceder a otras propiedades del nodo fiduciario según tus necesidades
            # Por ejemplo, puedes obtener las coordenadas de los puntos fiduciarios:
            for i in range(node.GetNumberOfControlPoints()):
                puntoRs = [0, 0, 0]
                node.GetNthControlPointPosition(i, puntoRs)
                print(f'los puntos RAS son {puntoRs}')

                
            valorDelPunto=self.indices(imagen_wmparc,datos_wmparc,puntoRs)
            significado=self.zonaCerebral(archivo_aseg_label,datos_wmparc,valorDelPunto,node)   
            self.datosFiduciarios+=[[nombreViejo, significado, puntoRs[0],puntoRs[1], puntoRs[2]]]  
  
    #Exxxportar
    #uso 
    def exportarPDF(self):
        self.getPDF2(self.datosFiduciarios)   
     
        
    #Agrega lineas en la escena para luego modelar sobre ellas
    #En uso
    def agregarLineas(self):
        nombre_deseado = f'Referencia electrodo {self.elec}'
        self.listaFidus.append(nombre_deseado)
        fiduNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode',nombre_deseado)
        # Establecer el nombre deseado para los fiduciarios
        
              
    
        slicer.util.getNode(nombre_deseado).GetDisplayNode().SetSelectedColor(1,0,0)
        slicer.util.getNode(nombre_deseado).GetDisplayNode().SetOpacity(0.75)
        slicer.util.getNode(nombre_deseado).GetDisplayNode().SetGlyphSize(1)
        # Configurar la clase de referencia para el modo de colocación
        selection_node = slicer.mrmlScene.GetNodeByID("vtkMRMLSelectionNodeSingleton")
        selection_node.SetReferenceActivePlaceNodeClassName("vtkMRMLMarkupsLineNode")

        # Configurar el modo de colocación y persistencia
        interaction_node = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
        place_mode_persistence = 0
        interaction_node.SetPlaceModePersistence(place_mode_persistence)
        interaction_node.SetCurrentInteractionMode(1)  # 1 corresponde al modo de colocación
        self.elec+=1  
   
    #Carga autoamticamente los fiduciarios de radiosensibilidad
    #En uso   
    def modelizarRs(self,markup: vtkMRMLMarkupsFiducialNode, rutaArchivo,indice):
        
        
        startTime = time.time()
        shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
        SceneID = shNode.GetSceneItemID()
        
        #carpetaEsferasModelos = shNode.CreateFolderItem(SceneID, f"Rs_modelos")
        carpetaRS = shNode.CreateFolderItem(SceneID, f"RS")
        transformNode= self.getTransformation(markup,rutaArchivo,"RS",self.carpeta)
        
        if indice==0: #SD10R-SP05X-000
            coordenadasFidu=[1.205, 6.205 ,11.205 ,16.205 ,21.205 ,26.205 ,31.205 ,36.205 ,41.205,46.205]
            
        elif indice==1:#SD10R-SP10X-000
            coordenadasFidu=[1.205, 11.205 ,21.205 ,31.205 ,41.205 ,51.205 ,61.205 ,71.205 ,81.205,91.205 ]
            
        elif indice==2:#bf09r-SP61X-0BB
            coordenadasFidu=[0.785, 3.785, 9.785, 15.785, 21.785, 27.785, 33.785, 39.785, 45.785]
            
        elif indice==3:#SD08R-SP05X-000
            coordenadasFidu=[3.285,7.79,13.79,19.79,25.79,31.79,37.79,43.79]
               
        else:
            print("The model doesn´t exist")         

    
        electrodePath = os.path.join(os.path.dirname(__file__), 'Resources\\Electrodos')
        shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
        SceneID = shNode.GetSceneItemID()  
             
        carpetaDestino=shNode.GetItemByName(f"Electrodo {self.carpeta}")

        modeloesferita=[""]*len(coordenadasFidu)
        esfera=[""]*len(coordenadasFidu)
                      
        for i in range(len(coordenadasFidu)):
            '''
            #modelos STAND BY HASTA DISEÑAR LOS OTROS
            esfera[i]=f"BF09R-RS_{i+1}.stl"
            
            modeloesferita[i]=os.path.join(electrodePath,esfera[i])
            modeloEsfera=slicer.util.loadModel(modeloesferita[i])
            
            modeloEsfera.SetAndObserveTransformNodeID(transformNode.GetID())
            modeloEsfera.GetDisplayNode().SetColor(0,1,0)
            modeloEsfera.GetDisplayNode().SetOpacity(0.05)
            modeloEsfera.GetDisplayNode().SetVisibility(False)
            
            itemID1 = shNode.GetItemByDataNode(modeloEsfera)
            shNode.SetItemParent(itemID1,carpetaEsferasModelos)              
            '''
    
            
            #fiduciarios
            #creo nodos fiduciarios con el nombre mapeo x-x
            fiduNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsFiducialNode',f"{self.carpeta}_RS {i+1}") 
            fiduNode.SetLocked(True)
            #seteo las caracteristicas de los fiduciarios
            pointListNode = slicer.util.getNode(f"{self.carpeta}_RS {i+1}").GetDisplayNode().SetGlyphSize(30)
            slicer.util.getNode(f"{self.carpeta}_RS {i+1}").GetDisplayNode().SetSelectedColor(0,1,0)
            slicer.util.getNode(f"{self.carpeta}_RS {i+1}").GetDisplayNode().SetOpacity(0.15)
            slicer.util.getNode(f"{self.carpeta}_RS {i+1}").GetDisplayNode().SetVisibility(False)     
            #slicer.util.getNode(f"Mapeo {i+1}-{i+2}").GetDisplayNode().SetLocked(True)            
            
            #agrego el fiduciario a la escena
            pepe=slicer.modules.markups.logic().AddControlPoint(0, 0, coordenadasFidu[i])

            #transformo las coordenadas
            transformNode = slicer.util.getNode(f'TransformacionRS {self.carpeta}')
            transformMatrix = vtk.vtkMatrix4x4()
            # Obtener la transformación del nodo directamente
            transform = transformNode.GetTransformToParent()
            #guardo los fiduciarios en la carpeta Mapeo
            itemID1 = shNode.GetItemByDataNode(fiduNode)
            shNode.SetItemParent(itemID1,carpetaRS)   
            

      
        #sirve para establecer las coordenadas a los fiduciarios     
        for i in range(len(coordenadasFidu)):
            fiduNode= slicer.util.getNode(f"{self.carpeta}_RS {i+1}")
            for j in range(1):
            # Obtener las coordenadas originales del fiduciario
                coordenadas_originales = np.array([0,0,coordenadasFidu[i]])

                # Crear un objeto vtkVector3d con las coordenadas originales
                coordenadas_vtk = vtk.vtkVector3d(*coordenadas_originales)

                # Aplicar la transformación a las coordenadas
                transform.TransformPoint(coordenadas_vtk, coordenadas_vtk)

                # Establecer las nuevas coordenadas en el fiduciario
                fiduNode.SetNthControlPointPosition(j, [coordenadas_vtk.GetX(), coordenadas_vtk.GetY(), coordenadas_vtk.GetZ()])    
            
            
        itemID3 = shNode.GetItemByDataNode(transformNode)
        shNode.SetItemParent(itemID3,carpetaRS)      
        #shNode.SetItemParent(carpetaEsferasModelos,carpetaDestino) 
        shNode.SetItemParent(carpetaRS,carpetaDestino) 
        ############################################################################

        stopTime = time.time()
        print(f'Processing completed in {stopTime-startTime:.2f} seconds')        
        logging.info(f'Processing completed in {stopTime-startTime:.2f} seconds')   
       
    #En uso
    def cambioNumeroCarpeta(self,value):
        self.carpeta=value  
        self.elec=value

    #Carga autoamticamente los fiduciarios para el mapeo
    #En uso   
    def modelizarMapping(self,markup: vtkMRMLMarkupsFiducialNode, rutaArchivo,indice):
        startTime = time.time()
        #guardo la escena en una variable
        shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
        SceneID = shNode.GetSceneItemID()
        
        #creo la carpeta Mapeo en la escena
        carpetaMapeo = shNode.CreateFolderItem(SceneID, f"Mapeo adyacente")
        
        #obtengo la transformacion
        transformNode= self.getTransformation(markup,rutaArchivo,"Mapeo",self.carpeta)
        
        #IF que sirve para identificar el tipo de electrodo y devuelve las coordenadas en Z de los fiduciarios
        if indice==0: #SD10R-SP05X-000
            coordenadasFidu=[3.705 ,8.705 ,13.705 ,18.705 ,23.705 ,28.705 ,33.705 ,38.705 ,43.705]
        
        elif indice==1:#SD10R-SP10X-000

            coordenadasFidu=[6.205, 16.205 ,26.205 ,36.205 ,46.205 ,56.205 ,66.205 ,76.205 ,86.205 ]
        elif indice==2:#bf09r-SP61X-0BB
           # coordenadasFidu=[3.285, 7.785, 13.785, 19.785, 25.785, 31.785, 37.785, 43.785]
            coordenadasFidu=[2.285, 6.785, 12.785, 18.785, 24.785, 30.785, 36.785, 42.785]
            
        elif indice==3:#SD08R-SP05X-000
            coordenadasFidu=[2.285,7.79,13.79,19.79,25.79,31.79,37.79,43.79]
            
        else:
            print("The model doesn´t exist")         
        
 
        #obtengo la carpeta del electrodo recientemente creado. Se resta 1 por que al finalizar el modelado del electrodo se incremetna en 1     
        carpetaDestino=shNode.GetItemByName(f"Electrodo {self.carpeta}")
         
        #cargo los fiduciarios.      
        for i in range(len(coordenadasFidu)):
            #creo nodos fiduciarios con el nombre mapeo x-x
            fiduNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsFiducialNode',f"{self.carpeta}_Mapeo {i+1}-{i+2}") 
            fiduNode.SetLocked(True)
            
            #seteo las caracteristicas de los fiduciarios
            pointListNode = slicer.util.getNode(f"{self.carpeta}_Mapeo {i+1}-{i+2}").GetDisplayNode().SetGlyphSize(1)
            slicer.util.getNode(f"{self.carpeta}_Mapeo {i+1}-{i+2}").GetDisplayNode().SetSelectedColor(0,0,1)
            slicer.util.getNode(f"{self.carpeta}_Mapeo {i+1}-{i+2}").GetDisplayNode().SetOpacity(0.4)
            slicer.util.getNode(f"{self.carpeta}_Mapeo {i+1}-{i+2}").GetDisplayNode().SetVisibility(False)   
            slicer.util.getNode(f"{self.carpeta}_Mapeo {i+1}-{i+2}").GetDisplayNode().SetTextScale(2)
            #print(slicer.util.getNode(f"Mapeo {i+1}-{i+2}").GetDisplayNode())
            
            #agrego el fiduciario a la escena
            pepe=slicer.modules.markups.logic().AddControlPoint(0, 0, coordenadasFidu[i])
            

            #transformo las coordenadas
            transformNode = slicer.util.getNode(f'TransformacionMapeo {self.carpeta}')
            transformMatrix = vtk.vtkMatrix4x4()
            # Obtener la transformación del nodo directamente
            transform = transformNode.GetTransformToParent()
            #guardo los fiduciarios en la carpeta Mapeo
            itemID1 = shNode.GetItemByDataNode(fiduNode)
            shNode.SetItemParent(itemID1,carpetaMapeo)    
        
        itemID3 = shNode.GetItemByDataNode(transformNode)
        shNode.SetItemParent(itemID3,carpetaMapeo)   
        #guardo la carpeta mapeo en la del electrodo      
        shNode.SetItemParent(carpetaMapeo,carpetaDestino)
       
        '''
        for i in range(fiduNode.GetNumberOfFiducials()):
        # Obtener las coordenadas originales del fiduciario
            coordenadas_originales = np.array(fiduNode.GetNthControlPointPositionVector(i))

            # Crear un objeto vtkVector3d con las coordenadas originales
            coordenadas_vtk = vtk.vtkVector3d(*coordenadas_originales)

            # Aplicar la transformación a las coordenadas
            transform.TransformPoint(coordenadas_vtk, coordenadas_vtk)

            # Establecer las nuevas coordenadas en el fiduciario
            fiduNode.SetNthFiducialPositionFromArray(i, [coordenadas_vtk.GetX(), coordenadas_vtk.GetY(), coordenadas_vtk.GetZ()])'''
      
      
        #sirve para establecer las coordenadas a los fiduciarios     
        for i in range(len(coordenadasFidu)):
            fiduNode= slicer.util.getNode(f"{self.carpeta}_Mapeo {i+1}-{i+2}")
            for j in range(1):
            # Obtener las coordenadas originales del fiduciario
                coordenadas_originales = np.array([0,0,coordenadasFidu[i]])

                # Crear un objeto vtkVector3d con las coordenadas originales
                coordenadas_vtk = vtk.vtkVector3d(*coordenadas_originales)

                # Aplicar la transformación a las coordenadas
                transform.TransformPoint(coordenadas_vtk, coordenadas_vtk)

                # Establecer las nuevas coordenadas en el fiduciario
                fiduNode.SetNthControlPointPosition(j, [coordenadas_vtk.GetX(), coordenadas_vtk.GetY(), coordenadas_vtk.GetZ()])
        
        stopTime = time.time()
        print(f'Processing completed in {stopTime-startTime:.2f} seconds')        
        logging.info(f'Processing completed in {stopTime-startTime:.2f} seconds')   
  
    #Modeliza electrodo y llama  las funciones modelizarMapping() y modelizarRs()     
    #En uso
    def modelizarElectrodo(self,markup: vtkMRMLMarkupsFiducialNode, rutaArchivo,indice)-> None:
        startTime = time.time()

        if indice==0:
            contacto='electrodoContactoSD10R-SP05X-000.stl'
            plastico="electrodoPlasticoSD10R-SP05X-000.stl"
        elif indice==1:
            contacto='electrodoContactoSD10R-SP10X-000.stl'
            plastico="electrodoPlasticoSD10R-SP10X-000.stl"
        elif indice==2:
            contacto='electrodoContactoBF09R-SP61X-0BB.stl'
            plastico="electrodoPlasticoBF09R-SP61X-0BB.stl"
        elif indice==3:
            contacto='electrodoContactoSD08R-SP05X-000.stl'
            plastico="electrodoPlasticoSD08R-SP05X-000.stl"
        else:
            print("The model doesn´t exist")         
            
        electrodePath = os.path.join(os.path.dirname(__file__), 'Resources\\Electrodos')
        modelocontactito=os.path.join(electrodePath,contacto)
        modeloplastiquito=os.path.join(electrodePath,plastico)
              
        shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
        SceneID = shNode.GetSceneItemID()
        
        nombre=f"Electrodo {self.carpeta}"
        carpetaDestino = shNode.CreateFolderItem(SceneID, nombre)
 
        transformNode= self.getTransformation(markup,rutaArchivo,"Modelo",nombre)

        #modeloElectrodo=slicer.util.loadSegmentation("C:\\Users\\Emiliano\\Documents\\Unaj\\BIOING\\procesamiento de imagenes biomedicas\\ElectrodeMarking\\ElectrodeMarking\\Resources\\Electrodos\\electrodoContactoSD08R-SP05X-000.stl")
        #modeloPlastico=slicer.util.loadSegmentation("C:\\Users\\Emiliano\\Documents\\Unaj\\BIOING\\procesamiento de imagenes biomedicas\\ElectrodeMarking\\ElectrodeMarking\\Resources\\Electrodos\\electrodoPlasticoSD08R-SP05X-000.stl")
        #modeloPlastico=slicer.util.loadModel("C:\\Users\\Emiliano\\Documents\\Unaj\\BIOING\\procesamiento de imagenes biomedicas\\ElectrodeMarking\\ElectrodeMarking\\Resources\\Electrodos\\electrodoPlasticoSD08R-SP05X-000.stl")    

        
        modeloElectrodo=slicer.util.loadModel(modelocontactito)
        #modeloElectrodo.GetDisplayNode().SetColor(1,0,0)
        #modeloElectrodo.GetDisplayNode().SetOpacity(0.5)
        segmentacionElectrodo=slicer.util.loadSegmentation(modelocontactito)
      
               
        modeloPlastico=slicer.util.loadModel(modeloplastiquito)    
        modeloPlastico.GetDisplayNode().SetColor(1,0,0)
        modeloPlastico.GetDisplayNode().SetOpacity(0.15)

        # Aplicar la transformación al modelo
        modeloElectrodo.SetAndObserveTransformNodeID(transformNode.GetID())
        modeloPlastico.SetAndObserveTransformNodeID(transformNode.GetID())
        segmentacionElectrodo.SetAndObserveTransformNodeID(transformNode.GetID())
        
        
        #enviar los modelos a la carpeta creada      
        itemID1 = shNode.GetItemByDataNode(modeloElectrodo)
        itemID2 = shNode.GetItemByDataNode(modeloPlastico)        
        itemID3 = shNode.GetItemByDataNode(transformNode)
        itemID4 = shNode.GetItemByDataNode(segmentacionElectrodo)
        
        lineaReferencia=shNode.GetItemByName(f"Referencia electrodo {self.carpeta}")
        
        shNode.SetItemParent(itemID1,carpetaDestino)
        shNode.SetItemParent(itemID2,carpetaDestino)
        shNode.SetItemParent(itemID3,carpetaDestino)
        shNode.SetItemParent(itemID4,carpetaDestino)
        
        shNode.SetItemParent(lineaReferencia,carpetaDestino)


        self.modelizarRs(markup,rutaGuardado,indice)
        self.modelizarMapping(markup,rutaGuardado,indice)
        self.carpeta +=1
        stopTime = time.time()
        print(f'Processing completed in {stopTime-startTime:.2f} seconds')        
        logging.info(f'Processing completed in {stopTime-startTime:.2f} seconds')   
 
    #Se utiliza para generar el reporte.
    #genera imagens biomedicas de los fiduciarios
    #En uso
    def modelizar_px(self, markup: vtkMRMLMarkupsFiducialNode, rutaArchivo)-> None:
        startTime = time.time()
        with open(f'{rutaArchivo}\\{markup.GetName()}.json', 'r') as file:
            data = json.load(file)
            centros = data


        fiduciarios=centros["markups"][0]["controlPoints"]
        diametro=centros["markups"][0]["display"]["glyphSize"]
        
        listaCentros=[]
        for pepe in range(0,len(fiduciarios)):
            listaCentros.append(fiduciarios[pepe]["position"])
            
        # Configuración de la imagen
        image_size = 256
        num_slices = 256    

        center_x_mm = 0
        center_y_mm = 0
        center_z_mm = 0
        # Crear un volumen 3D
        volume = np.zeros((image_size, image_size, num_slices))
        
        # Supongamos que deseas que el origen esté en el centro de la imagen
        offset_x = -127.5
        offset_y = -127.5
        offset_z = -127.5

        # Crear una matriz de transformación con el origen en el punto deseado
        affine_con_offset = np.eye(4)
        affine_con_offset[0, 3] = offset_x
        affine_con_offset[1, 3] = offset_y
        affine_con_offset[2, 3] = offset_z
        # Llenar el volumen con píxeles en blanco según los centros de las esferas

        for centro in listaCentros:
                x_mm, y_mm, z_mm = centro

                x_mm, y_mm, z_mm = -x_mm, -y_mm, z_mm

            
                
            # Calcular el radio (la mitad del diámetro) en píxeles
                radio_x = diametro / (2)
                radio_y = diametro / (2)
                radio_z = diametro / (2)
               
                # Convertir las coordenadas de milímetros a píxeles y ajustar al centro de la imagen
                x_pixel = (x_mm - center_x_mm) + (image_size // 2)-0.5
                y_pixel = (y_mm - center_y_mm) + (image_size // 2)-0.5
                z_pixel = (z_mm - center_z_mm) + (num_slices // 2)-0.5
               
                # Calcular la distancia desde el centro de la esfera al píxel actual
                xx, yy, zz = np.meshgrid(np.arange(image_size), np.arange(image_size), np.arange(num_slices), indexing='ij')
                dist = np.sqrt((xx - x_pixel) ** 2 + (yy - y_pixel) ** 2 + (zz - z_pixel) ** 2)
            # Establecer el píxel en blanco si está dentro del radio de la esfera
                volume[dist <= radio_x] = 255
            
        # Guardar el volumen como archivo NIfTI
        nifti_img = nib.Nifti1Image(volume, affine=affine_con_offset)
        nib.save(nifti_img, f'{rutaArchivo}\\{markup.GetName()}.nii')
        
        propiedades = {
            "name":f"{markup.GetName()} Volume",
            "center": True,
            "autoWindowLevel": True,
            "show": True
        }
        slicer.util.loadVolume(f"{rutaArchivo}\\{markup.GetName()}.nii",properties=propiedades)
        slicer.util.loadSegmentation(f"{rutaArchivo}\\{markup.GetName()}.nii")   

        stopTime = time.time()
        print(f'Processing completed in {stopTime-startTime:.2f} seconds')        
        logging.info(f'Processing completed in {stopTime-startTime:.2f} seconds')    
     
    
    
    
    
    #################################################################################################### 
    #Funciones obsoeltas.  
    #Mueve carpetas
    #En desuso 
    def moverCarpeta(self,carpeta,carpetaArriba):
        shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
        sceneItemID = shNode.GetSceneItemID()
        segmentationItemID = shNode.GetItemChildWithName(sceneItemID,carpeta)
        folderItemID = shNode.GetItemChildWithName(sceneItemID,carpetaArriba)
       
        shNode.MoveItem(folderItemID,segmentationItemID)
        slicer.mrmlScene.StartState(slicer.vtkMRMLScene.ImportState)
        slicer.mrmlScene.EndState(slicer.vtkMRMLScene.ImportState)
      
   #Desuso
    def getPDF(self,datosFiduciarios):
        capturaPath = os.path.join(os.path.dirname(__file__), 'Resources\\PlantillaPDF\\Captura.png')
        reportePdfPath=os.path.join(rutaGuardado,"reporte.pdf")
        def addPageNumber(canvas, doc):
            """
            Add the page number
            """
            page_num = canvas.getPageNumber()
            text = "Page #%s" % page_num
            canvas.drawRightString(200*mm, 20*mm, text)

        doc = SimpleDocTemplate(reportePdfPath,pagesize=A4,
                            rightMargin=72,leftMargin=72,
                            topMargin=72,bottomMargin=15)
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
        
        Story = []
        

        i=0
        

        Story.append(Spacer(0, 57))
        ptext = f'''<img src={capturaPath} width="500" height="140"/>'''        
        Story.append(Paragraph(ptext, styles["Normal"])) 
        for datos in datosFiduciarios:
            # Create return address


            ptext = f'<font size="12">Nombre viejo: %s</font>' % str(datos[0])        
            Story.append(Paragraph(ptext, styles["Normal"]))
            Story.append(Spacer(1, 9))
            ptext = f'<font size="12">Nombre Nuevo: %s</font>' % str(datos[1])        
            Story.append(Paragraph(ptext, styles["Normal"]))
            Story.append(Spacer(1, 9))
            ptext = f'<font size="12">Coordenada R: %s</font>' % str(datos[2])        
            Story.append(Paragraph(ptext, styles["Normal"]))
            Story.append(Spacer(1, 9))
            ptext = f'<font size="12">Coordenada A: %s</font>' % str(datos[3])        
            Story.append(Paragraph(ptext, styles["Normal"]))
            Story.append(Spacer(1, 9))
            ptext = f'<font size="12">Coordenada S: %s</font>' % str(datos[4])        
            Story.append(Paragraph(ptext, styles["Normal"]))
            Story.append(Spacer(1, 9)) 
            ptext = f'<font size="12">--------------------------------------------------------------------------------------</font>'        
            Story.append(Paragraph(ptext, styles["Normal"]))
            Story.append(Spacer(1, 4)) 
            i+=1 
            
            if i==len(datosFiduciarios):

                break  
 

            if i %5==0:
                Story.append(Spacer(1, 55))
                ptext = f'<font size="8">                          Av. Calchaquí 5401 – Tel.: 011 4210 9000 - Florencio Varela – Buenos Aires - Argentina</font>'        
                Story.append(Paragraph(ptext, styles["Normal"]))
                
                Story.append(PageBreak())
                Story.append(Spacer(0, 57))
                ptext = f'''<img src={capturaPath} width="500" height="140"/>'''     
                Story.append(Paragraph(ptext, styles["Normal"]))
                

            
            
        doc.build(Story, onFirstPage=addPageNumber, onLaterPages=addPageNumber)
        


        print(f"Nuevo documento generado en: {rutaGuardado}") 
  
    #Obsoelto
    def modelizar_mm(self)-> None:
        startTime = time.time()        
        with open('C:\\Users\\Emiliano\\Documents\\Unaj\\BIOING\\procesamiento de imagenes biomedicas\\ElectrodeMarking\\ElectrodeMarking\\Resources\\Electrodo 1.json', 'r') as file:
            data = json.load(file)
            centros = data

        x1,y1,z1=1,1,1
        fiduciarios=centros["markups"][0]["controlPoints"]
        diametro=centros["markups"][0]["display"]["glyphSize"]
        
        listaCentros=[]
        for pepe in range(0,len(fiduciarios)):
            listaCentros.append(fiduciarios[pepe]["position"])
            
        # Configuración de la imagen
        image_size = 256
        num_slices = 256    
        # Tamaño total de la imagen en milímetros (ajusta según tus datos)
        total_width_mm = image_size*x1
        total_height_mm = image_size*y1
        total_depth_mm = num_slices*z1            
        # Resolución en milímetros por píxel (ajusta según tus datos)
        resolution_x_mm_per_pixel = total_width_mm / image_size
        resolution_y_mm_per_pixel = total_height_mm / image_size
        resolution_z_mm_per_pixel = total_depth_mm / num_slices

        # Centro de la imagen en milímetros
        center_x_mm = total_width_mm / 2.0
        center_y_mm = total_height_mm / 2.0
        center_z_mm = total_depth_mm / 2.0
        center_x_mm = 0
        center_y_mm = 0
        center_z_mm = 0
        
        # Crear un volumen 3D
        volume = np.zeros((image_size, image_size, num_slices))    
        # Llenar el volumen con píxeles en blanco según los centros de las esferas

        for centro in listaCentros:
                x_mm, y_mm, z_mm = centro

                x_mm, y_mm, z_mm = -x_mm, -y_mm, z_mm

                diametro_mm = diametro 
                
            # Calcular el radio (la mitad del diámetro) en píxeles
                radio_x = diametro_mm / (2 * resolution_x_mm_per_pixel)
                radio_y = diametro_mm / (2 * resolution_y_mm_per_pixel)
                radio_z = diametro_mm / (2 * resolution_z_mm_per_pixel)
                
                # Convertir las coordenadas de milímetros a píxeles y ajustar al centro de la imagen
                x_pixel = int((x_mm - center_x_mm) / resolution_x_mm_per_pixel) + image_size // 2
                y_pixel = int((y_mm - center_y_mm) / resolution_y_mm_per_pixel) + image_size // 2
                z_pixel = int((z_mm - center_z_mm) / resolution_z_mm_per_pixel) + num_slices // 2
               
                
                # Calcular la distancia desde el centro de la esfera al píxel actual
                xx, yy, zz = np.meshgrid(np.arange(image_size), np.arange(image_size), np.arange(num_slices), indexing='ij')
                dist = np.sqrt((xx - x_pixel) ** 2 + (yy - y_pixel) ** 2 + (zz - z_pixel) ** 2)
            # Establecer el píxel en blanco si está dentro del radio de la esfera
                volume[dist <= radio_x] = 255
            
        # Guardar el volumen como archivo NIfTI
        nifti_img = nib.Nifti1Image(volume, affine=np.eye(4))
        nib.save(nifti_img, 'C:\\Users\\Emiliano\\Documents\\Unaj\\BIOING\\procesamiento de imagenes biomedicas\\ElectrodeMarking\\ElectrodeMarking\\Resources\\outputFiduciarios.nii')
        
        propiedades = {
            "name":"outputFiduciarios",
            "center": True,
            "autoWindowLevel": True,
            "show": True
        }
        slicer.util.loadVolume("C:\\Users\\Emiliano\\Documents\\Unaj\\BIOING\\procesamiento de imagenes biomedicas\\ElectrodeMarking\\ElectrodeMarking\\Resources\\outputFiduciarios.nii",properties=propiedades)    
        
        stopTime = time.time()
        print(f'Processing completed in {stopTime-startTime:.2f} seconds')        
        logging.info(f'Processing completed in {stopTime-startTime:.2f} seconds')      
    
        
#original       
''' def process(self,
                inputVolume: vtkMRMLScalarVolumeNode,
                outputVolume: vtkMRMLScalarVolumeNode,
                imageThreshold: float,
                invert: bool = False,
                showResult: bool = True) -> None:
        """
        Run the processing algorithm.
        Can be used without GUI widget.
        :param inputVolume: volume to be thresholded
        :param outputVolume: thresholding result
        :param imageThreshold: values above/below this threshold will be set to 0
        :param invert: if True then values above the threshold will be set to 0, otherwise values below are set to 0
        :param showResult: show output volume in slice viewers
        """

        if not inputVolume or not outputVolume:
            raise ValueError("Input or output volume is invalid")

        import time
        startTime = time.time()
        logging.info('Processing started')

        # Compute the thresholded output volume using the "Threshold Scalar Volume" CLI module
        cliParams = {
            'InputVolume': inputVolume.GetID(),
            'OutputVolume': outputVolume.GetID(),
            'ThresholdValue': 1,
            'ThresholdType': 'Above' if invert else 'Below'
        }
        cliNode = slicer.cli.run(slicer.modules.thresholdscalarvolume, None, cliParams, wait_for_completion=True, update_display=showResult)
        # We don't need the CLI module node anymore, remove it to not clutter the scene with it
        slicer.mrmlScene.RemoveNode(cliNode)

        stopTime = time.time()
        logging.info(f'Processing completed in {stopTime-startTime:.2f} seconds')'''

#
# ElectrodeMarkingTest
#

class ElectrodeMarkingTest(ScriptedLoadableModuleTest):
    """
    This is the test case for your scripted module.
    Uses ScriptedLoadableModuleTest base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setUp(self):
        """ Do whatever is needed to reset the state - typically a scene clear will be enough.
        """
        slicer.mrmlScene.Clear()

    def runTest(self):
        """Run as few or as many tests as needed here.
        """
        self.setUp()
        self.test_ElectrodeMarking1()

    def test_ElectrodeMarking1(self):
        """ Ideally you should have several levels of tests.  At the lowest level
        tests should exercise the functionality of the logic with different inputs
        (both valid and invalid).  At higher levels your tests should emulate the
        way the user would interact with your code and confirm that it still works
        the way you intended.
        One of the most important features of the tests is that it should alert other
        developers when their changes will have an impact on the behavior of your
        module.  For example, if a developer removes a feature that you depend on,
        your test should break so they know that the feature is needed.
        """

        self.delayDisplay("Starting the test")

        # Get/create input data

        import SampleData
        registerSampleData()
        inputVolume = SampleData.downloadSample('ElectrodeMarking1')
        self.delayDisplay('Loaded test data set')

        inputScalarRange = inputVolume.GetImageData().GetScalarRange()
        self.assertEqual(inputScalarRange[0], 0)
        self.assertEqual(inputScalarRange[1], 695)

        outputVolume = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode")
        threshold = 100

        # Test the module logic

        logic = ElectrodeMarkingLogic()

        # Test algorithm with non-inverted threshold
        logic.process(inputVolume, outputVolume, threshold, True)
        outputScalarRange = outputVolume.GetImageData().GetScalarRange()
        self.assertEqual(outputScalarRange[0], inputScalarRange[0])
        self.assertEqual(outputScalarRange[1], threshold)

        # Test algorithm with inverted threshold
        logic.process(inputVolume, outputVolume, threshold, False)
        outputScalarRange = outputVolume.GetImageData().GetScalarRange()
        self.assertEqual(outputScalarRange[0], inputScalarRange[0])
        self.assertEqual(outputScalarRange[1], inputScalarRange[1])

        self.delayDisplay('Test passed')
