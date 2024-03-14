# Louisiana Air Quality Map

This application provides a visual representation of air quality data for different locations in Louisiana. It allows users to select specific coordinates on a map or input coordinates manually to retrieve air quality information. The data is fetched from a SQL Server database named "AirPollution".

## Required Packages

- tkinter
- PIL (Python Imaging Library)
- pyodbc

- pip install tkinter
- pip install pillow
- pip install pyodbc

## How to Use

1. **Launch the Application**: Run the Python script `LouisianaMapApp.py` to launch the application.

2. **Select Coordinates**: There are three ways to select coordinates:
   - Enter coordinates manually in the provided entry box. Use the format: `latitude, longitude` (e.g., `92.4324, -91.43423`). Press Enter to fetch the air quality data.
   - Click on the map to select coordinates visually.
   - Choose from the list of available coordinates in the coordinate bank.

3. **View Air Quality Data**: Once coordinates are selected, the application displays air quality data including CO2 levels, PM2.5 levels, PM10 levels, temperature, and humidity in the corresponding entry fields.

4. **Coordinate Bank**: The application maintains a list of available coordinates fetched from the database. Users can select coordinates from this list for quick access.

5. **Adding New Data into the Database**: To add new data to the database, simply choose a coordinate, and make sure it is selected in the "selected coordinates" field. Then, fill in your data in the CO2, PM2.5, PM10, Temperature, and Humidity fields. Finally, you can click the "Add New Data" button, and your data will be added to the database.

## Screenshots

![](/Screenshots/AirQualityImage1.png/)
![](/Screenshots/AirQualityImage2.png/)
![](/Screenshots/AirQualityImage3.png/)
