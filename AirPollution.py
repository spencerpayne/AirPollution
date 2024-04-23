# CSC 315 Database Project
# John, Mridula, Tahmina, Derrick
# 
# files needed to run:
# tkinter, tkcalendar, pyodbc, tkintermapview. use pip to install them.
# Also needed: SQL Server
#
import tkinter as tk    # gui
from tkinter import *   
import pyodbc   # our database connector
import tkcalendar   # calendar
import tkintermapview   # map
from tkinter import ttk # ttk is apart of TKinter, gives us the option to use a combobox
from tkinter import messagebox  # messagebox for the sort methods
from datetime import datetime   # datetime is used to convert the date to a year for the Lung Cancer table.

class LoginPage(tk.Tk):
    def __init__(self):
        super().__init__()
        #   Creates a list of cities to load into the combobox
        self.cities = ["Shreveport", "Alexandria", "Monroe", "BatonRouge", "Hammond", "Houma",
                       "Chalmette", "Geismar", "Kenner", "Lafayette", "Marrero", "PortAllen", "Vinton", "NewOrleans"]

        # Update the window to calculate its width and height
        self.update_idletasks()
        self.title("Login")

        # Calculate the center coordinates relative to the screen
        x = (self.winfo_screenwidth() - self.winfo_reqwidth()) / 2
        y = (self.winfo_screenheight() - self.winfo_reqheight()) / 2

        # Set the window's geometry to be centered on the screen
        self.geometry(f"+{int(x)}+{int(y)}")
        self.resizable(False, False)

        self.username_label = ttk.Label(self, text="Username:")
        self.username_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")

        self.username_entry = ttk.Entry(self)
        self.username_entry.grid(row=0, column=1, padx=10, pady=10)

        self.password_label = ttk.Label(self, text="Password:")
        self.password_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")

        self.password_entry = ttk.Entry(self, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)

        self.login_button = ttk.Button(self, text="Login", command=self.login)
        self.login_button.grid(row=2, column=0, columnspan=2,
                               padx=10, pady=10, sticky="ew")
    #   gets the user login, for example: sa, user, or Data analyst
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        try:    # then it puts the username and password into the connection string.
                # this login is for getting into the actual program
            AirPollutionDB = {
                'server': 'localhost',  # if not localhost, change this to the correct IP address.
                'database': 'AirPollutionLungCancerDB',
                'username': username,  # Use the username passed from the login screen
                'password': password,  # Use the password passed from the login screen
                'driver': '{ODBC Driver 18 for SQL Server}'
            }

            # Connect to the database using the provided credentials
            self.connection = pyodbc.connect(
                f"DRIVER={AirPollutionDB['driver']};SERVER={
                    AirPollutionDB['server']};DATABASE={AirPollutionDB['database']};"
                f"UID={AirPollutionDB['username']};PWD={
                    AirPollutionDB['password']};TrustServerCertificate=yes"
            )
            #   opens the application after authentication
            self.open_map_app()

        except Exception as e:
            print("Error authenticating user:", e)
    # function to actually open the map app. it gets the user and password and actually uses them to log in.
    def open_map_app(self):
        # Retrieve username and password before destroying the window
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Destroy the login window
        self.destroy()

        try:    # logs in with username and password
            # Open the main application window with the retrieved username and password
            app = LouisianaMapApp(
                username=username, password=password, cities=self.cities)   # load the list of cities
            app.mainloop()
        except Exception as e:
            messagebox.showerror(
                "Error", f"An error occurred while opening the main application: {e}")

# main class with our map
class LouisianaMapApp(tk.Tk):
    def __init__(self, username, password, admin=False, cities=None):
        super().__init__()
        self.cities = cities if cities else []  # populates the city combobox.
        self.marker_dict = {}
        self.username = username
        if username == "sa":    # this adds the "add data" button, only if user 'sa' is logged in.
            admin = True
        self.password = password
        self.connection = None  # Initialize the connection attribute
        self.admin = admin

        # Establish the database connection
        self.connect_to_database()  # calls the connect to database function

        # Other initialization code remains unchanged
        self.title("Air Quality of Louisiana")
        self.geometry("1300x700")

        self.create_widgets()   # calls the create widgets function

        # Call the loadCities method to populate the city combobox
        self.loadCities()

    def connect_to_database(self):  # we call the method again, this time to actually connect to the database
        try:
            AirPollutionDB = {
                'server': 'localhost',
                'database': 'AirPollutionLungCancerDB',
                'username': self.username,  # uses the input username from the login screen
                'password': self.password,  # uses the input password from the login screen
                'driver': '{ODBC Driver 18 for SQL Server}'
            }

            # Connect to the database using the provided credentials
            self.connection = pyodbc.connect(
                f"DRIVER={AirPollutionDB['driver']};SERVER={
                    AirPollutionDB['server']};DATABASE={AirPollutionDB['database']};"
                f"UID={AirPollutionDB['username']};PWD={
                    AirPollutionDB['password']};TrustServerCertificate=yes"
            )
        except Exception as e:
            print("Error establishing database connection:", e)

    # this method creates all of the widgets for our main page: calendar, map, entries, etc...
    # it also places them accordingly
    def create_widgets(self):
        self.date_label = tk.Label(self, text="Date: ")
        self.date_label.grid(column=0, row=2, sticky="NW", pady=(100, 10))

        self.calendar = tkcalendar.Calendar(self, year=2024, month=3, day=22)
        self.calendar.grid(column=1, row=2, rowspan=2,
                           sticky="NW", pady=(100, 10))

        self.year_label = tk.Label(self, text="Year: ")
        self.year_label.grid(column=2, row=1, sticky="E")

        years = list(range(2010, 2025))
        self.selected_year = tk.StringVar()  # Variable to store the selected year
        self.year_combobox = ttk.Combobox(
            self, textvariable=self.selected_year, state="readonly", values=years)
        self.year_combobox.grid(column=3, row=1, sticky="W")

        self.select_year_button = tk.Button(
            self, text="Search with Sort", command=self.sortSearch)
        self.select_year_button.grid(column=4, row=1, sticky="W")

        self.add_submit_button = tk.Button(
            self, text="Search with Full Date and City", command=self.on_user_input)
        self.add_submit_button.grid(column=1, row=4, sticky="W")

        self.sort_method_label = tk.Label(self, text="Sort Method:")
        self.sort_method_label.grid(
            column=0, row=5, sticky="NE", padx=(10, 0), pady=(100, 10))

        self.sort_methods = ["Highest", "Lowest", "Average"]
        self.selected_sort_method = tk.StringVar()
        self.sort_method_combobox = ttk.Combobox(
            self, textvariable=self.selected_sort_method, state="readonly", values=self.sort_methods)
        self.sort_method_combobox.grid(
            column=1, row=5, sticky="NW", pady=(100, 10))

        self.add_clear_button = tk.Button(
            self, text="Clear All", command=self.clear_input)
        self.add_clear_button.grid(column=3, row=4, sticky="W")

        self.city_label = tk.Label(self, text="Selected City:")
        self.city_label.grid(column=0, row=1, sticky="NW")

        self.selected_city = tk.StringVar()  # Variable to store the selected city
        self.city_combobox = ttk.Combobox(
            self, textvariable=self.selected_city, state="readonly")
        self.city_combobox.grid(column=1, row=1, sticky="NW")

        self.map_widget = tkintermapview.TkinterMapView(
            self, width=500, height=500, corner_radius=5)
        self.map_widget.grid(column=3, row=2, padx=(120, 10), pady=(
            50, 10), rowspan=5, columnspan=5, sticky="SE")
        self.map_widget.set_position(30.9843, -91.9623)
        self.map_widget.set_zoom(7)

        if self.admin:  # if user = admin, add the add more data
            self.add_data_widget = tk.Button(
                self, text="Add Data", command=self.open_new_data_window)
            self.add_data_widget.grid(column=2, row=4, sticky="W")

        self.output_label = tk.Label(self, text="Output:")
        self.output_label.grid(column=2, row=5, sticky="SW")

        self.air_quality_labels = {}
        labels = ["PM 2.5", "Lung Cancer Cases"]
        for i, label_text in enumerate(labels):
            label = tk.Label(self, text=f"{label_text}")
            label.grid(column=1, row=6+i*30, sticky="SE")
            entry = tk.Entry(self, width=20)
            entry.grid(column=2, row=6+i*30, sticky="SE")
            self.air_quality_labels[label_text] = entry

    # method that converts the City to Parish, and then gets the corresponding PM2.5 values for that city.
    def fetch_air_quality_data(self, city, date):
        try:
            cursor = self.connection.cursor()
            query = """
                SELECT apd.PM25
                FROM AirPollutionLungCancerDB.dbo.AirPollutionData apd
                INNER JOIN AirPollutionLungCancerDB.dbo.CityToParish ctp ON apd.City = ctp.City
                WHERE apd.Date = ? AND ctp.City = ?
            """
            cursor.execute(query, (date, city))
            row = cursor.fetchone()
            return row[0] if row else None
        except Exception as e:
            print("Error fetching air quality data:", e)
            return None

    # similar to the method above, it fetches lung cancer rates.
    def fetch_lung_cancer_rates(self, city, year):
        try:
            cursor = self.connection.cursor()
            query = """
                SELECT lcr.CountOfCases
                FROM LungCancerRates lcr
                INNER JOIN CityToParish ctp ON lcr.Parish = ctp.Parish
                WHERE lcr.Year = ? AND ctp.City = ?
            """
            cursor.execute(query, (year, city))
            row = cursor.fetchone()
            return row[0] if row else None
        except Exception as e:
            print("Error fetching Lung Cancer Rates:", e)
            return None

    # this method clears text from the entries, and removes the markers from the map.
    def clear_input(self):
        for widget in self.winfo_children():
            # Check if the widget is an entry box
            if isinstance(widget, tk.Entry):
                # Clear the entry box
                widget.delete(0, 'end')
            # Remove all markers from the map
        for marker_info in self.marker_dict.values():
            self.map_widget.delete(marker_info["marker"])

            # Clear the marker dictionary
        self.marker_dict = {}

    # loads the cities into the combobox.
    def loadCities(self):
        try:
            cities = ["Shreveport", "Alexandria", "Monroe", "BatonRouge", "Hammond", "Houma", "Chalmette",
                      "Geismar", "Kenner", "Lafayette", "Marrero", "PortAllen", "Vinton", "NewOrleans"]
            print("Number of cities:", len(cities))
            self.city_combobox["values"] = cities
            self.selected_city.set(cities[0])  # Set the default selected city
        except Exception as e:
            print("Error in loadCities:", e)

    # method that gets the user input from the main application page. City and Date and then passes it to the database.
    def on_user_input(self):
        city = self.selected_city.get()
        date_str = self.calendar.get_date()
        date_obj = datetime.strptime(date_str, '%m/%d/%y')
        formatted_date = date_obj.strftime('%Y-%m-%d')
        formatted_year = date_obj.strftime('%Y')
        coords = self.fetch_coordinates(city)

        # Clear PM 2.5 and Lung Cancer Rate data entry fields
        self.air_quality_labels["PM 2.5"].delete(0, tk.END)
        self.air_quality_labels["Lung Cancer Cases"].delete(0, tk.END)

        # Pass the connection object to the fetch_air_quality_data method
        air_quality_data = self.fetch_air_quality_data(city, formatted_date)

        print("Air quality data:", air_quality_data)

        if air_quality_data is not None:
            if air_quality_data:
                self.air_quality_labels["PM 2.5"].insert(
                    tk.END, air_quality_data)
                print("Setting PM 2.5 marker...")
            else:
                print("No air quality data found for the provided city.")
        else:
            print("No air quality data found for the provided city.")

        # Pass the connection object to the fetch_lung_cancer_rates method
        lung_cancer_data = self.fetch_lung_cancer_rates(city, formatted_year)
        print("Lung cancer data:", lung_cancer_data)

        if lung_cancer_data is not None:
            if lung_cancer_data:
                self.air_quality_labels["Lung Cancer Cases"].insert(
                    tk.END, lung_cancer_data)
                print("Setting lung cancer marker...")
                # Create a marker only if there is lung cancer data available
                self.update_marker(coords, city, formatted_date,
                                   air_quality_data, lung_cancer_data)
            else:
                print("No Cancer Rate Data found")
        else:
            print("No Cancer Rate Data found")

    # method that adds the marker to the map and adds the city, date, PM2.5, and Lung Cancer Count to the marker.
    def update_marker(self, coords, city, date, air_quality_data, lung_cancer_data):
        print("Updating marker...")
        print("Coordinates:", coords)
        print("City:", city)
        print("Date:", date)
        print("Air quality data:", air_quality_data)
        print("Lung cancer data:", lung_cancer_data)

        # Check if marker exists for the coordinates
        if coords in self.marker_dict:
            print("Marker already exists.")

            # If marker exists, check if the new city is the same as the city of the existing marker
            existing_marker_city = self.marker_dict[coords]["city"]
            if existing_marker_city == city:
                print("City matches existing marker.")

                # If the cities match, update the text of the existing marker with new data
                marker_text = f"City: {city}, Date: {date}\nPM 2.5: {
                    air_quality_data if air_quality_data else 'N/A'}\nLung Cancer Cases: {lung_cancer_data if lung_cancer_data else 'N/A'}"
                self.marker_dict[coords]["marker"].set_text(marker_text)
                return
            else:
                print("City does not match existing marker. Removing previous marker...")
                # If the cities don't match, remove the previous marker
                self.map_widget.remove_marker(
                    self.marker_dict[coords]["marker"])
                del self.marker_dict[coords]
        # if there is no marker, create one.
        print("Creating new marker...")
        marker_text = f"City: {city}\nDate: {date}\nPM 2.5: {
            air_quality_data if air_quality_data else 'N/A'}\nLung Cancer Cases: {lung_cancer_data if lung_cancer_data else 'N/A'}"
        new_marker = self.map_widget.set_marker(
            coords[0], coords[1], text=marker_text, font=('Arial', 10))
        self.marker_dict[coords] = {"marker": new_marker, "city": city}

    # this method is so the map knows where to place a marker depending on the city selection. 
    def fetch_coordinates(self, city):
        cities = {
            "Alexandria": (31.332153069519233, -92.478657421875),
            "BatonRouge": (30.4515, -91.1871),
            "Lafayette": (30.2241, -92.0198),
            "Shreveport": (32.5252, -93.7502),
            "Vinton": (30.1911, -93.5814),
            "Monroe": (32.5093, -92.1193),
            "Hammond": (30.5044, -90.4612),
            "Houma": (29.5958, -90.7195),
            "Chalmette": (29.9466, -89.9792),
            "Geismar": (30.2193, -91.0065),
            "Kenner": (29.9941, -90.2417),
            "Marrero": (29.8994, -90.1004),
            "PortAllen": (30.4475, -91.2073),
            "NewOrleans": (29.9511, -90.0715)
        }

        # Return coordinates for the specified city if found
        return cities.get(city)

    # this method uses the stored procedures to output either the lowest, highest, or average lung cancer cases depending on the user's 
    # input of city, year, and sort method.
    def sortSearch(self):
        sort_method = self.selected_sort_method.get()   # gets the sort method from the combobox.
        try:
            highest_cancer_count = None
            highest_pm_value = None
            
            cursor = self.connection.cursor()

            # Get the selected parish and year from the dropdown menu and year entry
            # Assuming the parish is selected from the city combobox
            city = self.selected_city.get()
            selected_year = self.selected_year.get()
            print(city, selected_year)

            # Validate if the year entry is not empty and is a valid integer
            if selected_year:
                try:
                    selected_year = (selected_year)
                except ValueError:
                    messagebox.showerror("Error", "Please enter a valid year.") 
                    return
                
                # Highest_Lung_Cancer_Cases Stored Procedure
                if sort_method == "Highest":
                    cursor.execute("""
                        DECLARE @Given_Year INT = ?;
                        DECLARE @Given_City VARCHAR(50) = ?;
                        DECLARE @Highest_Cancer_Count INT;
                        DECLARE @Highest_PM_Value FLOAT;

                        EXEC Highest_Lung_Cancer_Cases 
                            @Given_Year = @Given_Year,
                            @Given_City = @Given_City,
                            @Highest_Cancer_Count = @Highest_Cancer_Count OUTPUT,
                            @Highest_PM_Value = @Highest_PM_Value OUTPUT;

                        SELECT @Highest_Cancer_Count AS Highest_Cancer_Count, @Highest_PM_Value AS Highest_PM_Value;
                    """,
                                selected_year,
                                city)   # uses selected year and city for the input.

                    # Fetch the output parameters from the cursor
                    row = cursor.fetchone()

                    # Get the actual output parameter values
                    highest_cancer_count = row.Highest_Cancer_Count
                    highest_pm_value = row.Highest_PM_Value

                    # pops up a message with the appropriate information for the user.
                    messagebox.showinfo("Sort Search Result", f"City: {city}\nYear: {selected_year}\nHighest Cancer Count: {highest_cancer_count}\nHighest PM Value: {highest_pm_value}")
                    
                elif sort_method == "Lowest":
                        cursor.execute("""
                            DECLARE @Given_Year INT = ?;
                            DECLARE @Given_City VARCHAR(50) = ?;
                            DECLARE @Lowest_Cancer_Count INT;
                            DECLARE @Lowest_PM_Value FLOAT;

                            EXEC Lowest_Lung_Cancer_Cases 
                                @Given_Year = @Given_Year,
                                @Given_City = @Given_City,
                                @Lowest_Cancer_Count = @Lowest_Cancer_Count OUTPUT,
                                @Lowest_PM_Value = @Lowest_PM_Value OUTPUT;

                            SELECT @Lowest_Cancer_Count AS Lowest_Cancer_Count, @Lowest_PM_Value AS Lowest_PM_Value;
                        """,
                                selected_year,
                                city)

                    # Fetch the output parameters from the cursor
                        row = cursor.fetchone()

                    # Get the actual output parameter values
                        lowest_cancer_count = row.Lowest_Cancer_Count
                        lowest_pm_value = row.Lowest_PM_Value

                        messagebox.showinfo("Sort Search Result", f"City: {city}\nYear: {selected_year}\nLowest Cancer Count: {lowest_cancer_count}\nLowest PM Value: {lowest_pm_value}")
                    # Print the output parameters
                elif sort_method == "Average":
                        cursor.execute("""
                            DECLARE @Given_Year INT = ?;
                            DECLARE @Given_City VARCHAR(50) = ?;
                            DECLARE @Average_Cancer_Count INT;
                            DECLARE @Average_PM25 FLOAT;

                            EXEC Average_Lung_Cancer_Cases 
                                @Given_Year = @Given_Year,
                                @Given_City = @Given_City,
                                @Average_Cancer_Count = @Average_Cancer_Count OUTPUT,
                                @Average_PM25 = @Average_PM25 OUTPUT;

                            SELECT @Average_Cancer_Count AS Average_Cancer_Count, @Average_PM25 AS Average_PM25;
                        """,
                                    selected_year,
                                    city)

                        # Fetch the output parameters from the cursor
                        row = cursor.fetchone()

                    # Get the actual output parameter values
                        average_cancer_count = row.Average_Cancer_Count
                        average_pm_value = row.Average_PM25

                    # Messagebox that informs the user of the output.
                        messagebox.showinfo("Sort Search Result", f"City: {city}\nYear: {selected_year}\nAverage Cancer Count: {average_cancer_count}\nAverage PM Value: {average_pm_value}")

        except pyodbc.Error as e:
             # Handle any pyodbc errors
            messagebox.showerror("Error", f"Error performing sort search: {e}")

    # method that actually opens the window and loads the cities.
    def open_new_data_window(self):
        try:
            # Pass your predefined list of cities to the create_new_data_window method
            self.create_new_data_window(self.cities)
        except Exception as e:
            print("Error opening new data window:", e)

    # method for opening the new data window. Called when the user presses "Add Data", creates widgets and more for the window.
    def create_new_data_window(self, city_names):
        try:
            top = Toplevel()
            top.geometry("400x400")
            top.title("Add New Data")

            city_label = Label(top, text="City: ")
            city_label.grid(column=1, row=1)

            # Extract city names from the cities list
            city_names = self.cities
            self.selected_city = tk.StringVar()  # Variable to store the selected city
            self.city_combobox = ttk.Combobox(
                top, textvariable=self.selected_city, state="readonly", values=city_names)
            self.city_combobox.grid(column=2, row=1, sticky="NW")

            date_label = Label(top, text="Date: ")
            date_label.grid(column=1, row=2)

            self.date = tkcalendar.Calendar(top, font=("Arial", 8))
            self.date.grid(column=2, row=2)

            pm25_label = Label(top, text="PM 2.5: ")
            pm25_label.grid(column=1, row=3)

            self.pm_25_entry = Entry(top, width=25)
            self.pm_25_entry.grid(column=2, row=3)

            cancer_data_label = Label(top, text="Lung Cancer Cases: ")
            cancer_data_label.grid(column=1, row=4)

            self.cancer_data_entry = Entry(top, width=25)
            self.cancer_data_entry.grid(column=2, row=4)

            rate_label = Label(top, text="Rate: ")
            rate_label.grid(column=1, row=5)

            self.rate_entry = Entry(top, width=25)
            self.rate_entry.grid(column=2, row=5)

            population_label = Label(top, text="Population: ")
            population_label.grid(column=1, row=6)

            self.population_entry = Entry(top, width=25)
            self.population_entry.grid(column=2, row=6)

            submit_button = Button(top, text="Submit", command=self.add_data)
            submit_button.grid(column=1, row=7)
        except Exception as e:
            print("Error creating new data window:", e)

    # this method is for the submitting data to the database, it gets the entries from the user and correctly formats them.
    def add_data(self):
        try:
            # Get data from the entry fields
            city = self.selected_city.get()
            date_str = self.date.get_date()
            date_obj = datetime.strptime(date_str, '%m/%d/%y')
            formatted_date = date_obj.strftime('%Y-%m-%d')
            pm25 = self.pm_25_entry.get()
            lung_cancer_data = self.cancer_data_entry.get()
            population = self.population_entry.get()
            rate = self.rate_entry.get()

            # Check if pm25, lung_cancer_data, population, and rate can be converted to appropriate types
            if pm25.isdigit() and lung_cancer_data.isdigit() and population.isdigit() and '.' in rate:
                # Convert the values to appropriate types
                pm25 = int(pm25)
                lung_cancer_data = int(lung_cancer_data)
                population = int(population)
                rate = float(rate)

                # Extract the year from the date - this is important for the LungCancerRates table.
                year = date_obj.year

                # Check if the data already exists in the database
                if self.check_existing_data(formatted_date, city, year):
                    messagebox.showinfo(
                        "Data Exists", "Data already exists in the database for the selected date, city, and year.")
                else:
                    # If data does not exist, proceed with insertion
                    self.insert_in_air_pollution_db(formatted_date, city, pm25)
                    self.insert_in_lung_cancer_db(
                        year, city, rate, lung_cancer_data, population)
                    messagebox.showinfo(
                        "Success", "New data added successfully.")

            else:
                # Show error message if input is invalid
                messagebox.showerror(
                    "Input Error", "Invalid input. Please enter valid integer values for PM 2.5, Lung Cancer Cases, and Population, and a valid float value for Rate.")
        except Exception as e:
            # Show error message for any other exception
            messagebox.showerror("Error", f"Error adding new data: {e}")

    # since our database does not like duplicate data, this method checks that data does not already exist before entering it into database.
    def check_existing_data(self, date, city, year):
        try:
            cursor = self.connection.cursor()
            query = "SELECT COUNT(*) FROM AirPollutionData WHERE Date = ? AND City = ?"
            cursor.execute(query, (date, city))
            result = cursor.fetchone()
            if result and result[0] > 0:
                return True  # Data already exists
            else:
                return False  # Data does not exist
        except Exception as e:
            print("Error checking existing data:", e)
            return False  # Assume data does not exist in case of error

    # this method gets the date in yyyy-mm-dd format, city, and pm2.5. It then inserts it into the AirPollutionRates table.
    def insert_in_air_pollution_db(self, formatted_date, city, pm25):
        try:
            cursor = self.connection.cursor()
            cursor.execute("EXEC Insert_In_Air_Pollution_DB ?, ?, ?",   # call the stored procedure
                           (formatted_date, city, pm25))
            self.connection.commit()
            print("Data inserted into Air Pollution DB successfully")
        except Exception as e:
            error_message = f"Error inserting data into Air Pollution DB: {e}"
            print(error_message)
            messagebox.showerror("Error", error_message)

    # this method gets the year, city, lung cancer rate, count, and population. It converts the city to the corresponding parish in the CityToParish table
    def insert_in_lung_cancer_db(self, year, city, rate, lung_cancer_data, population):
        try:
            cursor = self.connection.cursor()

            # Fetch the corresponding parish for the given city from the CityToParish table
            cursor.execute(
                "SELECT Parish FROM CityToParish WHERE City = ?", (city,))
            result = cursor.fetchone()
            if result:
                parish = result[0]
            else:
                raise ValueError(f"No parish found for city: {city}")

            # Insert data into LungCancerRates table with the fetched parish - uses stored procedure
            cursor.execute("{CALL Insert_In_Lung_Cancer_DB (?, ?, ?, ?, ?)}",
                           (year, parish, rate, lung_cancer_data, population))
            self.connection.commit()
        except Exception as e:
            messagebox.showerror(
                "Error", f"Error inserting data into Lung Cancer DB: {e}")

# crucial for the program to open.
if __name__ == "__main__":
    login_page = LoginPage()
    login_page.mainloop()
