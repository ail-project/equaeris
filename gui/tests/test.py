from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.switch import Switch
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.spinner import Spinner
from kivy.uix.button import Button

class Automatic(BoxLayout):
    def __init__(self, **kwargs):
        super(Automatic, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.file = FileChooserIconView()
        self.add_widget(self.file)
        self.ip = TextInput(text="IP", multiline=False)
        self.add_widget(self.ip)
        self.add_widget(Label(text="aggressive:"))
        self.aggressive = Switch(active = True)
        self.add_widget(self.aggressive)

class Specific(BoxLayout):
    def __init__(self, **kwargs):
        services = ("redis", "cassandraDB", "rethinkDB", "mongoDB", "elasticsearch", "couchDB")
        super(Specific, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.service = Spinner(text='Service', values=services)
        self.add_widget(self.service)
        self.IP = TextInput(text = "IP", multiline=False)
        self.port = TextInput(text="port", multiline=False)
        self.add_widget(self.IP)
        self.add_widget(self.port)
        self.aggressive = Switch(active=True)
        self.add_widget(self.aggressive)


class Discovery(GridLayout):

    def __init__(self, **kwargs):
        super(Discovery, self).__init__(**kwargs)
        self.cols = 1
        self.add_widget(Label(text='Discovery'))
        self.add_widget(Label(text="Automatic Discovery"))
        automatic = Automatic()
        self.add_widget(automatic)
        specific = Specific()
        self.add_widget(specific)



class MyApp(App):

    def build(self):
        return Discovery()


if __name__ == '__main__':
    MyApp().run()
