import tkinter as tk    #imports tkinter as tk so we don't have to write out tkinter everytime
from tkinter import *   # imports all of tkinter's modules
import pyodbc   # allows us to connect python to the SQL Server
import tkcalendar   # calendar widget for tkinter
from datetime import datetime   #datetime module so we can convert dates to match the server
import tkintermapview   # this gives us an interactive map

class LouisianaMapApp(tk.Tk):
    def __init__(self): # call the main window "self"
        super().__init__()  # initialize

        #   add a title and set the size of the window.
        self.title("Air Quality of Louisiana")  # sets the title 
        self.geometry("1200x700")   # sets the window size

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

        self.info_label = tk.Label(self, text="Or, search for a year and the program will output which city had\n the highest number of cases for that year.")  # provide instruction to user
        self.info_label.grid(column=3, row=0, columnspan=3, sticky="W")

        self.info_label2 = tk.Label(self, text="Enter a city in Louisiana and select a date BELOW\n to see the PM 2.5 and Cancer Data") # more user instruction
        self.info_label2.grid(column=1, row=0, columnspan=2, sticky="W")

        self.year_label = tk.Label(self, text="Year: ") # label that says "Year: "
        self.year_label.grid(column=2, row=1, sticky="E")

        self.year_entry = tk.Entry(self)    # where the user can enter a specific year.
        self.year_entry.grid(column=3, row=1, sticky="W")

        self.add_submit_button = tk.Button(self, text="Search", command=self.on_user_input) # submit button, uses "on_user_input" function when clicked
        self.add_submit_button.grid(column=1, row=4, sticky="E")

        self.map_widget = tkintermapview.TkinterMapView(self, width=500, height=500, corner_radius=0)   # add the map to the window and set the height and width and corner radius.
        self.map_widget.grid(column=4, row=2, padx=(100, 10), rowspan=5, columnspan=5, sticky="SE")
        self.map_widget.set_position(30.9843, -91.9623) # Louisiana coordinates
        self.map_widget.set_zoom(7)

        self.add_data_widget = tk.Button(self, text="Add More Data", command=self.open_new_data_window) # button that allows user to enter more data to database
        self.add_data_widget.grid(column=2, row=4, sticky="W")
        #TODO: add way to add data to database
            
        self.output_label = tk.Label(self, text="Output:")
        self.output_label.grid(column=2, row=5, sticky="W")
        #   right here we add our labels for our air pollution, we can adjust this accordingly

        self.air_quality_labels = {}
        labels = ["PM 2.5", "Cancer Data", "City with highest rate: "]
        for i, label_text in enumerate(labels): # this is how we space out the labels evenly, with a for loop. 
            label = tk.Label(self, text=f"{label_text}")
            label.grid(column=1, row=6+i*30, sticky="E")  # right here we use the for loop the evenly space out the labels vertically
            entry = tk.Entry(self, width=20)
            entry.grid(column=2, row=6+i*30, sticky="E") # same thing with the entry
            self.air_quality_labels[label_text] = entry

        # try to connect to SQL server. - this is important. change the database name if its not called AirPollution.
        try:
            self.conn = pyodbc.connect( # connect to SQL Server with pyodbc. 
                "DRIVER={SQL Server};SERVER=localhost;DATABASE=AirPollution;Trusted_Connection=yes;"   
            )
            print("Connected to SQL Server successfully")   # print this if successful connection
            self.load_coordinates() 
        except Exception as e:
            print("Error connecting to SQL Server:", e) # print an exception if unsuccessful connection

    #   this is where we grab the SQL data. We can change this if needed
    def fetch_air_quality_data(self, city, lon, date):
        try:
            cursor = self.conn.cursor() # pyodbc uses a cursor to execute querys.
            query = "SELECT PM25, AirQualityRating FROM PollutionData WHERE Date = ? AND City = ?"  # this gets the PM 2.5 and Air Quality Rating value with the user input for Date and City.
            cursor.execute(query, (date, city))
            rows = cursor.fetchall()
            return rows[0] if rows else None
        except Exception as e:
            print("Error fetching air quality data:", e)
            return None

    # this is how we add the coordinates to the listbox/coordinate bank. It also prints the loaded coordinates into the console.
    def load_coordinates(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT City FROM PollutionData")   # gets each individual city from the database
        city = cursor.fetchall() # retrieve all coordinates
        print("Fetched cities:", city)  # list them in the console

    def on_user_input(self):    # function that gets the user input for city abd date and then formats the date for SQL Server.
        city = self.input_entry.get()   # get city
        date_str = self.calendar.get_date() # get date
        date_obj = datetime.strptime(date_str, '%m/%d/%y')  # create the format
        formatted_date = date_obj.strftime('%Y-%m-%d')  # finally format the date

        if city == "Shreveport":    # add a marker to the map if the user chooses Shreveport
            self.map_widget.set_position(32.6137, -93.8655, marker=True)  # Shreveport coorindates
            self.map_widget.set_zoom(7)
        # TODO: add more cities

        air_quality_data = self.fetch_air_quality_data(city, formatted_date, formatted_date)    # get city and formatted date
        if air_quality_data is not None:
            if air_quality_data:
                self.air_quality_labels["PM 2.5"].delete(0, tk.END) # delete anyting in the field
                self.air_quality_labels["PM 2.5"].insert(0, air_quality_data[0])    # add the PM 2.5 data to the field
                self.air_quality_labels["Cancer Data"].delete(0, tk.END)    # delete anything in the field
                self.air_quality_labels["Cancer Data"].insert(0, air_quality_data[1])   # add the Cancer Data to the field
                
            else:
                print("No air quality data found for the provided city.")   # error handling
        else:
            print("No air quality data found for the provided city.")   # more error handling

    def open_new_data_window(self, event=None): # when user clicks the "Add More Data" button, open new window.
        top = Toplevel()    # top level is the second window that tkinter opens.
        top.geometry("400x300")
        top.title("Add New Data")
        city = Label(top, text="City: ")    # create label
        city.grid(column=1, row=1)  

        city_entry = Entry(top, width=25)   # create entry
        city_entry.grid(column=2, row=1)

        date_label = Label(top, text="Date: ")
        date_label.grid(column=1, row=2)

        date = tkcalendar.Calendar(top, year=2024, month=3, day=22, font=("Arial", 8))
        date.grid(column=2, row=2)

        pm25_label = Label(top, text="PM 2.5: ")
        pm25_label.grid(column=1, row=3)

        pm_25_entry = Entry(top, width=25)
        pm_25_entry.grid(column=2, row=3)

        cancer_data_label = Label(top, text="Cancer Data: ")
        cancer_data_label.grid(column=1, row=4)

        cancer_data_entry = Entry(top, width=25)
        cancer_data_entry.grid(column=2, row=4)

        sumbit_button = Button(top, text="Submit")
        sumbit_button.grid(column=1, row=5)
        top.mainloop()  # mainloop() ensures that the program runs, without it the program won't open


if __name__ == "__main__":
    app = LouisianaMapApp() # tkinter requires this statement 
    app.mainloop() # mainloop() ensures that the program runs, without it the program won't open
