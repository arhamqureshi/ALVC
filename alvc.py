# importing tkinter module
import time, threading, ctypes, os, json
from tkinter import (
    Tk, Entry, Label, StringVar, IntVar, Button, DISABLED, NORMAL, HORIZONTAL,
    filedialog, Frame, Radiobutton, messagebox, E, SUNKEN, RIDGE, END, font
)
from tkinter.ttk import Progressbar
from slicer import create_clips
from pathlib import Path
import webbrowser

__version__ = "v1.0.0"

class AnalyseGameplay(threading.Thread): 
    """
    Runs the actual process of analysing the gameplay. This needs to be
    done in a separate thread so that the GUI can function as expected.
    This class takes the GUI as an input so that it can continously update
    the GUI as the process progresses.
    """
    def __init__(self, gui): 
        threading.Thread.__init__(self) 
        self.gui = gui
              
    def run(self):
        # Get all the inputs from the GUI and set them
        self.pre = float(self.gui.pre_input.get())
        self.post = float(self.gui.post_input.get())
        self.sample_rate = int(self.gui.sample_rate_input.get())
        self.delete = True if int(self.gui.delete_bool.get()) == 1 else False
        self.input_directory = self.gui.input_directory.get()
        self.output_directory = self.gui.output_directory.get()

        try: 
            cont = True
            exists = False
            while cont: 
                recordings_dir = self.input_directory
                output_dir = self.output_directory
                exists, files = self.search_video_files(recordings_dir)
                total = len(files)
                if exists:
                    for idx, _file in enumerate(files):
                        self.gui.update_progress("process", (idx / total) * 100, idx, total)
                        self.gui.video_name['text'] = "Processing {}".format(_file)
                        create_clips(
                            input_dir=recordings_dir,
                            filename=_file,
                            output_dir=output_dir,
                            merge=False,
                            pre=self.pre,
                            post=self.post,
                            delete=self.delete,
                            sample_rate=self.sample_rate,
                            gui=self.gui
                        )
                    cont = False
                else:
                    messagebox.showerror("No Compatible Video Files", "No compatible video files found. Supported video files: .mp4")
                    cont = False
            self.gui.stop_analysis(analysis_complete=exists)
        finally:
            print('Process Terminated') 

           
    def get_id(self): 
        if hasattr(self, '_thread_id'): 
            return self._thread_id 
        for id, thread in threading._active.items(): 
            if thread is self: 
                return id
   
    def search_video_files(self, directory):
        """
        Search the input directory for compatible video files and return
        the list of valid files. These will be the files that are actually
        processed.
        """
        valid_files = []
        exists = True
        accepted_formats = ['mp4']
        for _file in os.listdir(directory):
            if _file.rsplit(".", 1)[-1] in accepted_formats:
                valid_files.append(_file)
        if len(valid_files) == 0:
            exists = False
        return exists, valid_files

    def raise_exception(self): 
        thread_id = self.get_id() 
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 
              ctypes.py_object(SystemExit)) 
        if res > 1: 
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0) 
            # print('Exception raise failure') 

class GUI(Frame):
    """
    The GUI is defined and created using this class
    """

    def __init__(self, gui):
        Frame.__init__(self, gui)
        self.gui = gui

        # Create the different sections in the GUI.
        self.information = Frame(self.gui)
        self.information.grid(row=0, column=0, padx=20, pady=10)

        self.inputs = Frame(self.gui, relief=RIDGE, borderwidth=3)
        self.inputs.grid(row=1, column=0, padx=20, pady=10)

        self.selection = Frame(self.gui, relief=RIDGE, borderwidth=3)
        self.selection.grid(row=2, column=0, padx=20, pady=10)

        self.progress = Frame(self.gui, relief=RIDGE, borderwidth=3)
        self.progress.grid(row=3, column=0, padx=20, pady=10)

        self.buttons = Frame(self.gui)
        self.buttons.grid(row=4, column=0, padx=20, pady=5)

        self.gui.title("ALVC ({})".format(__version__))
        
        # Create a settings file which is stored in the users home directory
        # This file saves the settings set so they don't reset to the defaults
        # every time the app is launched.
        self.create_settings_file()
        self.data = self.get_settings_data() # Get the saved settings.

        # Content for the first section which includes some information
        self.title = Label(self.information, text="Apex Legends Video Clipper")
        self.title.configure(font="Helvetica 12 bold")
        self.title.grid(row=0)

        self.version = Label(self.information, text=__version__)
        self.version.configure(font="Helvetica 9")
        self.version.grid(row=1)

        self.link = Label(self.information, text="What does all this mean?", fg="blue", cursor="hand2")
        self.link.grid(row=2)
        self.f = font.Font(self.link, self.link.cget("font"))
        self.f.configure(underline=True)
        self.link.configure(font=self.f)
        self.link.bind("<Button-1>", lambda e: webbrowser.open_new("https://github.com/arhamqureshi/ALVC/blob/main/README.md#program-settings"))

        self.report_bug = Label(self.information, text="Report Bug", fg="blue", cursor="hand2")
        self.report_bug.grid(row=3)
        self.f = font.Font(self.report_bug, self.report_bug.cget("font"))
        self.f.configure(underline=True)
        self.report_bug.configure(font=self.f)
        self.report_bug.bind("<Button-1>", lambda e: webbrowser.open_new("https://github.com/arhamqureshi/ALVC/issues/new/choose"))

        # Content for the second section which includes settings for the clips
        self.inputs_title = Label(self.inputs, text="Clip Settings", width=35, pady=10)
        self.inputs_title.configure(font="Verdana 10 underline bold")
        self.inputs_title.grid(row=0, column=0)
        self.sample_rate_label = Label(self.inputs, text="Samples", width=35, pady=5)
        self.sample_rate_label.grid(row=1, column=0)
        self.sample_rate_input = Entry(self.inputs, width=5, validate="all", validatecommand=(self.register(self.on_validate), "int", "%d", "%s", "%P"))
        self.sample_rate_input.insert(0, self.data['sample_rate_input'])
        self.sample_rate_input.grid(row=1, column=1)

        self.pre_input_label = Label(self.inputs, text="Seconds to capture BEFORE knock/elim", width=35, pady=5)
        self.pre_input_label.grid(row=2, column=0)
        self.pre_input = Entry(self.inputs, width=5, validate="all", validatecommand=(self.register(self.on_validate), "float", "%d", "%s", "%P"))
        self.pre_input.insert(0, self.data['pre_input'])
        self.pre_input.grid(row=2, column=1)

        self.pre_input_label = Label(self.inputs, text="Seconds to capture AFTER knock/elim", width=35, pady=5)
        self.pre_input_label.grid(row=3, column=0)
        self.post_input = Entry(self.inputs, width=5, validate="all", validatecommand=(self.register(self.on_validate), "float", "%d", "%s", "%P"))
        self.post_input.insert(0, self.data['post_input'])
        self.post_input.grid(row=3, column=1)

        self.delete_bool = IntVar()
        self.delete_bool.set(int(self.data['delete_bool']))
        
        self.delete_label = Label(self.inputs, text="Delete original file after processing?", width=35, pady=5)
        self.delete_label.grid(row=4, column=0)

        self.delete_yes = Radiobutton(self.inputs, text='Yes', variable=self.delete_bool, value=1)
        self.delete_yes.grid(row=4, column=1)

        self.delete_no = Radiobutton(self.inputs, text='No', variable=self.delete_bool, value=0)
        self.delete_no.grid(row=4, column=2)

        # Content for the third section which includes settings for the input/output directories
        self.directories_title = Label(self.selection, text="Input & Output Folders", width=35, pady=10)
        self.directories_title.configure(font="Verdana 9 underline bold")
        self.directories_title.grid(row=0, column=0)

        self.input_directory = StringVar(value="Select Folder with Gameplay Videos" if self.data['input_directory'] == "" else self.data['input_directory'])
        self.input_directory_label = Entry(self.selection, textvariable=self.input_directory, state='readonly', width=48)
        self.input_directory_label.grid(row=1, column=0, padx=10, pady=10)
        self.input_directory_button = Button(self.selection, text="Select Folder", command=lambda: self.select_directory("input"))
        self.input_directory_button.grid(row=1, column=1, padx=10, pady=10)

        self.output_directory = StringVar(value="Select Folder to Store Clips" if self.data['output_directory'] == "" else self.data['output_directory'])
        self.output_directory_label = Entry(self.selection, textvariable=self.output_directory, state='readonly', width=48)
        self.output_directory_label.grid(row=2, column=0, padx=10, pady=10)
        self.output_directory_button = Button(self.selection, text="Select Folder", command=lambda: self.select_directory("output"))
        self.output_directory_button.grid(row=2, column=1, padx=10, pady=10)

        # Content for the fourth section which includes the progress bars etc.
        self.video_name = Label(self.progress, text="Click Start to Begin!")
        self.video_name.grid(row=0, column=0, padx=10, pady=5)

        self.video_progress_label = Label(self.progress, text="Video Progress: 0/0 Frames")
        self.video_progress_label.grid(row=1, column=0, padx=10, sticky='w')
        self.video_progress = Progressbar(self.progress, orient = HORIZONTAL, length = 390, mode = 'determinate')
        self.video_progress.grid(row=2, column=0, padx=10, pady=10)

        self.process_progress_label = Label(self.progress, text="Overall Progress: 0/0 Videos")
        self.process_progress_label.grid(row=3, column=0, padx=10, sticky="w")
        self.process_progress = Progressbar(self.progress, orient = HORIZONTAL, length = 390, mode = 'determinate')
        self.process_progress.grid(row=4, column=0, padx=10, pady=5)

        self.start_button = Button(self.buttons, text='Start', command=self.start_analysis, width=27)
        self.start_button.grid(row=0, column=0, padx=10)
        
        self.cancel_button = Button(self.buttons, text='Cancel', command=self.cancel, width=27)
        self.cancel_button['state'] = DISABLED
        self.cancel_button.grid(row=0, column=1, padx=10)

        self.analyse_gameplay = AnalyseGameplay(self)

    def cancel(self):
        if messagebox.askyesno("Cancel?", "Are you sure you want to cancel?"):
            self.stop_analysis()
    
    def create_settings_file(self):
        """
        Creates a settings file with the default settings in the 
        users home directory if it doesn't exist already.
        """
        home_directory = Path.home()

        if ".alvc-settings.json" not in os.listdir(home_directory):
            default_settings = {
                "sample_rate_input": "30",
                "pre_input": "4",
                "post_input": "3",
                "delete_bool": "0",
                "input_directory": "",
                "output_directory": ""
            }

            with open(os.path.join(home_directory, ".alvc-settings.json"), "w") as write_file:
                json.dump(default_settings, write_file)

    
    def update_settings_data(self):
        """
        Updates the settings file with the new values defined
        in the GUI.
        """
        home_directory = Path.home()

        sample_text = self.sample_rate_input.get()
        pre_text = self.pre_input.get()
        post_text = self.post_input.get()
        delete_bool = self.delete_bool.get()
        input_directory = self.input_directory.get()
        output_directory = self.output_directory.get()

        new_settings = {
            "sample_rate_input": sample_text,
            "pre_input": pre_text,
            "post_input": post_text,
            "delete_bool": delete_bool,
            "input_directory": input_directory,
            "output_directory": output_directory
        }

        with open(os.path.join(home_directory, ".alvc-settings.json"), "w") as write_file:
            json.dump(new_settings, write_file)

    def get_settings_data(self):
        home_directory = Path.home()
        with open(os.path.join(home_directory, ".alvc-settings.json"), "r") as read_file:
            data = json.load(read_file)
        return data

    def start_analysis(self):
        valid, message = self.validate_fields()
        # If the fields are valid, disable all the input fields
        # and start the process
        if valid:
            self.update_settings_data()
            self.start_button['state'] = DISABLED
            self.input_directory_button['state'] = DISABLED
            self.output_directory_button['state'] = DISABLED
            self.input_directory_label['state'] = DISABLED
            self.output_directory_label['state'] = DISABLED
            self.pre_input['state'] = DISABLED
            self.post_input['state'] = DISABLED
            self.sample_rate_input['state'] = DISABLED
            self.delete_yes['state'] = DISABLED
            self.delete_no['state'] = DISABLED
            self.cancel_button['state'] = NORMAL
            self.analyse_gameplay = AnalyseGameplay(self)
            self.analyse_gameplay.start()
        else:
            messagebox.showerror("Error", message)

    def stop_analysis(self, analysis_complete=False):
        # Sets the fields to their defaualt state and stops the
        # analysis process.
        self.start_button['state'] = NORMAL
        self.input_directory_button['state'] = NORMAL
        self.output_directory_button['state'] = NORMAL
        self.input_directory_label['state'] = "readonly"
        self.output_directory_label['state'] = "readonly"
        self.pre_input['state'] = NORMAL
        self.post_input['state'] = NORMAL
        self.sample_rate_input['state'] = NORMAL
        self.delete_yes['state'] = NORMAL
        self.delete_no['state'] = NORMAL
        self.cancel_button['state'] = DISABLED
        self.video_name['text'] = "Click Start to Begin!"
        self.update_progress("video", 0, 0, 0)
        self.update_progress("process", 0, 0, 0)

        if analysis_complete:
            messagebox.showinfo("Analysis Complete", "Clips have been exported to {}".format(self.output_directory.get()))
        else:
            self.analyse_gameplay.raise_exception()
            messagebox.showinfo("Partial Analysis", "Clips captured before cancellation have been exported to {}".format(self.output_directory.get()))
            
        self.analyse_gameplay.raise_exception()
        self.analyse_gameplay = AnalyseGameplay(self)

    def select_directory(self, _type):
        folder_path = filedialog.askdirectory()
        if _type == "input":
            self.input_directory.set(folder_path)
            self.input_directory_label.delete(0, END)
            self.input_directory_label.insert(0, folder_path)

        if _type == "output":
            self.output_directory.set(folder_path)
            self.output_directory_label.delete(0, END)
            self.output_directory_label.insert(0, folder_path)

    def update_progress(self, bar, pct, val, total):
        if bar == "video":
            self.video_progress['value'] = pct
            self.video_progress_label['text'] = "Video Progress: {}/{} Frames".format(val, total)
        if bar == "process":
            self.process_progress['value'] = pct
            self.process_progress_label['text'] = "Overall Progress: {}/{} Videos".format(val, total)
        
        self.gui.update_idletasks()

    def validate_fields(self):
        messages = []
        errors = []
        pre_text = self.pre_input.get()
        post_text = self.post_input.get()
        sample_text = self.sample_rate_input.get()
        input_directory = self.input_directory.get()
        output_directory = self.output_directory.get()

        if pre_text == "":
            messages.append("Value Cannot be Empty")
            errors.append("False")

        if post_text == "":
            messages.append("Value Cannot be Empty")
            errors.append("False")
        
        if sample_text == "":
            messages.append("Value Cannot be Empty")
            errors.append("False")

        if input_directory == "Select Folder with Gameplay Videos" or input_directory == "":
            messages.append("Input Directory Cannot be Empty")
            errors.append("False")

        if not os.path.isdir(input_directory):
            messages.append("Input Directory Not Found")
            errors.append("False")

        if not os.path.isdir(output_directory):
            messages.append("Output Directory Not Found")
            errors.append("False")

        if output_directory == "Select Folder to Store Clips" or output_directory == "":
            messages.append("Output Directory Cannot be Empty")
            errors.append("False")

        if input_directory == output_directory:
            messages.append("Input & Output directories must be different")
            errors.append("False")

        if "False" in errors:
            message = ""
            for m in messages:
                message = message + " " + m + "\n"
            return False, message
        return True, "message"

    def on_validate(self, expected_type, action, current_val, future_val):
        if len(future_val) > 5:
            return False
        else:
            if future_val != "":
                try:
                    if expected_type == "float":
                        float(future_val)
                        return True
                    if expected_type == "int":
                        int(future_val)
                        return True
                    return False
                except Exception:
                    return False
            else:
                return True

if __name__ == "__main__":
    root = Tk()
    my_gui = GUI(root)
    root.mainloop()
