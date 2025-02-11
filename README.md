# Flask + Vue.js Authentication System

## Overview

This project provides a simple authentication system built with **Flask** (for the backend) and **Vue.js** (for the frontend). It includes a login and signup page, leveraging **hash authentication** and **role-based authorization** to manage user access.

## Features

### **Secure Login**
- The system uses **hashed passwords** to ensure secure login. User credentials are stored securely, preventing unauthorized access.

### **Role-Based Authorization**
- Users can have different roles such as **root**, **member**, and **coach**. The access to various features of the system is controlled based on the user role.

### **Easy User Registration**
- Users can easily create new accounts using a simple sign-up form. After registration, they can log in and manage their credentials.

## Technologies Used

- **Flask**: A lightweight Python web framework used for creating the backend of the application.
- **Vue.js**: A progressive JavaScript framework used for building the frontend and handling dynamic interactions.
- **Vue Router**: Handles navigation between pages, such as the login and registration pages.
- **werkzeug.security**: Used for password hashing to ensure secure user authentication.

## Getting Started

### Prerequisites

Before running the project, ensure you have the following installed:

- **Python 3.x** (for the backend)
- **Flask** and **Flask-SQLAlchemy** for the backend setup

### Installation Steps

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-repository/flask-vue-authentication.git
   cd flask-vue-authentication
   ```

2. **Backend Setup:**

   - Install the Python dependencies:

     ```bash
     pip install -r requirements.txt
     ```

   - Set up the database (if using SQLite):

     ```bash
     py initial_data.py
     ```


3. **Run the Flask Backend:**

   In the root directory of the project, start the Flask server:

   ```
   py main.py
   ```

   The application will now be accessible on `http://127.0.0.1:5000`.

## Deployment

If you want to deploy the project to a production server, you can use tools like **Docker**, **Heroku**, or **AWS** to host both the Flask backend and Vue.js frontend.

## Contributing

Contributions are welcome! If you have suggestions or improvements, feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
