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
        return sm
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
