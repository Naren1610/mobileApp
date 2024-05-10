from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.boxlayout import BoxLayout

class PassRegistrationPage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        tp = TabbedPanel(do_default_tab=False)
        tpi1 = TabbedPanelItem(text='One')
        tpi1.add_widget(Label(text='Tab 1 Content'))
        tp.add_widget(tpi1)
        self.add_widget(tp)

class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(PassRegistrationPage(name='pass_registration'))
        return sm

if __name__ == '__main__':
    MyApp().run()
