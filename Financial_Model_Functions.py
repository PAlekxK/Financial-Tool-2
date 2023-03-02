import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.cbook as cbook
import numpy as np
import datetime
import tkinter as tk
from tkinter import simpledialog

import pandas as pd
import os
import yaml

def load_config(config_path='Financial_Tool.yml'):
    """Loads the config_path.yml into a dictionary"""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config

def load_starting_csv(field_list):
    # Need to be able to provide file path as input to load in existing file
    print("Which file would you like to use as a starting point? Please provide the file path")

    # Function should suggest a file path to help make interface easier - expected location
    starting_file_path = input("I suggest a file path in the format: \n" + r"C:\Users\kirschenbauer paul\Learning Material\Financial Tool\Financial Tool Repository\2023-01-02_financial_data.csv")

    #Function should then load in file as dataset. Function should establish dataset as the df and ensure it is not overwritten in the add_row function
    financial_data = pd.read_csv(starting_file_path, usecols = field_list)
    #check 
    
    #add if error here "Ensure file path is correct and the file is a csv file"

    #Ensure date is in date time
    financial_data['Date'] = pd.to_datetime(financial_data['Date']).dt.date
    #added .dt.date here
    
    #Remove empty spaces for column in financial_data.index():
    
    # Function should establish column names as the fields
    field_list = financial_data.columns

    # Function should display most and least recent dates and number of entries in dataset
    print("")
    print("The dataframe has "+str(len(financial_data))+" rows/entries")
    print("The dataframe's most recent entry is from: "+ str(financial_data['Date'].min()))
    print("The dataframe's least recent entry is from: "+ str(financial_data['Date'].max()))
    print("")
    return(financial_data, starting_file_path)


## old add row function (prompts field by field)
def add_row(financial_data, field_list, num_fields):
    #create empty list
    input_list = [None] * (num_fields)
    
    #initialize field counter to iterate through list
    field_counter = 0 
    
    #begin iterating through list
    for word in field_list:
       # check if we are in the first "Date" column
        if word == field_list[0]:

            #Get row date
            print("What is the date you would like to add data for?")
            row_month = int(input("Input MM"))
            row_day = int(input("Input DD"))
            row_year = int(input("Input YY"))
            row_date = datetime.datetime(row_year,row_month,row_day)

            #add row date to input_list    
            input_list[field_counter] = row_date

            #move to next field in input list
            field_counter= field_counter + 1
        else:
            print("Do you have a value to add for " + word +"?")
            print("If so, please enter the value in the field below. Otherwise, just hit Enter")
            value = input()
            if value == "":
                input_list[field_counter] = 0
                print("Ok fine")
                print("")
            else:
                input_list[field_counter] = value
            
            #move to next field in input list
            field_counter = field_counter + 1
    print(input_list)
    financial_data.reset_index()
    financial_data.loc[len(financial_data)] = input_list
    #financial_data.rename(index={len(financial_data):row_date},inplace = True)
    return financial_data

##### New add row function (prompts for all fields at once)
#Start by prompting for values
def account_balance_prompt(fields):
    ### Establish field names for pop-up
    column_names = fields
    column_names.remove('Date')
    # pop_up_defaults = [0] * len(column_names)
    # pop_up_fields = list(zip(column_names, pop_up_defaults))
    
    class UserInfoDialog(simpledialog.Dialog):
        def __init__(self, parent, title, fields):
            self.fields = fields
            simpledialog.Dialog.__init__(self, parent, title)

        def body(self, master):
            self.entries = []
            for i, field in enumerate(self.fields):
                tk.Label(master, text=field+":").grid(row=i)
                entry = tk.Entry(master)
                entry.grid(row=i, column=1)
                self.entries.append(entry)
            return self.entries[0]  # initial focus

        def apply(self):
            self.results = {}
            for entry, field in zip(self.entries, self.fields):
                self.results[field] = entry.get()

    root = tk.Tk()
    root.withdraw()


    dialog = UserInfoDialog(root, "User Information", column_names)

    if dialog.results is not None:
        print("Results:")
        for column_name in column_names:
            print("{}: {}".format(column_name, dialog.results[column_name]))
    else:
        print("You cancelled the input")

    root.destroy()
    
    return dialog.results

##### Calculate Net Worth 
def calculate_net_worth(financial_data, Assets, Liabilities):
    #Calculate Total Assets
    financial_data['Calculated Total Assets'] = financial_data[Assets].astype(float).sum(axis=1)

    #Calculate Total Liabilities
    financial_data['Calculated Total Liabilities'] = financial_data[Liabilities].astype(float).sum(axis=1)

    #Calculate Net Worth
    financial_data['Calculated_Net_Worth']=financial_data['Calculated Total Assets'] -financial_data['Calculated Total Liabilities']

    return financial_data
    
    
##### Get Stock Prices from Yahoo   
def fetch_yf_data(financial_data, symbols, start, end):
    data = yf.download(symbols, start, end)
    stockdata = data['Close']

    # financial_data = financial_data.merge(stockdata, how="left", left_on = 'Date', right_on = 'Date')
    financial_data_w_yf = financial_data.merge(stockdata, how="left", left_index = True, right_index = True)
    return financial_data_w_yf

##### Summary Table Display
def create_summary_table(financial_data, start_date, end_date):
    Change_df = financial_data.loc[[start_date,end_date]]
    Summary_table = Change_df.T
    Summary_table.iloc[0] = Summary_table.iloc[0].astype(float)
    Summary_table.iloc[1] = Summary_table.iloc[1].astype(float)
    
    Summary_table['Change - $'] = Summary_table[start_date].astype(float) - Summary_table[end_date].astype(float)
    
    Change_Percentage = 100*Summary_table['Change - $'].astype(float) / Summary_table[start_date].astype(float)
    
#     Summary_table = Summary_table[[start_date,end_date,'Change - $']].style.format("${:,.0f}")
    
    return Summary_table

##### Select date
def select_end_date(financial_data):
    def show_selected_date():
        # get the selected date
        selected_date = var.get()
        print("Selected date:", selected_date)
        # convert the selected date to a datetime object
        selected_datetime = datetime.datetime.strptime(selected_date, '%Y-%m-%d')
        # update the variable storing the selected date
        selected_datetime_variable.set(selected_datetime)

    # create a sample list of dates
    dates = financial_data.index

    # create the main window
    root = tk.Tk()
    root.title("Select date")

    # create the drop-down menu
    var = tk.StringVar(value=dates[0])
    option = tk.OptionMenu(root, var, *dates)
    option.pack()

    # create a variable to store the selected datetime
    selected_datetime_variable = tk.StringVar()

    # create a button to show the selected date
    show_button = tk.Button(root, text="Show selected date", command=show_selected_date)
    show_button.pack()

    # start the main loop
    root.mainloop()
    
    return selected_datetime_variable.get()

##### Time Series Chart
def plot_time_series(financial_data, y_dimension, y_dimension_name, plot_title):
    financial_data.sort_index(ascending = False, inplace = True)
    x_axis = financial_data.index
    y_axis = financial_data[y_dimension]

    graph = plt.plot(x_axis, y_axis,':g1')
    plt.title(plot_title)
    plt.xlabel('Date')
    plt.ylabel(y_dimension_name)

    plt.grid(True, axis = 'y')
    plt.grid(True, axis = 'x',which = 'major')


    current_values = plt.gca().get_yticks()/1000
    plt.gca().set_yticklabels(['${:,.0f}k'.format(x) for x in current_values])

    plt.show()


##### Stacked area chart
def plot_stacked_area(financial_data, account_hierarchy, Lia_or_Ass):
    graph_data = pd.DataFrame(columns = account_hierarchy['field_list'][Lia_or_Ass])
    
    i=0
    for account in account_hierarchy['field_list'][Lia_or_Ass]:
        graph_data[account] = financial_data[account_hierarchy['field_list'][Lia_or_Ass][account]].T.sum()
        i = i +1

    graph_data
    graph_data.plot.area()
    
    current_values = plt.gca().get_yticks()
    
    plt.gca().set_yticklabels(['${:,.0f}'.format(x) for x in current_values])

    plt.xlabel('Date', fontweight='bold', color = 'green', fontsize='10', horizontalalignment='center')
    plt.ylabel(Lia_or_Ass + ' Value', fontweight='bold', color = 'green', fontsize='10', horizontalalignment='center')
    plt.title(Lia_or_Ass + ' Composition over Time', fontweight='bold', color = 'green', fontsize='10', horizontalalignment='center')