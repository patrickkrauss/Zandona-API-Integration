# Zandona-API-Integration

This program was created with the goal of completely automating the process of importing and organizing vehicle refueling data, which is crucial to calculate average consumption of vehicles and manage expense costs.

The project was developed using Pandas for data manipulation and the Requests library for connection with the API provided by the Zandoná gas station network.

The program execution steps are:

1. The user selects the desired year and month to import data
2. The script connects to the API using the Api token and send the requests to download the necessary data
3. The script organizes and adjust the returned data removing unused information
4. The imported data is saved to a new Excel file on the same directory of the script

The output file with all the vehicle refueling data of the month can be imported into the desired system.


Program Running in terminal:

https://user-images.githubusercontent.com/8397051/201432663-8c1ea6d2-5e1e-4764-8aa5-8f24bd5d0550.mp4


Example of Output file:

![Result](Images/output.png)
