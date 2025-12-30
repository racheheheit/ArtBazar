ArtBazar – Online Art Marketplace
ArtBazar is a full-stack web application designed to bridge the gap between artists and buyers through a modern digital marketplace. The platform enables artists to showcase their artwork online while providing users with a seamless browsing and purchasing experience. The project focuses on clean UI design, structured backend development, and scalable database architecture.

Features -
ArtBazar provides a complete user authentication system that supports account creation and login functionality. The project includes a Google Sign-In integration setup, allowing for easy extension of third-party authentication. Users can browse artworks displayed in a gallery-style layout, add selected items to a shopping cart, and manage their cart contents before proceeding to checkout. The cart-to-order workflow is planned as part of future development to complete the purchasing lifecycle.
The platform supports structured artwork listings with images and descriptive details. The interface is fully responsive, ensuring compatibility across desktops, tablets, and mobile devices. A modern gradient-based UI theme is used throughout the application, and the backend architecture is secured using Flask to manage routing and data flow.

Tech Stack -
The frontend of ArtBazar is built using HTML5 and CSS3 with a strong emphasis on responsive web design principles. Custom styling and typography are implemented using Google Fonts, specifically Poppins and Momo Trust Display, to achieve a polished visual appearance.
The backend is developed in Python using the Flask framework, enabling clean separation of routes, logic, and templates. MySQL is used as the primary database for storing user data, artwork information, and cart-related records. The authentication layer is structured to support Google Sign-In, with both frontend placeholders and backend logic prepared for integration.

Project Structure -
The project follows a structured directory layout to ensure maintainability and clarity. Static assets such as CSS files and images are stored within the static directory, while HTML templates are organized inside the templates directory. The main application logic is handled through the app.py file, and all required dependencies are listed in the requirements.txt file. The README.md file documents the project and its usage.

Cart System -
The cart system is implemented using a dedicated Cart table that stores essential information such as cart identifiers, customer identifiers, artwork identifiers, quantity, timestamps, and status fields. Foreign key constraints are intentionally omitted during the initial development phase to allow flexibility while testing features. Backend routes have been implemented to support adding items to the cart, viewing cart contents, and removing items. A checkout mechanism is planned that will transfer cart data into an Orders table for order processing.

UI and Design -
The user interface follows a modern visual language using a linear gradient background defined by the colors #c6f3ff and #0a3359. The design includes rounded cards and buttons to improve accessibility and aesthetics. A clean hero section is placed on the landing page to guide users toward key actions. The layout is fully responsive, and hover effects and transitions are applied to enhance user interaction.
