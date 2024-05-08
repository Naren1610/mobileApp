from os.path import basename

from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.filechooser import FileChooserIconView, FileChooserListView
from kivy.uix.popup import Popup
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen,ScreenManager
import qrcode
from kivy.uix.image import Image
import tempfile
import pyodbc
from kivymd.material_resources import dp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineListItem
from kivymd.uix.menu import MDDropdownMenu
from hashlib import sha256
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from datetime import datetime
import os


def get_connection():
    connection_string = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=MRYADAV\SQLEXPRESS;DATABASE=mobileApp;"
        "Trusted_Connection=yes;"
    )
    return pyodbc.connect(connection_string)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
           IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'users')
           CREATE TABLE users (
               id INT IDENTITY(1,1) PRIMARY KEY,
               firstname NVARCHAR(30) NOT NULL,
               lastname NVARCHAR(30) NOT NULL,
               email NVARCHAR(50) UNIQUE NOT NULL,
               phone NVARCHAR(15) UNIQUE NOT NULL,
               password NVARCHAR(255) NOT NULL
           );
       ''')
    conn.commit()
    conn.close()


class SignupScreen(Screen):
    def signup(self, phone, password):
        if self.validate_password(password):
            if self.add_user(phone, password):
                print("User created successfully!")
            else:
                print("Username already exists!")
        else:
            print("Password does not meet the requirements!")


    def add_user(self,firstname, lastname, email,phone, password):
        conn = get_connection()
        cursor = conn.cursor()
        hashed_password = sha256(password.encode()).hexdigest()
        try:
            cursor.execute('INSERT INTO users (firstname, lastname, email, phone, password) VALUES (?, ?, ?, ?, ?)', (firstname, lastname, email, phone, hashed_password))
            conn.commit()
            self.manager.current = 'login'
            return True
        except pyodbc.IntegrityError:
            return False
        finally:
            conn.close()


    def check_user(phone, password):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT password FROM users WHERE phone = ?', (phone,))
        result = cursor.fetchone()
        conn.close()
        if result:
            hashed_password = sha256(password.encode()).hexdigest()
            return hashed_password == result[0]
        return False


class LoginPage(Screen):
    def signin(self, phone, password):
        if SignupScreen.check_user(phone, password):
            print("Login successful!")
        else:
            print("Invalid username or password!")

    def validate_password(self, password):
        if len(password) < 6:
            return False
        if not any(char.isupper() for char in password):
            return False
        if not any(char in '!@#$%^&*()-_=+[]{};:"\'|,<>.?/' for char in password):
            return False
        return True


class HomePage(Screen):
    pass
class BusTicketPage(Screen):
    pass



class PassRegistrationPage(Screen):
    id_proof_menu = ObjectProperty(None)
    pass_menu = ObjectProperty(None)
    def __init__(self, **kwargs):
        super(PassRegistrationPage, self).__init__(**kwargs)


    def on_enter(self):
        # Set up the ID proof menu only once
        if not self.id_proof_menu:
            self.initialize_id_proof_menu()
        if not self.pass_menu:
            self.initialize_pass_menu()

    def initialize_id_proof_menu(self):
        menu_items = [
            {"viewclass": "OneLineListItem", "text": f"{proof}", "height": dp(56),
             "on_release": lambda x=f"{proof}": self.set_id_proof(x)}
            for proof in ["Passport", "Driver's License", "State ID"]
        ]
        self.id_proof_menu = MDDropdownMenu(
            caller=self.ids.id_proof_type,
            items=menu_items,
            width_mult=4
        )

    def set_id_proof(self, proof_type):
        self.ids.chosen_id_proof.text = proof_type
        self.id_proof_menu.dismiss()
    def upload_file(self, proof_type):
        # Create a file chooser dialog for PDF files
        content = BoxLayout(orientation='vertical')
        filechooser = FileChooserIconView(filters=["*.pdf"])

        select_button = Button(text="Select", size_hint=(1, 0.1))
        cancel_button = Button(text="Cancel", size_hint=(1, 0.1))

        content.add_widget(filechooser)
        content.add_widget(select_button)
        content.add_widget(cancel_button)

        # Create popup
        self.popup = Popup(title=f"Select PDF for {proof_type}",
                           content=content,
                           size_hint=(0.9, 0.9))

        # Bind the select button to the function that checks the file and dismisses the popup
        select_button.bind(on_release=lambda x: self.check_file(filechooser.selection))

        # Bind the cancel button to dismiss the popup
        cancel_button.bind(on_release=lambda x: self.popup.dismiss())

        self.popup.open()

    def check_file(self, selection):
        if selection:
            file_path = selection[0]
            # Check if the file size is less than 1MB
            if os.path.getsize(file_path) < 1 * 1024 * 1024:
                self.ids.chosen_id_proof.text = file_path
                self.popup.dismiss()
            else:
                self.show_error_dialog("The file size must be less than 1MB.")
        else:
            self.show_error_dialog("Please select a file.")

    def show_error_dialog(self, message):
        dialog = MDDialog(text=message)
        dialog.open()

    def initialize_pass_menu(self):
        pass_types = ["Weekly", "Quarterly", "Yearly"]
        menu_items = [
            {"viewclass": "OneLineListItem", "text": pass_type, "height": dp(56),
             "on_release": lambda x=pass_type: self.set_pass_type(x)}
            for pass_type in pass_types
        ]
        self.pass_menu = MDDropdownMenu(
            caller=self.ids.pass_type,
            items=menu_items,
            width_mult=4
        )

    def set_pass_type(self, pass_type):
        self.ids.chosen_pass.text = pass_type
        self.pass_menu.dismiss()


class MyApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Amber"
        init_db()
        Builder.load_file('login.kv')
        Builder.load_file('signup.kv')
        Builder.load_file('home.kv')
        Builder.load_file('passes.kv')

        sm = ScreenManager()
        sm.add_widget(LoginPage(name='login'))
        sm.add_widget(HomePage(name='home'))
        sm.add_widget(SignupScreen(name='signup'))
        sm.add_widget(BusTicketPage(name='bus_ticket'))
        sm.add_widget(PassRegistrationPage(name='pass_registration'))

        return sm

    def date_input_filter(self, value, from_undo=False):
        allowed_chars = "0123456789/"
        if all(char in allowed_chars for char in value[-1]):
            parts = value.split("/")
            if len(parts) > 3:
                return value[:-1]
            for part in parts:
                if len(part) > 2:
                    return value[:-1]
            return value
        return value[:-1]

    def validate_date(self, date_text):
        try:
            datetime.strptime(date_text, '%d/%m/%Y')
            return True
        except ValueError:
            return False

    def date_filter(self, value, from_undo):
        # Allow numbers and slashes only
        allowed_chars = "0123456789/"
        if all(char in allowed_chars for char in value):
            return value
        return ''

    def process_destination(self,destination):
        if destination:
            #simulating wallet balance

           wallet_balance=100  #assuming wallet balance
           travel_cost = 20  # assuming cost for the ride
           if wallet_balance>=travel_cost:
               wallet_balance-=travel_cost
               self.generate_qr_code(destination,wallet_balance)
           else:
               print("Insufficient balance")
    def generate_qr_code(self,data,balance):
        #to generate a Qr code
        qr=qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(f"Destination: {data} - Balance: {balance}")
        qr.make(fit=True)
        img=qr.make_image(fill_color="black",back_color="white")
        # Save QR code to a temporary file
        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        img.save(temp.name)
        temp.close()

        # Display the QR code
        self.show_qr_code(temp.name)

        #for displaying the QR code

    def show_qr_code(self, file_path):
        # Display QR Code in a popup
        image = Image(source=file_path, pos_hint={"center_x": 0.5, "center_y": 0.5})
        popup = Popup(title="QR Code", content=image, size_hint=(None, None), size=(300, 300))
        popup.open()
    # def toggle_extra_controls(self, layout):
    #     # Toggle visibility by changing opacity
    #     layout.opacity = 1 if layout.opacity == 0 else 0


    def open_ticket_page(self):
        self.root.current = 'bus_ticket'
    def process_button(self, transport_type):
        print(f"{transport_type} button pressed!")
        # Hide extra controls when other icons are clicked
        self.root.ids.extra_controls_layout.opacity = 0

    def process_passes(self):
        print("Passes button pressed!")
        # Implement functionality for 'Passes'

    def process_tickets(self,layout):
        self.open_ticket_page()

    def process_ticket_submission(self, pickup, destination):
        if pickup and destination:
            print(f"Pickup: {pickup}, Destination: {destination}")
            # Add logic for handling the ticket data here
            self.root.current = 'home'  # Optionally switch back to the home page or other relevant action
        else:
            print("Please enter both pickup and destination locations")
    def switch_to_home(self):
        # This assumes that you have a method or logic to switch views
        self.root.current = 'home'
        self.root.ids.tickets_controls.opacity = 0

    def on_start(self):
        self.menu = MDDropdownMenu(
            width_mult=4,
        )

    def update_autocomplete(self, textfield):
        if not textfield.text.strip():
            self.menu.dismiss()
            return

        # Filter or fetch suggestions based on the textfield input
        suggestions = self.get_suggestions(textfield.text)

        # Clear the menu
        self.menu.items = []
        # Create menu items
        for suggestion in suggestions:
            menu_item = {
                "viewclass": "OneLineListItem",
                "text": suggestion,
                "on_release": lambda x=suggestion: self.set_destination(textfield, x),
            }
            self.menu.items.append(menu_item)

        # Open the menu
        self.menu.caller = textfield
        self.menu.open()

    def get_suggestions(self, query):
        # Example data
        return [loc for loc in ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'] if
                query.lower() in loc.lower()]

    def set_destination(self, textfield, location):
        textfield.text = location
        self.menu.dismiss()


if __name__ == "__main__":
    Window.size = (360, 640)
    #Builder.load_file("login.kv")
    MyApp().run()
