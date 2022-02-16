import math

import sys

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import vtk
from vtk.util.colors import tomato
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtkmodules.vtkFiltersSources import *
from vtkmodules.vtkRenderingCore import *

# Просто Pi
PI = math.pi


class MouseInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, parent=None):
        self.AddObserver("LeftButtonPressEvent", self.leftButtonPressEvent)

    def leftButtonPressEvent(self, obj, event):
        self.OnLeftButtonDown()




class Shape():

    def get_area(self):
        pass

    def get_perimeter(self):
        pass
    
    #Получение точек для отрисовки
    def get_mapper(self):
        pass


class Circle(Shape):

    def __init__(self, r=0):
        super().__init__()
        self.r = r

    def set_r(self, x):
        if x:
            self.r = float(x)
            
    def get_area(self):
        return PI*(self.r**2)

    def get_perimeter(self):
        return 2*PI*self.r

    #Получение точек для отрисовки
    def get_mapper(self):
        polygonSource = vtkRegularPolygonSource()
        polygonSource.GeneratePolygonOff()
        polygonSource.SetNumberOfSides(50)
        polygonSource.SetRadius(self.r)
        polygonSource.SetCenter(0.0, 0.0, 0.0)

        self.mapper = vtkPolyDataMapper()
        self.mapper.SetInputConnection(polygonSource.GetOutputPort())
        return self.mapper


class Sphere(Circle):

    def __init__(self):
        super().__init__()

    def get_area(self):
        return 4 * PI * self.r ** 2

    def get_volume(self):
        return 4/3 * PI * self.r ** 3

    #Получение точек для отрисовки
    def get_mapper(self):

        sphereSource = vtkSphereSource()
        sphereSource.SetCenter(0.0, 0.0, 0.0)
        sphereSource.SetRadius(self.r)
        sphereSource.SetPhiResolution(100)
        sphereSource.SetThetaResolution(100)

        self.mapper = vtkPolyDataMapper()
        self.mapper.SetInputConnection(sphereSource.GetOutputPort())

        return self.mapper


class Cylinder(Circle):
    def __init__(self, h=0.0):
        super().__init__()

        self.h = h

    def set_h(self, x):
        if x:
            self.h = float(x)

    def get_area(self):
        return 2 * PI * self.r * (self.h + self.r)

    def volume(self):
        return PI * self.r ** 2 * self.h

    #Получение точек для отрисовки
    def get_mapper(self):
        # source
        cylinder = vtk.vtkCylinderSource()
        cylinder.SetResolution(50)
        cylinder.SetRadius(self.r)
        cylinder.SetHeight(self.h)

        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInputConnection(cylinder.GetOutputPort())
        return self.mapper


class Cone(Cylinder):
    def __init__(self):
        super().__init__()

    def get_area(self):
        return PI * self.r * (self.r + (self.r ** 2 + self.h * 2) ** 0.5)

    def volume(self):
        return 1/3 * PI * self.r ** 2 * self.h

    #Получение точек для отрисовки
    def get_mapper(self):

        source = vtk.vtkConeSource()
        source.SetResolution(100)
        source.SetRadius(self.r)
        source.SetHeight(self.h)

        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInputConnection(source.GetOutputPort())
        return self.mapper


class Pyramid(Shape):
    # a - длина стороны
    def __init__(self,n=3, a=0, h=0):
        super().__init__()
        self.a = a
        self.h = h
        self.n = n
        self.r = 0.0

    def set_r(self):
        # по этой формуле рассматриваем r как бедро равнобедренного треугольника и через основание а и угол находим
        self.r = self.a / (2 * math.cos(math.radians((180 - 360 / self.n) / 2)))
    def set_a(self, x):
        if x:
            self.a = float(x)
            self.set_r()

    def set_h(self, x):
        if x:
            self.h = float(x)

    def set_n(self, x):
        if x:
            self.n = int(x)
            self.set_r()

    #Получение точек для отрисовки
    def get_mapper(self):

        source = vtk.vtkConeSource()
        source.SetResolution(self.n)
        source.SetRadius(self.r)
        source.SetHeight(self.h)

        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInputConnection(source.GetOutputPort())
        return self.mapper




class Main_Window(QWidget):

    def __init__(self):
        super().__init__()

        # в атрибуте будет храниться фигура, с которой работают в данный момент (при старте программы это пустая фигура)
        self.shape = Shape()

        # инициализация главного UI
        self.UI()

        # Массив для временных кнопок, лейблов и других элементов интерфейса
        self.UI_elements = []

        self.validator = QIntValidator(1, 99, self)
    def UI(self):

        # кнопка отрисовки фигруы
        b_draw = QPushButton("Нарисовать фигуру", self)
        b_draw.clicked.connect(lambda:  self.draw_shape(self.shape))
        b_draw.move(0, 30)

        #выбор фигуры для работы
        cb_shape_type = QComboBox(self)
        cb_shape_type.addItem("")
        cb_shape_type.addItems([
            "Круг",
           # "Квадрат",
           # "Прямоугольник",
           # "Треугольник",
           # "Трапеция",
           # "Ромб",
            "Сфера",
           # "Куб",
           # "Параллелепипед",
            "Пирамида",
            "Цилиндр",
            "Конус"
        ])

        cb_shape_type.currentTextChanged.connect(lambda: self.defining_interface(cb_shape_type.currentText()))

        
        self.setGeometry(300, 300, 600, 600)
        self.setWindowTitle('Кажется работает')
        self.show()

        # для того что бы окно отрисовки было показано сразу (можно убрать) 
        self.draw_shape(self.shape)

    #Вызов окна отрисовки
    def draw_shape(self, shape):

        self.ren_win = Rendering_Window(shape)

    #показывает все элементы из массива
    def show_UI_elements(self):
        for element in self.UI_elements:
            element.show()

    # скрывает все элементы из массива и очищает его
    def clear_UI_elements(self):
        for element in self.UI_elements:
            element.hide()
        self.UI_elements.clear()

    # def update_UI_elements(self):
    #     for element in self.UI_elements:
    #         element.update()


    #определяет для какой фигуры показать интерфейс
    def defining_interface(self, shape_type):
        if shape_type == "":
            self.shape = Shape()
        elif shape_type == "Круг":
            self.interface_for_circle()
        elif shape_type == "Квадрат":
            pass
        elif shape_type == "Прямоугольник":
            pass
        elif shape_type == "Треугольник":
            pass
        elif shape_type == "Трапеция":
            pass
        elif shape_type == "Ромб":
            pass
        elif shape_type == "Сфера":
            self.interface_for_sphere()
        elif shape_type == "Куб":
            pass
        elif shape_type == "Параллелепипед":
            pass
        elif shape_type == "Пирамида":
            self.interface_for_pyramid()
        elif shape_type == "Цилиндр":
            self.interface_for_cylinder()
        elif shape_type == "Конус":
            self.interface_for_cone()


    def interface_for_circle(self):

        self.clear_UI_elements()

        self.shape = Circle()

        le_radius = QLineEdit(self)
        self.UI_elements.append(le_radius)
        le_radius.move(200, 100)
        le_radius.setValidator(self.validator)
        le_radius.textEdited.connect(lambda: self.shape.set_r(le_radius.text()))

        l_radius = QLabel("Радиус = ", self)
        self.UI_elements.append(l_radius)
        l_radius.move(140, 100)

        b_perimeter = QPushButton("Рассчитать периметр", self)
        self.UI_elements.append(b_perimeter)
        b_perimeter.setGeometry(400, 100, 200, 25)
        b_perimeter.clicked.connect(lambda: b_perimeter.setText(str(self.shape.get_perimeter())))

        b_area = QPushButton("Рассчитать площадь", self)
        self.UI_elements.append(b_area)
        b_area.setGeometry(400, 150, 200, 25)
        b_area.clicked.connect(lambda: b_area.setText(str(self.shape.get_area())))

        self.show_UI_elements()

    def interface_for_sphere(self):

        self.clear_UI_elements()
        #
        self.shape = Sphere()

        le_radius = QLineEdit(self)
        self.UI_elements.append(le_radius)
        le_radius.move(200, 100)
        le_radius.setValidator(self.validator)
        le_radius.textEdited.connect(lambda: self.shape.set_r(le_radius.text()))

        l_radius = QLabel("Радиус = ", self)
        self.UI_elements.append(l_radius)
        l_radius.move(140, 100)

        b_volume = QPushButton("Рассчитать объем", self)
        self.UI_elements.append(b_volume)
        b_volume.setGeometry(400, 100, 200, 25)
        b_volume.clicked.connect(lambda: b_volume.setText(str(self.shape.get_perimeter())))

        b_area = QPushButton("Рассчитать площадь", self)
        self.UI_elements.append(b_area)
        b_area.setGeometry(400, 150, 200, 25)
        b_area.clicked.connect(lambda: b_area.setText(str(self.shape.get_area())))

        self.show_UI_elements()

    def interface_for_cube(self):
        pass

    def interface_for_pyramid(self):

        self.clear_UI_elements()

        self.shape = Pyramid()

        le_radius = QLineEdit(self)
        self.UI_elements.append(le_radius)
        le_radius.move(200, 100)
        le_radius.setValidator(self.validator)
        le_radius.textEdited.connect(lambda: self.shape.set_a(le_radius.text()))

        l_radius = QLabel("Сторона = ", self)
        self.UI_elements.append(l_radius)
        l_radius.move(140, 100)

        le_height = QLineEdit(self)
        self.UI_elements.append(le_height)
        le_height.move(200, 150)
        le_height.setValidator(self.validator)
        le_height.textEdited.connect(lambda: self.shape.set_h(le_height.text()))

        l_height = QLabel("Высота = ", self)
        self.UI_elements.append(l_height)
        l_height.move(140, 150)

        le_num = QLineEdit(self)
        self.UI_elements.append(le_num)
        le_num.move(200, 200)
        le_num.setValidator(self.validator)
        le_num.textEdited.connect(lambda: self.shape.set_n(le_num.text()))

        l_num = QLabel("Кол-во сторон", self)
        self.UI_elements.append(l_num)
        l_num.move(100, 200)

        b_volume = QPushButton("Рассчитать объем", self)
        self.UI_elements.append(b_volume)
        b_volume.setGeometry(400, 100, 200, 25)
        b_volume.clicked.connect(lambda: b_volume.setText(str(self.shape.get_perimeter())))

        b_area = QPushButton("Рассчитать площадь", self)
        self.UI_elements.append(b_area)
        b_area.setGeometry(400, 150, 200, 25)
        b_area.clicked.connect(lambda: b_area.setText(str(self.shape.get_area())))

        self.show_UI_elements()

    def interface_for_cylinder(self):

        self.clear_UI_elements()
        #
        self.shape = Cylinder()

        le_radius = QLineEdit(self)
        self.UI_elements.append(le_radius)
        le_radius.move(200, 100)
        le_radius.setValidator(self.validator)
        le_radius.textEdited.connect(lambda: self.shape.set_r(le_radius.text()))

        l_radius = QLabel("Радиус = ", self)
        self.UI_elements.append(l_radius)
        l_radius.move(140, 100)

        le_height = QLineEdit(self)
        self.UI_elements.append(le_height)
        le_height.move(200, 150)
        le_height.setValidator(self.validator)
        le_height.textEdited.connect(lambda: self.shape.set_h(le_height.text()))

        l_height = QLabel("Высота = ", self)
        self.UI_elements.append(l_height)
        l_height.move(140, 150)

        b_volume = QPushButton("Рассчитать объем", self)
        self.UI_elements.append(b_volume)
        b_volume.setGeometry(400, 100, 200, 25)
        b_volume.clicked.connect(lambda: b_volume.setText(str(self.shape.get_perimeter())))

        b_area = QPushButton("Рассчитать площадь", self)
        self.UI_elements.append(b_area)
        b_area.setGeometry(400, 150, 200, 25)
        b_area.clicked.connect(lambda: b_area.setText(str(self.shape.get_area())))

        self.show_UI_elements()

    def interface_for_cone(self):

        self.clear_UI_elements()

        self.shape = Cone()

        le_radius = QLineEdit(self)
        self.UI_elements.append(le_radius)
        le_radius.move(200, 100)
        le_radius.setValidator(self.validator)
        le_radius.textEdited.connect(lambda: self.shape.set_r(le_radius.text()))

        l_radius = QLabel("Радиус = ", self)
        self.UI_elements.append(l_radius)
        l_radius.move(140, 100)

        le_height = QLineEdit(self)
        self.UI_elements.append(le_height)
        le_height.move(200, 150)
        le_height.setValidator(self.validator)
        le_height.textEdited.connect(lambda: self.shape.set_h(le_height.text()))

        l_height = QLabel("Высота = ", self)
        self.UI_elements.append(l_height)
        l_height.move(140, 150)

        b_volume = QPushButton("Рассчитать объем", self)
        self.UI_elements.append(b_volume)
        b_volume.setGeometry(400, 100, 200, 25)
        b_volume.clicked.connect(lambda: b_volume.setText(str(self.shape.get_perimeter())))

        b_area = QPushButton("Рассчитать площадь", self)
        self.UI_elements.append(b_area)
        b_area.setGeometry(400, 150, 200, 25)
        b_area.clicked.connect(lambda: b_area.setText(str(self.shape.get_area())))

        self.show_UI_elements()


class Rendering_Window(QMainWindow):
    def __init__(self, shape):
        super().__init__()

        # actor
        actor = vtk.vtkActor()
        actor.SetMapper(shape.get_mapper())
        actor.GetProperty().SetColor(tomato)
        # actor.RotateX(0)
        # actor.RotateY(0)

        # renderer
        ren = vtk.vtkRenderer()
        ren.AddActor(actor)
        ren.SetBackground(0.1, 0.2, 0.4)

        # interactor
        frame = QFrame()
        inter = QVTKRenderWindowInteractor(frame)
        inter.SetInteractorStyle(MouseInteractorStyle())

        ren_win = inter.GetRenderWindow()
        ren_win.AddRenderer(ren)

        # ren.ResetCamera()
        # ren.GetActiveCamera().Zoom(1)

        ren_win.Render()
        inter.Initialize()

        layout = QVBoxLayout()
        layout.addWidget(inter)
        frame.setLayout(layout)
        self.setCentralWidget(frame)

        self.setWindowTitle("Что то рисую.")
        self.setGeometry(300+600, 300, 600, 600)
        # self.centerOnScreen()
        self.show()



    # def centerOnScreen(self):
    #     res = QDesktopWidget().screenGeometry()
    #     self.move((res.width()/2) - (self.frameSize().width()/2),
    #               (res.height()/2) - (self.frameSize().height()/2))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_win = Main_Window()
    sys.exit(app.exec_())

    
