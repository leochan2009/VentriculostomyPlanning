import slicer, vtk
from ctk import ctkAxesWidget
from VentriculostomyPlanningUtils.UserEvents import VentriculostomyUserEvents
from SlicerDevelopmentToolboxUtils.buttons import LayoutButton, CheckableIconButton, BasicIconButton
from SlicerDevelopmentToolboxUtils.icons import Icons
from SlicerDevelopmentToolboxUtils.mixins import ModuleWidgetMixin
import os
import qt
import numpy

class GreenSliceLayoutButton(LayoutButton):
  """ LayoutButton inherited class which represents a button for the SlicerLayoutOneUpGreenSliceView including the icon.

  Args:
    text (str, optional): text to be displayed for the button
    parent (qt.QWidget, optional): parent of the button

  .. code-block:: python

    from VentriculostomyPlanningUtils.buttons import GreenSliceLayoutButton

    button = GreenSliceLayoutButton()
    button.show()
  """

  iconFileName=os.path.join(os.path.dirname(os.path.normpath(os.path.dirname(os.path.realpath(__file__)))),'Resources','Icons','LayoutOneUpGreenSliceView.png')
  _ICON = qt.QIcon(iconFileName)
  LAYOUT = slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpGreenSliceView

  def __init__(self, text="", parent=None, **kwargs):
    super(GreenSliceLayoutButton, self).__init__(text, parent, **kwargs)
    self.toolTip = "Green Slice Only Layout"


class ConventionalSliceLayoutButton(LayoutButton):
  """ LayoutButton inherited class which represents a button for the ConventionalSliceLayoutButton including the icon.

  Args:
    text (str, optional): text to be displayed for the button
    parent (qt.QWidget, optional): parent of the button

  .. code-block:: python

    from VentriculostomyPlanningUtils.buttons import ConventionalSliceLayoutButton

    button = ConventionalSliceLayoutButton()
    button.show()
  """
  iconFileName=os.path.join(os.path.dirname(os.path.normpath(os.path.dirname(os.path.realpath(__file__)))),'Resources','Icons','LayoutConventionalSliceView.png')
  _ICON = qt.QIcon(iconFileName)
  LAYOUT = slicer.vtkMRMLLayoutNode.SlicerLayoutConventionalView

  def __init__(self, text="", parent=None, **kwargs):
    super(ConventionalSliceLayoutButton, self).__init__(text, parent, **kwargs)
    self.toolTip = "Conventional Slice Only Layout"


class ScreenShotButton(BasicIconButton):
  
  iconFileName=os.path.join(os.path.dirname(os.path.normpath(os.path.dirname(os.path.realpath(__file__)))),'Resources','Icons','screenShot.png')
  _ICON = qt.QIcon(iconFileName)
  
  @property
  def caseResultDir(self):
    return self._caseResultDir

  @caseResultDir.setter
  def caseResultDir(self, value):
    self._caseResultDir = value
    self.imageIndex = 0

  def __init__(self, text="", parent=None, **kwargs):
    super(ScreenShotButton, self).__init__(text, parent, **kwargs)
    import ScreenCapture
    self.cap = ScreenCapture.ScreenCaptureLogic()
    self.checkable = False
    self._caseResultDir = ""
    self.imageIndex = 0

  def _connectSignals(self):
    super(ScreenShotButton, self)._connectSignals()
    self.clicked.connect(self.onClicked)

  def onClicked(self):
    if self.caseResultDir:
      self.cap.showViewControllers(False)
      fileName = os.path.join(self._caseResultDir, 'Results', 'screenShot'+str(self.imageIndex)+'.png')
      if os.path.exists(fileName):
        self.imageIndex = self.imageIndex + 1
        fileName = os.path.join(self._caseResultDir, 'Results', 'screenShot' + str(self.imageIndex) + '.png')
      self.cap.captureImageFromView(None, fileName)
      self.cap.showViewControllers(True)
      self.imageIndex = self.imageIndex + 1
    else:
      slicer.util.warningDisplay("Case was not created, create a case first")
    pass

class ReverseViewOnCannulaButton(CheckableIconButton):
  
  iconFileName=os.path.join(os.path.dirname(os.path.normpath(os.path.dirname(os.path.realpath(__file__)))),'Resources','Icons','ReverseView.png')
  _ICON = qt.QIcon(iconFileName)
  
  @property
  def cannulaNode(self):
    return self._cannulaNode

  @cannulaNode.setter
  def cannulaNode(self,value):
    self._cannulaNode = value
    self.cameraReversePos = None

  def __init__(self, text="", parent=None, **kwargs):
    super(ReverseViewOnCannulaButton, self).__init__(text, parent, **kwargs)
    self._cannulaNode = None
    self._pitchAngle = 0.0
    self._yawAngle = 0.0
    self.cameraPos = [0.0] * 3
    self.cameraReversePos = None
    self.camera = None
    layoutManager = slicer.app.layoutManager()
    threeDView = layoutManager.threeDWidget(0).threeDView()
    displayManagers = vtk.vtkCollection()
    threeDView.getDisplayableManagers(displayManagers)
    for index in range(displayManagers.GetNumberOfItems()):
      if displayManagers.GetItemAsObject(index).GetClassName() == 'vtkMRMLCameraDisplayableManager':
        self.camera = displayManagers.GetItemAsObject(index).GetCameraNode().GetCamera()
        self.cameraPos = self.camera.GetPosition()
    self.toolTip = "Reverse the view of the cannula from the other end"

  def calculateAnglesBasedOnCannula(self):
    nFiducials = self.cannulaNode.GetNumberOfFiducials()
    if nFiducials>=1:
      firstPos = numpy.array([0.0, 0.0, 0.0])
      self.cannulaNode.GetNthFiducialPosition(0,firstPos)
      lastPos = numpy.array([0.0, 0.0, 0.0])
      self.cannulaNode.GetNthFiducialPosition(nFiducials-1,lastPos)
      self._pitchAngle = numpy.arctan2(lastPos[2] - firstPos[2], abs(lastPos[1] - firstPos[1])) * 180.0 / numpy.pi
      self._yawAngle = -numpy.arctan2(lastPos[0] - firstPos[0], abs(lastPos[1] - firstPos[1])) * 180.0 / numpy.pi
      return True
    return False

  def _onToggled(self, checked):
    if self.cannulaNode:
      layoutManager = slicer.app.layoutManager()
      threeDView = layoutManager.threeDWidget(0).threeDView()
      if checked == True and self.calculateAnglesBasedOnCannula():
        displayManagers = vtk.vtkCollection()
        threeDView.getDisplayableManagers(displayManagers)
        for index in range(displayManagers.GetNumberOfItems()):
          if displayManagers.GetItemAsObject(index).GetClassName() == 'vtkMRMLCameraDisplayableManager':
            self.camera = displayManagers.GetItemAsObject(index).GetCameraNode().GetCamera()
            self.cameraPos = self.camera.GetPosition()
        if not self.cameraReversePos:
          threeDView.lookFromViewAxis(ctkAxesWidget.Posterior)
          threeDView.pitchDirection = threeDView.PitchUp
          threeDView.yawDirection = threeDView.YawRight
          threeDView.setPitchRollYawIncrement(self._pitchAngle)
          threeDView.pitch()
          if self._yawAngle < 0:
            threeDView.setPitchRollYawIncrement(self._yawAngle)
          else:
            threeDView.setPitchRollYawIncrement(360 - self._yawAngle)
          threeDView.yaw()
          if self.cannulaNode and self.cannulaNode.GetNumberOfFiducials() >= 2:
            posSecond = [0.0] * 3
            self.cannulaNode.GetNthFiducialPosition(1, posSecond)
            threeDView.setFocalPoint(posSecond[0], posSecond[1], posSecond[2])
          self.cameraReversePos = self.camera.GetPosition()
        else:
          self.camera.SetPosition(self.cameraReversePos)
          threeDView.zoomIn()  # to refresh the 3D viewer, when the view position is inside the skull model, the model is not rendered,
          threeDView.zoomOut()  # Zoom in and out will refresh the viewer
        slicer.mrmlScene.InvokeEvent(VentriculostomyUserEvents.ReverseViewClicked)
      else:
        displayManagers = vtk.vtkCollection()
        threeDView.getDisplayableManagers(displayManagers)
        for index in range(displayManagers.GetNumberOfItems()):
          if displayManagers.GetItemAsObject(index).GetClassName() == 'vtkMRMLCameraDisplayableManager':
            self.camera = displayManagers.GetItemAsObject(index).GetCameraNode().GetCamera()
            self.cameraReversePos = self.camera.GetPosition()
        self.camera.SetPosition(self.cameraPos)
        threeDView.zoomIn()  # to refresh the 3D viewer, when the view position is inside the skull model, the model is not rendered,
        threeDView.zoomOut()  # Zoom in and out will refresh the viewer
        slicer.mrmlScene.InvokeEvent(VentriculostomyUserEvents.ReverseViewClicked)

class AlgorithmSettingsButton(BasicIconButton):

  def __init__(self, connectedLayout, text="", parent=None, **kwargs):
    self.connectedLayout = connectedLayout
    self._ICON = Icons.settings
    super(AlgorithmSettingsButton, self).__init__(text, parent, **kwargs)
    self.settings = AlgorithmSettingsMessageBox(self.connectedLayout, slicer.util.mainWindow())

  def _connectSignals(self):
    super(AlgorithmSettingsButton, self)._connectSignals()
    self.clicked.connect(self.__onClicked)

  def __onClicked(self):
    self.settings = AlgorithmSettingsMessageBox(self.connectedLayout, slicer.util.mainWindow())
    self.settings.show()


class AlgorithmSettingsMessageBox(qt.QMessageBox, ModuleWidgetMixin):

  def __init__(self, connectedLayout, parent = None, **kwargs):
    qt.QMessageBox.__init__(self, parent, **kwargs)
    self.setStandardButtons(0)
    self.setLayout(qt.QGridLayout())
    self.algorithmFrame = qt.QFrame()
    self.algorithmFrame.setLayout(connectedLayout)
    self.layout().addWidget(self.algorithmFrame, 0, 0, 1, 1)
    self.okButton = self.createButton("OK")
    self.addButton(self.okButton, qt.QMessageBox.AcceptRole)
    self.layout().addWidget(self.createHLayout([self.okButton]), 1, 0, 1, 1)

  def show(self):
    qt.QMessageBox.show(self)

  def setAlgorithmLayout(self, layout):
    self.algorithmLayout = layout
    self.algorithmFrame.setLayout(layout)

