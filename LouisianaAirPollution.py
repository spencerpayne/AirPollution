import tkinter as tk
from tkinter import *
import pyodbc
import tkcalendar
import tkintermapview
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime

class LoginPage(tk.Tk):
    def __init__(self):
        super().__init__()
        self.cities = ["Shreveport", "Alexandria", "Monroe", "BatonRouge", "Hammond", "Houma", "Chalmette", "Geismar", "Kenner", "Lafayette", "Marrero", "PortAllen", "Vinton", "NewOrleans"]
        
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
        self.login_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

    #TODO make it login to database, currently it uses a "fake" login
        if username == "admin" and password == "password":
            messagebox.showinfo("Login Successful", "Welcome Admin!")
            self.destroy()  # Close the login window
            app = LouisianaMapApp(admin=True, cities=self.cities)   # give admin priviliges
            app.mainloop()
        elif username == "guest" and password == "guestpassword":
            messagebox.showinfo("Login Successful", "Welcome Guest!")
            self.destroy()  # Close the login window
            app = LouisianaMapApp(admin=False, cities=self.cities) # restrict admin privileges
            app.mainloop()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

class LouisianaMapApp(tk.Tk):   # our main window
    def __init__(self, admin=False, cities=None):
        super().__init__()
        self.cities = cities if cities else []
        self.marker_dict = {}
        
        self.title("Air Quality of Louisiana")
        self.geometry("1300x650")

        self.admin = admin

        self.create_widgets()

    def create_widgets(self):
        self.input_label = tk.Label(self, text="Selected City:")
        self.input_label.grid(column=0, row=1, sticky="NW")

        self.date_label = tk.Label(self, text="Date: ")
        self.date_label.grid(column=0, row=2, sticky="NW", pady=(100, 10))

        self.calendar = tkcalendar.Calendar(self, year=2024, month=3, day=22)
        self.calendar.grid(column=1, row=2, rowspan=2, sticky="NW", pady=(100, 10))

        self.year_label = tk.Label(self, text="Year: ")
        self.year_label.grid(column=2, row=1, sticky="E")

        years = list(range(2010, 2025))
        self.selected_year = tk.StringVar()  # Variable to store the selected year
        self.year_combobox = ttk.Combobox(self, textvariable=self.selected_year, state="readonly", values=years)
        self.year_combobox.grid(column=3, row=1, sticky="W")

        self.select_year_button = tk.Button(self, text="Search Lung Cancer Rates by Year", command=self.select_year)
        self.select_year_button.grid(column=4, row=1, sticky="W")

        self.add_submit_button = tk.Button(self, text="Search with Full Date and City", command=self.on_user_input)
        self.add_submit_button.grid(column=1, row=4, sticky="W")

        self.add_clear_button = tk.Button(self, text="Clear All", command=self.clear_input)
        self.add_clear_button.grid(column=3, row=4, sticky="W")

        self.city_label = tk.Label(self, text="Selected City:")
        self.city_label.grid(column=0, row=1, sticky="NW")

        self.selected_city = tk.StringVar()  # Variable to store the selected city
        self.city_combobox = ttk.Combobox(self, textvariable=self.selected_city, state="readonly")
        self.city_combobox.grid(column=1, row=1, sticky="NW")

        self.map_widget = tkintermapview.TkinterMapView(self, width=500, height=500, corner_radius=5)
        self.map_widget.grid(column=3, row=2, padx=(120,10), pady=(50, 10), rowspan=5, columnspan=5, sticky="SE")
        self.map_widget.set_position(30.9843, -91.9623)
        self.map_widget.set_zoom(7)

        if self.admin:  # if user = admin, add the add more data
            self.add_data_widget = tk.Button(self, text="Add Data", command=self.open_new_data_window)
            self.add_data_widget.grid(column=2, row=4, sticky="W")

        self.output_label = tk.Label(self, text="Output:")
        self.output_label.grid(column=2, row=5, sticky="SW")

        self.air_quality_labels = {}
        labels = ["PM 2.5", "Lung Cancer Cases", "Highest Lung Cancer Rate", "Lowest Lung Cancer Rate"]
        for i, label_text in enumerate(labels):
            label = tk.Label(self, text=f"{label_text}")
            label.grid(column=1, row=6+i*30, sticky="SE")
            entry = tk.Entry(self, width=20)
            entry.grid(column=2, row=6+i*30, sticky="SE")
            self.air_quality_labels[label_text] = entry

        try:
            # our 3 databases
            AirPollutionDB = {
                'server': 'localhost',
                'database': 'AirPollution2',
                'username': 'sa',
                'password': 'DB_Password',
                'driver': '{ODBC Driver 18 for SQL Server}'

            }
            LungCancerDB = {
                'server': 'localhost',
                'database': 'LungCancer',
                'username': 'sa',
                'password': 'DB_Password',
                'driver': '{ODBC Driver 18 for SQL Server}'

            }
            LocationDB = {
                'server': 'localhost',
                'database': 'Location',
                'username': 'sa',
                'password': 'DB_Password',
                'driver': '{ODBC Driver 18 for SQL Server}'
            }

            # connect to all 3 databases
            self.AirPollutionConnection = pyodbc.connect(
                f"DRIVER={AirPollutionDB['driver']};SERVER={AirPollutionDB['server']};DATABASE={AirPollutionDB['database']};"
                f"UID={AirPollutionDB['username']};PWD={AirPollutionDB['password']};TrustServerCertificate=yes"
            )

            self.LungCancerConnection = pyodbc.connect(
                f"DRIVER={LungCancerDB['driver']};SERVER={LungCancerDB['server']};DATABASE={LungCancerDB['database']};"
                f"UID={LungCancerDB['username']};PWD={LungCancerDB['password']};TrustServerCertificate=yes"
            )
            self.LocationConnection = pyodbc.connect(
                f"DRIVER={LocationDB['driver']};SERVER={LocationDB['server']};DATABASE={LocationDB['database']};"
                f"UID={LocationDB['username']};PWD={LocationDB['password']};TrustServerCertificate=yes"
            )
            
            self.loadCities() 
        except Exception as e:
            print("Error connecting to SQL Server:", e)

    def fetch_air_quality_data(self, city, lon, date):
        try:
            cursor = self.AirPollutionConnection.cursor()
            query = "SELECT PM25 FROM BatonRouge WHERE Date = ? AND City = ?"
            cursor.execute(query, (date, city))
            rows = cursor.fetchall()
            return rows[0] if rows else None
        except Exception as e:
            print("Error fetching air quality data:", e)
            return None

    def fetchLungCancerRates(self, city, lon, date):
        try:
            cursor = self.LungCancerConnection.cursor()
            query = "SELECT Count FROM LungCancerRates3 WHERE Year = ? AND Parish = ?"
            cursor.execute(query, (date, city))
            rows = cursor.fetchall()
            return rows[0] if rows else None
        except Exception as e:
                print("Error fetching Lung Cancer Rates", e)
                return None

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

    def loadCities(self):
        cities = ["Shreveport", "Alexandria", "Monroe", "BatonRouge", "Hammond", "Houma", "Chalmette", "Geismar", "Kenner", "Lafayette", "Marrero", "PortAllen", "Vinton", "NewOrleans"]  # Add more cities as needed
        self.city_combobox["values"] = cities
        self.selected_city.set(cities[0])  # Set the default selected city

    def on_user_input(self):
        city = self.selected_city.get()  # Get the selected city from the dropdown menu
        date_str = self.calendar.get_date()
        date_obj = datetime.strptime(date_str, '%m/%d/%y')
        formatted_date = date_obj.strftime('%Y-%m-%d')
        formatted_date2 = date_obj.strftime('%Y')
        coords = self.fetch_coordinates(city)

        air_quality_data = self.fetch_air_quality_data(city, formatted_date, formatted_date)
        print("Air quality data:", air_quality_data)

        if air_quality_data is not None:
            if air_quality_data:
                self.air_quality_labels["PM 2.5"].delete(0, tk.END)
                self.air_quality_labels["PM 2.5"].insert(0, air_quality_data[0])
                print("Setting PM 2.5 marker...")
            else:
                print("No air quality data found for the provided city.")
        else:
            print("No air quality data found for the provided city.")

        lung_cancer_data = self.fetchLungCancerRates(city, formatted_date2, formatted_date2)
        print("Lung cancer data:", lung_cancer_data)

        if lung_cancer_data is not None:
            if lung_cancer_data:
                self.air_quality_labels["Lung Cancer Cases"].delete(0, tk.END)
                self.air_quality_labels["Lung Cancer Cases"].insert(0, lung_cancer_data[0])
                print("Setting lung cancer marker...")
            else:
                print("No Cancer Rate Data found")
        else:
            print("No Cancer Rate Data found")

        self.update_marker(coords, city, formatted_date, air_quality_data, lung_cancer_data)

    def update_marker(self, coords, city, date, air_quality_data, lung_cancer_data):
        # Check if marker exists for the coordinates
        if coords in self.marker_dict:
            # If marker exists, check if the new city is the same as the city of the existing marker
            existing_marker_city = self.marker_dict[coords]["city"]
            if existing_marker_city == city:
                # If the cities match, update the text of the existing marker with new data
                marker_text = f"City: {city}, Date: {date}\nPM 2.5: {air_quality_data}\nLung Cancer Cases: {lung_cancer_data}"
                self.marker_dict[coords]["marker"].set_text(marker_text)
                return
            else:
                # If the cities don't match, remove the previous marker
                self.map_widget.remove_marker(self.marker_dict[coords]["marker"])
                del self.marker_dict[coords]

        # Create a new marker with updated information
        marker_text = f"City: {city}\nDate: {date}\nPM 2.5: {air_quality_data}\nLung Cancer Cases: {lung_cancer_data}"
        new_marker = self.map_widget.set_marker(coords[0], coords[1], text=marker_text, font=('Arial', 10))
        self.marker_dict[coords] = {"marker": new_marker, "city": city}

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
        
        return cities.get(city)  # Return coordinates for the specified city if found
        
    def sortSearch(self):
        try:
            cursor = self.LungCancerConnection.cursor()

            # Get the selected city and year from the dropdown menu and year entry
            selected_city = self.selected_city.get()
            selected_year = self.selected_year.get()

            # Validate if the year entry is not empty and is a valid integer
            if selected_year:
                try:
                    selected_year = int(selected_year)
                except ValueError:
                    messagebox.showerror("Error", "Please enter a valid year.")
                    return

            # Construct the SQL query based on whether the user entered a year or not
            if selected_year:
                query = "SELECT Count, Year FROM LungCancerRates3 WHERE Parish = ? AND Year = ?"
                cursor.execute(query, (selected_city, selected_year))
            else:
                query = "SELECT Count, Year FROM LungCancerRates3 WHERE Parish = ?"
                cursor.execute(query, (selected_city,))

            result = cursor.fetchone()

            if result:
                count, year = result
                messagebox.showinfo("Sort Search Result", f"The count of lung cancer cases in {selected_city} in {year} is {count}.")
            else:
                messagebox.showinfo("Sort Search Result", f"No lung cancer cases found for {selected_city} in {selected_year}.")

        except Exception as e:
            print("Error performing sort search:", e)


    def open_new_data_window(self):
        # Get the list of cities
        cities = ["Shreveport", "Alexandria", "Monroe", "BatonRouge", "Hammond", "Houma", "Chalmette", "Geismar", "Kenner", "Lafayette", "Marrero", "PortAllen", "Vinton", "NewOrleans"]
        
        # Call the method to create the window, passing the list of cities
        self.create_new_data_window(cities)

    def create_new_data_window(self, cities): 
        top = Toplevel()
        top.geometry("400x400")
        top.title("Add New Data")

        city_label = Label(top, text="City: ")
        city_label.grid(column=1, row=1)

        # Extract city names from the cities list
        city_names = cities
        self.selected_city = tk.StringVar()  # Variable to store the selected city
        self.city_combobox = ttk.Combobox(top, textvariable=self.selected_city, state="readonly", values=city_names)
        self.city_combobox.grid(column=2, row=1, sticky="NW")

        date_label = Label(top, text="Date: ")
        date_label.grid(column=1, row=2)

        self.date = tkcalendar.Calendar(top, year=2024, month=3, day=22, font=("Arial", 8))
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

    def select_year(self):
        selected_year = self.selected_year.get()
        if selected_year:
            self.show_highest_cancer_city(selected_year)
            self.show_lowest_cancer_city(selected_year)
        else:
            messagebox.showerror("Error", "Please select a year first.")

    def show_highest_cancer_city(self, year):
        try:
            cursor = self.LungCancerConnection.cursor()

            # Construct the SQL query to fetch the city with the highest count of lung cancer cases for the given year
            cities_list = ", ".join([f"'{city}'" for city in self.cities])  # Construct the list of cities
            query = f"""
            SELECT TOP 1 Parish, Count 
            FROM LungCancerRates3 
            WHERE Year = ? AND Parish IN ({cities_list}) 
            GROUP BY Parish, Count 
            ORDER BY Count DESC
            """
            cursor.execute(query, (year,))
            result = cursor.fetchone()

            if result:
                city, count = result
                self.air_quality_labels["Highest Lung Cancer Rate"].delete(0, tk.END)
                self.air_quality_labels["Highest Lung Cancer Rate"].insert(0, f"{year}: {city} ({count} cases)")
            else:
                self.air_quality_labels["Highest Lung Cancer Rate"].delete(0, tk.END)
                self.air_quality_labels["Highest Lung Cancer Rate"].insert(0, f"No data found for {year}.")
        except Exception as e:
            messagebox.showerror("Error",f"{e}")
    def show_lowest_cancer_city(self, year):
        try:
            cursor = self.LungCancerConnection.cursor()

            # Construct the SQL query to fetch the city with the lowest count of lung cancer cases for the given year
            cities_list = ", ".join([f"'{city}'" for city in self.cities])  # Construct the list of cities
            query = f"""
            SELECT TOP 1 Parish, Count 
            FROM LungCancerRates3 
            WHERE Year = ? AND Parish IN ({cities_list}) 
            GROUP BY Parish, Count 
            ORDER BY Count ASC
            """
            cursor.execute(query, (year,))
            result = cursor.fetchone()

            if result:
                city, count = result
                self.air_quality_labels["Lowest Lung Cancer Rate"].delete(0, tk.END)
                self.air_quality_labels["Lowest Lung Cancer Rate"].insert(0, f"{year}: {city} ({count} cases)")
            else:
                self.air_quality_labels["Lowest Lung Cancer Rate"].delete(0, tk.END)
                self.air_quality_labels["Lowest Lung Cancer Rate"].insert(0, f"No data found for {year}.")
        except Exception as e:
            print("Error fetching data:", e)
            messagebox.showerror("Error", f"An error occurred: {e}")





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

                # Extract the year from the date
                year = date_obj.year

                # Call the stored procedure
                AirPollutionCursor = self.AirPollutionConnection.cursor()
                AirPollutionCursor.execute("{CALL Insert_In_Air_Pollution_DB (?, ?, ?)}", (formatted_date, city, pm25))
                self.AirPollutionConnection.commit()

                # Insert lung cancer data
                LungCancerCursor = self.LungCancerConnection.cursor()
                LungCancerCursor.execute("{CALL Insert_In_Lung_Cancer_DB (?, ?, ?, ?, ?)}", (year, city, rate, lung_cancer_data, population))
                self.LungCancerConnection.commit()

                print("New Data added successfully")
            else:
                # Show error message if input is invalid
                messagebox.showerror("Input Error", "Invalid input. Please enter valid integer values for PM 2.5, Lung Cancer Cases, and Population, and a valid float value for Rate.")
        except Exception as e:
            # Show error message for any other exception
            messagebox.showerror("Error", f"Error adding new data: {e}")





if __name__ == "__main__":
    login_page = LoginPage()
    login_page.mainloop()

