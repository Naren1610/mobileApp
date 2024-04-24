from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen,ScreenManager

#
# class testApp(Screen):
#     def __init__(self,**kwargs):
#         super().__init__(**kwargs)
#     pass
# class myApp(MDApp):
#     def build(self):
#         self.theme_cls.theme_style="Dark"
#         self.theme_cls.primary_palette = "Amber"#(color for text fields
#         return testApp()
# if __name__=="__main__":
#     Window.size=(360,640)
#     Builder.load_file("main.kv")
#     myApp().run()

class TestApp(Screen):
    pass

class HomePage(Screen):
    pass

class MyApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Amber"
        sm = ScreenManager()
        sm.add_widget(TestApp(name='login'))
        sm.add_widget(HomePage(name='home'))
        return sm

if __name__ == "__main__":
    Window.size = (360, 640)
    Builder.load_file("main.kv")
    MyApp().run()
