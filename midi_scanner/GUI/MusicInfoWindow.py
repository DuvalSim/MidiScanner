import tkinter as tk
from PIL import Image, ImageTk

import logging


class MusicInfoWindow(tk.Frame):    

    
    def __init__(self, parent, suggested_bpms, percentage_quarter_rythms ) -> None:
        """Creates a window to input music information such as bpm.

        Keyword arguments:
        parent -- the parent of the window
        suggested_bpms -- the list of suggested bpms to display
        percentage_quarter_rythms -- percentage of quarter notes associated with that bpm
        """
        tk.Frame.__init__(self, parent)

        self.logger = logging.getLogger("MusicInfoWindow")
        self.parent = parent
                
        self.suggested_numbers = suggested_bpms
        self.percentage_quarter_rythms = percentage_quarter_rythms
        self.selected_number = None

        self.listbox_label = tk.Label(self, text="Suggested BPMs and associated quarter notes percentage")
        self.listbox_label.pack()

        self.number_listbox = self.number_listbox = tk.Listbox(self, selectmode=tk.SINGLE, highlightthickness=0, bg="white", fg="black")
        self.populate_listbox()
        self.number_listbox.pack(side="top", fill="both", expand=True)
        self.number_listbox.config(selectbackground=self.number_listbox.cget("background"),selectforeground=self.number_listbox.cget("foreground") )  # Set selectbackground to match background
        self.number_listbox.bind("<ButtonRelease-1>", self.on_select)
        # self.number_listbox.bind("<Double-1>", self.on_select)

        self.input_label = tk.Label(self, text="Enter your chosen number:")
        self.input_label.pack()

        self.input_entry = tk.Entry(self)
        self.input_entry.pack()

        self.confirm_button = tk.Button(self, text="Confirm", command=self.confirm_selection)
        self.confirm_button.pack()

    def populate_listbox(self):
        max_percentage_width = max(len(str(percentage)) for percentage in self.percentage_quarter_rythms)
        for number, percentage in zip(self.suggested_numbers, self.percentage_quarter_rythms):
            percentage_str = f"{percentage}%"
            percentage_str = percentage_str.rjust(max_percentage_width + 1)  # Adding 1 for space after percentage
            self.number_listbox.insert(tk.END, f"{number} - {percentage_str}")
        
    def on_select(self, event):
        selected_index = self.number_listbox.curselection()
        if selected_index:
            number = self.suggested_numbers[selected_index[0]]
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, str(number))

    def confirm_selection(self):
        selected_number = self.input_entry.get()
        if selected_number.isdigit():
            self.selected_number = int(selected_number)
            self.destroy()
            self.parent.focus_set()

    def pick_number(self):
        self.wait_window()
        return self.selected_number
