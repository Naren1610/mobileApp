from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from plyer import filechooser
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



class PassRegistrationScreenManager(ScreenManager):
    def go_to_next(self, current_screen):
        if current_screen == 'personal_details':
            self.current = 'education_information'
        elif current_screen == 'education_information':
            self.current = 'upload_files'

    def go_to_prev(self, current_screen):
        if current_screen == 'education_information':
            self.current = 'personal_details'
        elif current_screen == 'upload_files':
            self.current = 'education_information'

class PersonalDetailsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding='10dp', spacing='10dp')
        layout.add_widget(MDTextField(hint_text="Father's Name"))
        layout.add_widget(MDTextField(hint_text="Current Residential Address"))
        layout.add_widget(MDRaisedButton(text="Next", on_release=lambda x: self.manager.go_to_next('personal_details')))
        self.add_widget(layout)

class EducationInformationScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding='10dp', spacing='10dp')
        layout.add_widget(MDTextField(hint_text="School/College Details"))
        layout.add_widget(MDRaisedButton(text="Previous", on_release=lambda x: self.manager.go_to_prev('education_information')))
        layout.add_widget(MDRaisedButton(text="Next", on_release=lambda x: self.manager.go_to_next('education_information')))
        self.add_widget(layout)

class UploadFilesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding='10dp', spacing='10dp')
        layout.add_widget(MDRaisedButton(text="Upload Photo", on_release=self.select_photo))
        layout.add_widget(MDLabel(id='photo_name'))
        layout.add_widget(MDRaisedButton(text="Upload ID Proof", on_release=self.select_id_proof))
        layout.add_widget(MDLabel(id='id_proof_name'))
        layout.add_widget(MDRaisedButton(text="Previous", on_release=lambda x: self.manager.go_to_prev('upload_files')))
        self.add_widget(layout)


    def select_photo(self):
        # Use plyer filechooser to select a photo
        print("method triggered")
        path = filechooser.open_file(filters=[["Images", "*.jpg", "*.jpeg", "*.png"]])
        if path:
            self.photo_name.text = path[0]  # Update the photo_name label with the selected path

    def select_id_proof(self):
        # Use plyer filechooser to select an ID proof
        path = filechooser.open_file(filters=[["Documents", "*.pdf"]])
        if path:
            self.id_proof_name.text = path[0]  # Update the id_proof_name label with the selected path

    def open_pass_menu(self):
        # Dropdown menu for selecting the pass type
        pass_types = ["Monthly", "Quarterly", "Yearly"]
        menu_items = [{"viewclass": "OneLineListItem", "text": pass_type, "height": dp(56),
                       "on_release": lambda x=pass_type: self.set_pass_type(x)}
                      for pass_type in pass_types]
        self.pass_menu = MDDropdownMenu(
            caller=self.ids.pass_type,  # Ensure there is an element with id 'pass_type' in the kv layout
            items=menu_items,
            width_mult=4
        )

    def set_pass_type(self, pass_type):
        self.ids.chosen_pass.text = pass_type  # Update the chosen_pass label with the selected pass type
        self.pass_menu.dismiss()  # Dismiss the menu after selection
class PassRegistrationContainer(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create and add the PassRegistrationScreenManager to this container screen
        self.pass_reg_manager = PassRegistrationScreenManager()
        self.add_widget(self.pass_reg_manager)
        # Add individual registration step screens to the PassRegistrationScreenManager
        self.pass_reg_manager.add_widget(PersonalDetailsScreen(name='personal_details'))
        self.pass_reg_manager.add_widget(EducationInformationScreen(name='education_information'))
        self.pass_reg_manager.add_widget(UploadFilesScreen(name='upload_files'))


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
        sm.add_widget(PassRegistrationContainer(name='pass_registration'))

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
