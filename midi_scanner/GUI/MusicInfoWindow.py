import tkinter as tk
from tkinter import ttk

from typing import Tuple

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

        TIMESIGNATURE_NUMERATOR_OPTIONS = [i for i in range(1, 17)]
        TIMESIGNATURE_DENOMINATOR_OPTIONS = [1, 2, 4, 8]
                
        self.suggested_numbers = suggested_bpms
        self.percentage_quarter_rythms = percentage_quarter_rythms
        self.selected_number = None

        self.listbox_label = tk.Label(self, text="Suggested BPMs and associated quarter notes percentage")
        self.listbox_label.grid(column=0, row=0)

        self.number_listbox = self.number_listbox = tk.Listbox(self, selectmode=tk.SINGLE, highlightthickness=0, bg="white", fg="black")
        self.populate_listbox()
        self.number_listbox.grid(column=0, row=1) #side="top", fill="both",
        self.number_listbox.config(selectbackground=self.number_listbox.cget("background"),selectforeground=self.number_listbox.cget("foreground") )  # Set selectbackground to match background
        self.number_listbox.bind("<ButtonRelease-1>", self.on_select)
        # self.number_listbox.bind("<Double-1>", self.on_select)

        self.input_label = tk.Label(self, text="Enter your chosen number:")
        self.input_label.grid(column=0, row=2)

        self.input_entry = tk.Entry(self)
        self.input_entry.grid(column=0, row=3)

        self.confirm_button = tk.Button(self, text="Confirm", command=self.confirm_selection)
        self.confirm_button.grid(column=0, row=4, columnspan=5)


        # self.time_signature_checkbox_label = tk.Label(self, text="Enter custom time signature (not bug proof): ")
        # self.time_signature_checkbox_label.grid(column=1, row=1, columnspan=4)

        self.time_signature_checkbox_var = tk.IntVar()
        self.time_signature_checkbox_var.set(0)
        time_signature_checkbox = tk.Checkbutton(self, variable=self.time_signature_checkbox_var, text= "Enter custom time signature (still buggy sometimes): ", command=self.update_timeSignature_state)
        time_signature_checkbox.grid(column=1, columnspan=4, row=1)
        
        self.time_signature_numerator_combo = ttk.Combobox(self, values=TIMESIGNATURE_NUMERATOR_OPTIONS, width=3)
        self.time_signature_numerator_combo.grid(row=2, column=1)
        self.time_signature_numerator_combo.current(3) # 4

        # Create the "/" label in the middle
        slash_label = tk.Label(self, text="/")
        slash_label.grid(row=2, column=2)

        # Create the denominator dropdown (bottom number of time signature)
        self.time_signature_denominator_combo = ttk.Combobox(self, values=TIMESIGNATURE_DENOMINATOR_OPTIONS, width=3)
        self.time_signature_denominator_combo.grid(row=2, column=3)
        self.time_signature_denominator_combo.current(2)

        self.update_timeSignature_state()
        




    def update_timeSignature_state(self):
        active = (self.time_signature_checkbox_var.get() == 1)
        new_state = "readonly" if active else "disabled"
        self.time_signature_denominator_combo.configure(state=new_state)
        self.time_signature_numerator_combo.configure(state=new_state)

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

    def get_current_time_signature(self):
        if self.time_signature_checkbox_var.get() == 0:
            return None
        numerator = self.time_signature_numerator_combo.get()
        denominator = self.time_signature_denominator_combo.get()
        time_signature = f"{numerator}/{denominator}"

        return time_signature

    def confirm_selection(self):

        selected_number = self.input_entry.get()
        self.current_time_signature = self.get_current_time_signature()
        
        if selected_number.isdigit():
            self.selected_number = int(selected_number)
            self.destroy()
            self.parent.focus_set()

    def pick_info(self) -> Tuple[int, str]:
        """Get user input on music information

        Returns:
            Tuple[int, str]: bpm, timeSignature (None if none selected)
        """
        self.wait_window()
        return (self.selected_number, self.current_time_signature)
    

if __name__ == "__main__":
    root = tk.Tk()
    app = MusicInfoWindow(root, suggested_bpms=[50, 100], percentage_quarter_rythms=[10, 20])
    
    app.pack()
    print(app.pick_info())
    root.mainloop()