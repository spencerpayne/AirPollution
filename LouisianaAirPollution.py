import tkinter as tk    #imports tkinter as tk so we don't have to write out tkinter everytime
from tkinter import *   # imports all of tkinter's modules
import pyodbc   # allows us to connect python to the SQL Server
import tkcalendar   # calendar widget for tkinter
from datetime import datetime   #datetime module so we can convert dates to match the server
import tkintermapview   # this gives us an interactive map

# To run this program:
# Ensure you have the following:
# SQL Server, python, pyodbc, tkinter, tkcalendar, and tkintermapview

class LouisianaMapApp(tk.Tk):
    def __init__(self): # call the main window "self"
        super().__init__()  # initialize

        #   add a title and set the size of the window.
        self.title("Air Quality of Louisiana")  # sets the title 
        self.geometry("1300x650")   # sets the window size

        # ------- here, we add all of the widgets for tkinter, including labels, entrys, buttons, radiobuttons, a map, and a calendar. -------
        #   add a label for the selected coordinates box.
        self.input_label = tk.Label(self, text="Selected City:")
        self.input_label.grid(column=0, row=1, sticky="NW")  # place the label in column 0, row 1, and keep it in the NW quadrant of the grid

        #   add the entry box for the user to enter coordinates.
        self.input_entry = tk.Entry(self, width=35)
        self.input_entry.grid(column=1, row=1, sticky="NW") 
        #TODO add a dropdown where the user can select each city in the database

        # label that says "Date: "
        self.date_label = tk.Label(self, text="Date: ")
        self.date_label.grid(column=0, row=2, sticky="NW", pady=(100, 10))  # give it padding so the spacing looks nicer.

        self.calendar = tkcalendar.Calendar(self, year=2024, month=3, day=22)   # here we add the calendar and set it to March 22, 2024.
        self.calendar.grid(column=1, row=2, rowspan=2, sticky="NW", pady=(100, 10)) # span it across multiple rows 

        self.info_label = tk.Label(self, text="Or, search for a year and choose a sort method\n and the program will output which city had\n the highest or lowest number of cases for that year.")  # provide instruction to user
        self.info_label.grid(column=3, row=0, columnspan=3, sticky="W")

        self.info_label2 = tk.Label(self, text="Enter a city in Louisiana and select a date BELOW\n to see the PM 2.5 and Cancer Data") # more user instruction
        self.info_label2.grid(column=1, row=0, columnspan=2, sticky="W")

        self.year_label = tk.Label(self, text="Year: ") # label that says "Year: "
        self.year_label.grid(column=2, row=1, sticky="E")

        self.year_entry = tk.Entry(self, width=35)    # where the user can enter a specific year.
        self.year_entry.grid(column=3, row=1, sticky="W")

        self.sort_label = tk.Label(self, text="Sort: ") # label for the sort radio buttons
        self.sort_label.grid(column=2, row=2, sticky="SE")

        self.highest_first_sort = tk.Radiobutton(self, text="Highest First", value="highest")   # radio button that lets user choose to sort by highest first
        self.highest_first_sort.grid(column=3, row=2, sticky="SW")

        self.lowest_first_sort = tk.Radiobutton(self, text="Lowest first", value="lowest")  # radio button that lets user choose to sort by lowest first
        self.lowest_first_sort.grid(column=3, row=3, sticky="NW")

        self.add_submit_button = tk.Button(self, text="Search", command=self.on_user_input) # submit button, uses "on_user_input" function when clicked
        self.add_submit_button.grid(column=1, row=4, sticky="E")

        # ------- MAP -------
        self.map_widget = tkintermapview.TkinterMapView(self, width=400, height=400, corner_radius=5)   # add the map to the window and set the height and width and corner radius.
        self.map_widget.grid(column=3, row=2, padx=(120,10), pady=(50, 10), rowspan=5, columnspan=5, sticky="SE")
        self.map_widget.set_position(30.9843, -91.9623) # Louisiana coordinates
        self.map_widget.set_zoom(7)

        # ------- Add More Data Button -------
        self.add_data_widget = tk.Button(self, text="Add More Data", command=self.open_new_data_window) # button that allows user to enter more data to database
        self.add_data_widget.grid(column=2, row=4, sticky="W")
        #TODO: add way to add data to database
        
        # ------- Output Label -------
        self.output_label = tk.Label(self, text="Output:")
        self.output_label.grid(column=2, row=5, sticky="SW")
        #   right here we add our labels for our air pollution, we can adjust this accordingly

        # ------- Label and Entry for our data retrived from database -------
        self.air_quality_labels = {}
        labels = ["PM 2.5", "Lung Cancer Cases", "City with highest/lowest rate: "]
        for i, label_text in enumerate(labels): # this is how we space out the labels evenly, with a for loop. 
            label = tk.Label(self, text=f"{label_text}")
            label.grid(column=1, row=6+i*30, sticky="SE")  # right here we use the for loop the evenly space out the labels vertically
            entry = tk.Entry(self, width=20)
            entry.grid(column=2, row=6+i*30, sticky="SE") # same thing with the entry
            self.air_quality_labels[label_text] = entry

        # ------- Connect to database - user can modify the server and database if needed -------
        try:
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

            # Establish connections
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
            
            self.load_coordinates() 
        except Exception as e:
            print("Error connecting to SQL Server:", e) # print an exception if unsuccessful connection

    # ------- function that fetches air quality from database, uses user input of Date and City -------
    def fetch_air_quality_data(self, city, lon, date):
        try:
            cursor = self.AirPollutionConnection.cursor() # pyodbc uses a cursor to execute querys.
            query = " SELECT PM25 FROM BatonRouge WHERE Date = ? AND City = ?"  # this gets the PM 2.5 and Air Quality Rating value with the user input for Date and City.
            cursor.execute(query, (date, city))
            rows = cursor.fetchall()
            return rows[0] if rows else None
        except Exception as e:
            print("Error fetching air quality data:", e)
            return None

    def fetchLungCancerRates(self, city, lon, date):
        try:
            cursor = self.LungCancerConnection.cursor()
            query = "SELECT CountOfCases FROM LungCancerRates WHERE Year = ? AND Parish = ?"
            cursor.execute(query, (date, city))
            rows = cursor.fetchall()
            return rows[0] if rows else None
        except Exception as e:
                print("Error fetching Lung Cancer Rates", e)
                return None
    # ------- function that gets all of the cities from the database and prints them in the console. -------
    def load_coordinates(self):
        cursor = self.AirPollutionConnection.cursor() # connect to database
        cursor.execute("SELECT DISTINCT City FROM BatonRouge")   # execute query
        city = cursor.fetchall() # retrieves all cities
        print("Fetched cities:", city)  # list them in the console

    # ------- function that grabs the user input from the city and date entry -------
    def on_user_input(self):    
        city = self.input_entry.get()   # get city
        date_str = self.calendar.get_date() # get date
        date_obj = datetime.strptime(date_str, '%m/%d/%y')  # create the format for SQL Server
        formatted_date = date_obj.strftime('%Y-%m-%d')  # finally format the date
        formatted_date2 = date_obj.strftime('%Y')

        # ------- if user chooses a certain city, add a marker on the map. -------
        if city == "Shreveport":    # add a marker to the map if the user chooses Shreveport
            self.map_widget.set_position(32.5252, -93.7502, marker=True)  # Shreveport coorindates
            self.map_widget.set_zoom(7)
        elif city == "Baton Rouge":
            self.map_widget.set_position(30.4515, -91.1871, marker=True)
            self.map_widget.set_zoom(7)
        elif city == "Lafayette":
            self.map_widget.set_position(30.2241, -92.0198, marker=True)
            self.map_widget.set_zoom(7)
        elif city == "Bossier City":
            self.map_widget.set_position(32.5160, -93.7321, marker=True)
            self.map_widget.set_zoom(7)
        elif city == "New Orleans":
            self.map_widget.set_position(29.9511, -90.0715, marker=True)
            self.map_widget.set_zoom(7)

        # TODO: add more cities

        # ------- get city and the formatted date and insert -------
        air_quality_data = self.fetch_air_quality_data(city, formatted_date, formatted_date)
        if air_quality_data is not None:
            if air_quality_data:
                self.air_quality_labels["PM 2.5"].delete(0, tk.END)
                self.air_quality_labels["PM 2.5"].insert(0, air_quality_data[0])
            else:
                print("No air quality data found for the provided city.")
        else:
            print("No air quality data found for the provided city.")

        lung_cancer_data = self.fetchLungCancerRates(city, formatted_date2, formatted_date2)
        if lung_cancer_data is not None:
            if lung_cancer_data:
                self.air_quality_labels["Lung Cancer Cases"].delete(0, tk.END)
                self.air_quality_labels["Lung Cancer Cases"].insert(0, lung_cancer_data[0])  # Changed air_quality_data to lung_cancer_data
            else:
                print("No Cancer Rate Data found")
        else:
            print("No Cancer Rate Data found")

    def open_new_data_window(self): 
        top = Toplevel()    # top level is the second window that tkinter opens.
        top.geometry("400x300")
        top.title("Add New Data")

        city_label = Label(top, text="City: ")    # create label
        city_label.grid(column=1, row=1)  

        self.city_entry = Entry(top, width=25)   # Use self to make them accessible from other methods
        self.city_entry.grid(column=2, row=1)

        date_label = Label(top, text="Date: ")
        date_label.grid(column=1, row=2)

        self.date = tkcalendar.Calendar(top, year=2024, month=3, day=22, font=("Arial", 8))  # set default date and font
        self.date.grid(column=2, row=2)

        pm25_label = Label(top, text="PM 2.5: ")
        pm25_label.grid(column=1, row=3)

        self.pm_25_entry = Entry(top, width=25)
        self.pm_25_entry.grid(column=2, row=3)

        cancer_data_label = Label(top, text="Lung Cancer Cases: ")
        cancer_data_label.grid(column=1, row=4)

        self.cancer_data_entry = Entry(top, width=25)
        self.cancer_data_entry.grid(column=2, row=4)

        sumbit_button = Button(top, text="Submit", command=self.add_data)
        sumbit_button.grid(column=1, row=5)
        top.mainloop()  # mainloop() ensures that the program runs, without it the program won't open

    def add_data(self):
        try:   
            LungCancerCursor = self.LungCancerConnection.cursor()
            AirPollutionCursor = self.AirPollutionConnection.cursor() 

            city = self.city_entry.get()   # get city
            date_str = self.date.get_date() # get date
            date_obj = datetime.strptime(date_str, '%m/%d/%y')  # create the format for SQL Server
            formatted_date = date_obj.strftime('%Y-%m-%d')  # finally format the date
            pm25 = self.pm_25_entry.get()

            query = "INSERT INTO BatonRouge (City, Date, PM25) VALUES (?, ?, ?)"  # corrected the query syntax
            AirPollutionCursor.execute(query, (city, formatted_date, pm25))  # added comma to separate query and tuple
            self.AirPollutionConnection.commit()

            #TODO Add way to add Cancer #'s to db

            print("New Data added successfully")
        except Exception as e:
            print("Error adding new data:", e)


if __name__ == "__main__":
    app = LouisianaMapApp() # tkinter requires this statement 
    app.mainloop() # mainloop() ensures that the program runs, without it the program won't open
