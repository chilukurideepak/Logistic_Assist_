from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen
from kivymd.uix.behaviors import FakeRectangularElevationBehavior
from kivymd.uix.floatlayout import MDFloatLayout
from kivy.lang import Builder
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.base import runTouchApp
from kivy.core.window import Window
from support import account, otp
# fixing window size
Window.size = (300, 600)





# for animi_screen
class Animi_screen(Screen):
    pass


# for service selection
class Service_selection_screen(Screen):
    pass


class Company_login_screen(Screen):
    pass


class Company_signup_screen(Screen):
    pass

class Company_details(Screen):
    pass

class Carrier_login_screen(Screen):
    pass

class Company_dashboard(Screen):
    pass

class Bidding(Screen):
    pass

class Company_profile(Screen):
    pass

class Add_goods(Screen):
    pass

class Company_transaction_history(Screen):
    pass

class ResetPassword(Screen):
    def callback(self):
        MDApp.get_running_app().root.current = 'Company_login_screen'

class Carrier_otp_verify(Screen):
    pass

class Carrier_details(Screen):
    pass

class Carrier_dashboard(Screen):
    pass

class Carrier_profile(Screen):
    pass

class Carrier_history(Screen):
    pass

class Nav_bar(FakeRectangularElevationBehavior, MDFloatLayout):
    pass

class Company_questions(Screen):
    pass

class Carrier_questions(Screen):
    pass

class feedback(Screen):
    pass


# Main class of Application
class Main(MDApp):

    def build(self):
        self.theme_cls.theme_style = 'Light'
        self.theme_cls.primary_palette = 'DeepPurple'
        self.login_firebase = account()
        self.login_otp = otp()
        Builder.load_file("main.kv")

    def change_screen(self, screen_name):
        self.root.current = screen_name





Main().run()
