# required packages: tkinter, PIL, pyodbc
# To use:
# Enter coordinates into the box or select from the coordinate bank. Enter it like this: 92.4324, -91.43423
# You can also click on the map to select coordinates. 
# Press enter while the selected coordinate box is highlighted to search.
import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk
import pyodbc

class LouisianaMapApp(tk.Tk):
    def __init__(self):
        super().__init__()

        #   add a title and set the size of the window.
        self.title("Air Quality of Louisiana")
        self.geometry("1400x600")

        #   open the image of Louisiana map and set it to 800x600 so it fits in the screen.
        self.map_image = Image.open("louisiana_map.jpg")
        self.map_image = self.map_image.resize((800, 600))
        self.map_photo = ImageTk.PhotoImage(self.map_image)

        #   here, we set the bounds of the map, the very top left corner of the map is 33.66452, -95.57564. We can adjust this if we need to.
        self.map_bounds = {
            "top_left": (33.66452, -95.57564),
            "bottom_right": (29.0, -89.0),
        }

        #   create a canvas to hold the map of Louisiana and set it to the same height and width as the image.
        self.canvas = tk.Canvas(self, width=800, height=600)
        self.canvas.pack(side=tk.LEFT)  # place it on the left side of the window.
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.map_photo)  #   add the image to the canvas
        self.canvas.bind("<Button-1>", self.on_map_click)   # create an event when the user clicks on the map

        #   add a label for the selected coordinates box.
        input_label = tk.Label(self, text="Selected Coordinates:")
        input_label.place(x=820, y=25)  # place the label

        #   add the entry box for the user to enter coordinates.
        self.input_entry = tk.Entry(self, width=35)
        self.input_entry.place(x=820, y=50)
        self.input_entry.bind("<Return>", self.on_user_input)   # pressing the enter key fetches the info

        #   right here we add our labels for our air pollution, we can adjust this accordingly
        self.air_quality_labels = {}
        labels = ["CO2", "PM2.5", "PM10", "Temperature", "Humidity"]
        for i, label_text in enumerate(labels): # this is how we space out the labels evenly, with a for loop. 
            label = tk.Label(self, text=f"{label_text}: ", anchor="w")
            label.place(x=820, y=350 + i * 30)  # right here we use the for loop the evenly space out the labels vertically
            entry = tk.Entry(self, width=20)
            entry.place(x=920, y=350 + i * 30)  # same thing with the entry
            self.air_quality_labels[label_text] = entry

        #   label that says "available coordinates"
        available_label = tk.Label(self, text="Available Coordinates:")
        available_label.place(x=1150, y=25)    # place it

        # we create a frame that holds the listbox/coordinate bank and the scrollbar.
        listbox_frame = tk.Frame(self)
        listbox_frame.place(x=1100, y=50)

        # here is the coordinate bank. It lists all the current coordinates (lat, long) in the SQL query.
        self.coordinates_listbox = tk.Listbox(listbox_frame, width=40, height=15)
        self.coordinates_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.coordinates_listbox.bind("<<ListboxSelect>>", self.on_coordinate_selected)

        # create the scrollbar for the coordinate bank.
        scrollbar = tk.Scrollbar(
            listbox_frame, orient=tk.VERTICAL, command=self.coordinates_listbox.yview
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.coordinates_listbox.config(yscrollcommand=scrollbar.set)   # here, we attatch the scrollbar to the coordinate bank.



        # try to connect to SQL server. 
        try:
            self.conn = pyodbc.connect(
                #'Driver={ODBC Driver 18 for SQL Server};Server=tcp:<database-server-name>.database.windows.net,1433;Database=<database-name>;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30' for azure I think
                "DRIVER={SQL Server};SERVER=localhost;DATABASE=AirPollution;Trusted_Connection=yes;"    # I have it set to connect to my localhost using Windows Authentication. Database is named "AirPollution"
            )

            #
            #
            #   I think we should add the sql queries here?
            #
            #
            

            print("Connected to SQL Server successfully")
            self.load_coordinates()
        except Exception as e:
            print("Error connecting to SQL Server:", e)

        # our button that adds data to the database.
        self.add_data_button = tk.Button(
            self, text="Add New Data", command=self.add_new_data
        )
        self.add_data_button.place(x=820, y=500)

    #   this is where we grab the SQL data. We can change this if needed
    def fetch_air_quality_data(self, lat, lon): # grabs the lat and lon
        try:
            cursor = self.conn.cursor() # need a cursor to connect 
            query = "SELECT CO2, PM25, PM10, Temperature, Humidity FROM AirQualityData WHERE Latitude = ? AND Longitude = ?"    # query to select air pollution data
            cursor.execute(query, (lat, lon))   # execute query.
            rows = cursor.fetchall()    # grabs the rows that were just queried
            return rows[0] if rows else None
        except Exception as e:
            print("Error fetching air quality data:", e)
            return None

    # this is how we add the coordinates to the listbox/coordinate bank. It also prints the loaded coordinates into the console.
    def load_coordinates(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT DISTINCT Latitude, Longitude FROM AirQualityData")
            coordinates = cursor.fetchall()
            print("Fetched coordinates:", coordinates)
            for lat, lon in coordinates:
                self.coordinates_listbox.insert(tk.END, f"{lat}, {lon}")
        except Exception as e:
            print("Error loading coordinates:", e)

    # this determines the map bounds/coordinates and then when a user clicks on the map, the coordinates are added to the search coordinate box.
    def on_map_click(self, event):
        x, y = event.x, event.y
        map_width, map_height = self.map_image.size
        lat_range = (
            self.map_bounds["top_left"][0] - self.map_bounds["bottom_right"][0]
        )
        lon_range = (
            self.map_bounds["bottom_right"][1] - self.map_bounds["top_left"][1]
        )
        lat = self.map_bounds["top_left"][0] - (lat_range * y / map_height) # calculate latitude on map clicked
        lon = self.map_bounds["top_left"][1] + (lon_range * x / map_width)  # calculate longitude on map clicked
        
        self.input_entry.delete(0, tk.END)  # delete entry if another coordinate is selected
        self.input_entry.insert(0, f"{lat}, {lon}")

        self.canvas.delete("marker")
        
        air_quality_data = self.fetch_air_quality_data(lat, lon)
        if air_quality_data:
            for label_text, entry in self.air_quality_labels.items():   # add the SQL data into the CO2, PM2.5, PM10, Temperature, and Humidity boxes.
                entry.delete(0, tk.END)
                entry.insert(0, air_quality_data[label_text])
        else:
            print("No air quality data found for the provided coordinates.")

        marker_size = 10
        self.canvas.create_oval(
            x - marker_size,
            y - marker_size,
            x + marker_size,
            y + marker_size,
            fill="red",
            tag="marker",
        )
    # this checks the user input when the
    def on_user_input(self, event):
        input_text = self.input_entry.get() # grab user input
        if input_text:
            try:
                lat, lon = map(float, input_text.split(","))    # splits the user input, the coordinates, by a , For example, 93, 95 will be read as 93 and 95 seperately.
            except ValueError:
                print("Invalid coordinates format. Please use latitude,longitude.")
                return
            air_quality_data = self.fetch_air_quality_data(lat, lon)
            if air_quality_data is not None:
                if air_quality_data:
                    for label_text, value in zip(
                        self.air_quality_labels.keys(), air_quality_data    # add SQL data into the boxes
                    ):
                        self.air_quality_labels[label_text].delete(0, tk.END)
                        self.air_quality_labels[label_text].insert(0, value)
                else:
                    print("No air quality data found for the provided coordinates.")
            else:
                print("Failed to fetch air quality data.")

    # when a coordinate is selected from the coordinate bank.
    def on_coordinate_selected(self, event):
        selected_index = self.coordinates_listbox.curselection()
        if selected_index:
            selected_item = self.coordinates_listbox.get(selected_index[0])
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, selected_item)

            self.canvas.delete("marker")

            lat, lon = map(float, selected_item.split(", "))

            map_width, map_height = self.map_image.size
            lat_range = (
                self.map_bounds["top_left"][0] - self.map_bounds["bottom_right"][0]
            )
            lon_range = (
                self.map_bounds["bottom_right"][1] - self.map_bounds["top_left"][1]
            )
            x = (lon - self.map_bounds["top_left"][1]) / lon_range * map_width
            y = (self.map_bounds["top_left"][0] - lat) / lat_range * map_height

            # this is what creates the red marker on the map.
            marker_size = 10
            self.canvas.create_oval(
                x - marker_size,
                y - marker_size,
                x + marker_size,
                y + marker_size,
                fill="red",
                tag="marker",
            )
    # this allows us to add new data into the SQL Server.
    def add_new_data(self):
        try:
            lat, lon = map(float, self.input_entry.get().split(","))    # splits the lat and long values by a ,
            air_quality_data = [float(entry.get()) for entry in self.air_quality_labels.values()]   # grab air quality data
            cursor = self.conn.cursor()
            query = "INSERT INTO AirQualityData (Latitude, Longitude, CO2, PM25, PM10, Temperature, Humidity) VALUES (?, ?, ?, ?, ?, ?, ?)"
            cursor.execute(query, (lat, lon, *air_quality_data))
            self.conn.commit()
            print("New data added successfully")
            self.coordinates_listbox.delete(0, tk.END)
            self.load_coordinates()
        except Exception as e:
            print("Error adding new data:", e)


if __name__ == "__main__":
    app = LouisianaMapApp()
    app.mainloop()
