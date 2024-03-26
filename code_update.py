import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk
#import pyodbc
import tkcalendar
from datetime import datetime
import tkintermapview

class LouisianaMapApp(tk.Tk):
    def __init__(self):
        super().__init__()

        #   add a title and set the size of the window.
        self.title("Air Quality of Louisiana")
        self.geometry("1400x700")

        #   add a label for the selected coordinates box.
        self.input_label = tk.Label(self, text="Selected City:")
        self.input_label.grid(column=0, row=1, sticky="NW")  # place the label

        #   add the entry box for the user to enter coordinates.
        self.input_entry = tk.Entry(self, width=35)
        self.input_entry.grid(column=1, row=1, sticky="NW")

        self.date_label = tk.Label(self, text="Date: ")
        self.date_label.grid(column=0, row=2, sticky="NW", pady=(100, 10))

        calendar = tkcalendar.Calendar(self, year=2024, month=3, day=22)
        calendar.grid(column=1, row=2, rowspan=2, sticky="NW", pady=(100, 10))

        self.info_label = tk.Label(self, text="Or, search for a year and the program will output which city had\n the highest number of cases for that year.")
        self.info_label.grid(column=3, row=0, columnspan=3, sticky="W")

        self.info_label2 = tk.Label(self, text="Enter a city in Louisiana and select a date BELOW\n to see the PM 2.5 and Cancer Data")
        self.info_label2.grid(column=1, row=0, columnspan=2, sticky="W")
        self.year_label = tk.Label(self, text="Year: ")
        self.year_label.grid(column=2, row=1, sticky="E")

        self.year_entry = tk.Entry(self)
        self.year_entry.grid(column=3, row=1, sticky="W")

        self.add_submit_button = tk.Button(self, text="Search", command=self.on_user_input)
        self.add_submit_button.grid(column=1, row=4, sticky="E")

        map_widget = tkintermapview.TkinterMapView(self, width=500, height=500, corner_radius=0)
        map_widget.grid(column=3, row=2, padx=(100, 10), rowspan=5, columnspan=5, sticky="SE")
        map_widget.set_position(30.9843, -91.9623) # Louisiana coordinates
        map_widget.set_zoom(7)

        self.add_data_widget = tk.Button(self, text="Add More Data", command=self.open_new_data_window)
        self.add_data_widget.grid(column=2, row=4, sticky="W")
            
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
            self.conn = pyodbc.connect(
                #'Driver={ODBC Driver 18 for SQL Server};Server=tcp:<database-server-name>.database.windows.net,1433;Database=<database-name>;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30' for azure I think
                "DRIVER={SQL Server};SERVER=localhost;DATABASE=AirPollution;Trusted_Connection=yes;"    # I have it set to connect to my localhost using Windows Authentication. Database is named "AirPollution"
            )
            print("Connected to SQL Server successfully")
            self.load_coordinates() 
        except Exception as e:
            print("Error connecting to SQL Server:", e)

    #   this is where we grab the SQL data. We can change this if needed
    def fetch_air_quality_data(self, lat, lon, date):
        try:
            cursor = self.conn.cursor()
            query = "SELECT PM25, AirQualityRating FROM PollutionData WHERE Date = ? AND Parish = ?"
            cursor.execute(query, (date, lat))
            rows = cursor.fetchall()
            return rows[0] if rows else None
        except Exception as e:
            print("Error fetching air quality data:", e)
            return None

    # this is how we add the coordinates to the listbox/coordinate bank. It also prints the loaded coordinates into the console.
    def load_coordinates(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT City FROM PollutionData")
        parish = cursor.fetchall() # retrieve all coordinates
        print("Fetched cities:", city)  # list them in the console

    def on_user_input(self):
        parish = self.input_entry.get()
        date_str = self.calendar.get_date()
        date_obj = datetime.strptime(date_str, '%m/%d/%y')
        formatted_date = date_obj.strftime('%Y-%m-%d')

        if parish == "Shreveport":
            self.map_widget.set_position(32.6137, -93.8655, marker=True)  # Paris, France
            self.map_widget.set_zoom(7)
        # TODO: add more cities

        air_quality_data = self.fetch_air_quality_data(city, formatted_date, formatted_date)
        if air_quality_data is not None:
            if air_quality_data:
                self.air_quality_labels["PM 2.5"].delete(0, tk.END)
                self.air_quality_labels["PM 2.5"].insert(0, air_quality_data[0])
                self.air_quality_labels["Cancer Data"].delete(0, tk.END)
                self.air_quality_labels["Cancer Data"].insert(0, air_quality_data[1])
                
            else:
                print("No air quality data found for the provided coordinates.")
        else:
            print("No air quality data found for the provided coordinates.")

    def open_new_data_window(self, event=None):
        top = Toplevel()
        top.geometry("400x300")
        top.title("Add New Data")
        city = Label(top, text="City: ")
        city.grid(column=1, row=1)

        city_entry = Entry(top, width=25)
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
        top.mainloop()


if __name__ == "__main__":
    app = LouisianaMapApp()
    app.mainloop()
