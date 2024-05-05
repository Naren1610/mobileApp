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
from kivymd.uix.list import OneLineListItem
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.pickers import MDDatePicker

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
               username NVARCHAR(50) UNIQUE NOT NULL,
               password NVARCHAR(255) NOT NULL
           );
       ''')
    conn.commit()
    conn.close()

from hashlib import sha256

def add_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    hashed_password = sha256(password.encode()).hexdigest()
    try:
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
        return True
    except pyodbc.IntegrityError:
        return False
    finally:
        conn.close()

def check_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
    result = cursor.fetchone()
    conn.close()
    if result:
        hashed_password = sha256(password.encode()).hexdigest()
        return hashed_password == result[0]
    return False



class LoginPage(Screen):
    pass

class HomePage(Screen):
    pass
class BusTicketPage(Screen):
    pass


from kivy.uix.popup import Popup
from kivy.uix.label import Label


class PassRegistrationPage(Screen):
    certificate_path = ''
    photo_path = ''

    def show_file_chooser(self, file_type):
        content = FileChooserIconView(filters=self.get_filters(file_type))
        content.bind(on_submit=self.select_file(file_type))
        popup = Popup(title="Select File", content=content, size_hint=(0.9, 0.9))
        popup.open()

    def get_filters(self, file_type):
        if file_type == 'certificate':
            return ['*.pdf', '*.doc', '*.docx']
        elif file_type == 'photo':
            return ['*.jpg', '*.jpeg', '*.png']
        return []

    popup = None  # Reference to the popup

    def show_file_chooser(self, file_type):
        filechooser = FileChooserIconView(filters=['*.*'], size_hint=(1, 0.9))
        filechooser.bind(
            on_submit=lambda instance, selection, touch: self.on_file_selected(instance, selection, touch, file_type))

        layout = BoxLayout(orientation='vertical')
        layout.add_widget(filechooser)

        self.popup = Popup(content=layout, size_hint=(0.9, 0.9), title="Select File")
        self.popup.open()

    def on_file_selected(self, instance, selection, touch, file_type):
        if selection:
            file_path = selection[0]  # Assuming the user selects one file
            file_name = basename(file_path)  # Extracts the file name from the path
            if file_type == 'certificate':
                self.ids.certificate_name.text = f"Selected: {file_name}"
                self.certificate_path = file_path
            elif file_type == 'photo':
                self.ids.photo_name.text = f"Selected: {file_name}"
                self.photo_path = file_path

        if self.popup:
            self.popup.dismiss()
            self.popup = None

    def clear_selection(self, file_type):
        if file_type == 'certificate':
            self.ids.certificate_name.text = ""
            self.certificate_path = None
        elif file_type == 'photo':
            self.ids.photo_name.text = ""
            self.photo_path = None
    def submit_registration(self):
        if not self.validate_fields():
            return
        print(f"Processing registration with the files: {self.certificate_path}, {self.photo_path}")
        # Process registration here
        Popup(content=Label(text='Registration Successful!'), size_hint=(None, None), size=(400, 400)).open()

    def validate_fields(self):
        valid = True
        if not self.ids.full_name.text:
            self.ids.full_name_error.text = 'Full name is required.'
            valid = False
        else:
            self.ids.full_name_error.text = ''

        if not self.ids.dob.text:
            self.ids.dob_error.text = 'Date of birth is required.'
            valid = False
        else:
            self.ids.dob_error.text = ''

        if not self.ids.institution.text:
            self.ids.institution_error.text = 'Institution name is required.'
            valid = False
        else:
            self.ids.institution_error.text = ''

        if not self.certificate_path:
            self.ids.certificate_error.text = 'Please select a certificate.'
            valid = False
        else:
            self.ids.certificate_error.text = ''

        if not self.photo_path:
            self.ids.photo_error.text = 'Please select a photo.'
            valid = False
        else:
            self.ids.photo_error.text = ''

        return valid


class MyApp(MDApp):

    def signup(self, username, password):
        if self.validate_password(password):
            if add_user(username, password):
                print("User created successfully!")
            else:
                print("Username already exists!")
        else:
            print("Password does not meet the requirements!")



    def signin(self, username, password):
        if check_user(username, password):
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

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Amber"
        init_db()
        Builder.load_file('login.kv')

        sm = ScreenManager()
        sm.add_widget(LoginPage(name='login'))
        sm.add_widget(HomePage(name='home'))
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
