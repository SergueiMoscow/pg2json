import tkinter as tk
from tkinter import ttk


databases = ['db1', 'db2', 'db3']


def getBackups(database):
    return ['date1', 'date2', 'date3']


def restore(database, date):
    print(f"Restoring from {database} at date {date}")


def get_dates(evt):
    # Note here that Tkinter passes an event object to onselect()
    database = combo1.get()
    dates = getBackups(database)
    combo2['values'] = dates


def ok_function():
    database = combo1.get()
    date = combo2.get()
    restore(database, date)


if __name__ == '__main__':
    root = tk.Tk()

    combo1 = ttk.Combobox(root, values=databases)
    combo1.bind('<<ComboboxSelected>>', get_dates)
    combo1.grid(row=0, column=0)

    combo2 = ttk.Combobox(root)
    combo2.grid(row=0, column=1)

    okButton = ttk.Button(root, text="Ok", command=ok_function)
    okButton.grid(row=1, column=0)

    cancelButton = ttk.Button(root, text="Отмена", command=root.quit)
    cancelButton.grid(row=1, column=1)

    root.mainloop()
