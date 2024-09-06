from calls import *
import sys
from PyQt5.QtWidgets import QApplication
from GUI import NumberInputWindow

def main():
    response, access_token = refresh_token()
    
    # Obtén los datos del cliente usando el token de acceso
    getCustomerData(access_token)
    
    # Autentica al usuario y obtiene la información del usuario
    response2 = auth_client.get_user_info(access_token=access_token)
    print(response2.text)
    print("\n\n\n")
    
    app = QApplication(sys.argv)
    window = NumberInputWindow(access_token)  # Pass the access_token here
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()


