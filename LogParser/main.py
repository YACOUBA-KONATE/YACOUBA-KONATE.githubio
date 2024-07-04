#Required library
from email.mime.application import MIMEApplication
import pprint
from tkcalendar import Calendar
import datetime
from datetime import datetime
from tkinter.font import Font
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from tkinter.scrolledtext import ScrolledText
import pandas as pd  
import matplotlib.pyplot as plt 
from tksheet import Sheet
import re
import seaborn as sns 
import smtplib
import ssl
import json
from pretty_html_table import build_table
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

class MyGUI:
    def __init__(self):      
        self.root = tk.Tk()
        self.root.title("LOG PARSER GUI")

        # Create a Text widget for line numbers
        self.line_numbers = tk.Text(self.root, width=4, padx=3, takefocus=0, border=0, background='lightgrey', state='disabled', wrap='none')
        self.line_numbers.pack(side='left', fill='y')
        # Create a Font object with bold weight for the line numbers
        self.line_number_font = Font(family='Helvetica', size=10, weight='bold')

        # Apply the bold font to the line numbers Text widget
        self.line_numbers.configure(font=self.line_number_font)

        # Create a ScrolledText widget for the main text
        self.textbox = ScrolledText(self.root, height=20, width=80)
        self.textbox.pack(expand=True, fill='both', padx=10, pady=10)
        self.textbox.bind('<KeyRelease>', self.on_key_release)
        self.textbox.bind('<MouseWheel>', self.on_mouse_wheel)
       
       #create the main button after the textbox
        self.main_button()

        self.sheet = None  # Initialize sheet variable

        self.root.protocol("WM_DELETE_WINDOW",self.on_closing)
        self.root.mainloop()

    def main_button(self):
        # Create a frame to hold the buttons
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack()

        # Create the Open File button
        self.OpenButton = tk.Button(self.button_frame, text="Open File", command=self.On_Opening)
        self.OpenButton.pack(side='left', padx=5, pady=5)

        # Separator as a line
        separator1 = ttk.Separator(self.button_frame, orient='vertical')
        separator1.pack(side='left', fill='y', padx=5)

        # Create Parse Fille button
        self.ParseButton = tk.Button(self.button_frame, text="Parse Log File", command=self.On_Parse)
        self.ParseButton.pack(side='left', padx=5, pady=5)

        # Another separator as a line
        separator2 = ttk.Separator(self.button_frame, orient='vertical')
        separator2.pack(side='left', fill='y', padx=5)

        # Create Analyze Data via button
        self.ExportDataBtn = tk.Button(self.button_frame, text="Analyze Data", command=self.On_Analyze)
        self.ExportDataBtn.pack(side='left', padx=5, pady=5)

        # Another separator as a line
        separator3 = ttk.Separator(self.button_frame, orient='vertical')
        separator3.pack(side='left', fill='y', padx=5)

        # Create Export Data via Email button
        self.ExportDataBtn = tk.Button(self.button_frame, text="Export Data", command=self.Send_mail)
        self.ExportDataBtn.pack(side='left', padx=5, pady=5)

    def on_closing(self):
        if messagebox.askyesno(title="Quit?", message="Do you really want to quit"):
            self.root.destroy()
  
    def On_Opening(self):
        # Open a file dialog and ask the user to select a text file
        dosyaTipi = [("Text Files", "*.txt"),("Log Files", "*.log")]
        file_path = filedialog.askopenfilename(filetypes=dosyaTipi)
        if file_path:
            self.textbox.delete('1.0', tk.END)
            try:
                # Open the file and read its contents
                with open(file_path, 'r') as file:
                    file_contents = file.read()
                
                # Display the file contents in the textbox
                self.textbox.delete('1.0', tk.END)  # Clear the current contents
                self.textbox.insert('1.0', file_contents)  # Insert new contents
                self.textbox.configure(state='disabled')  # Disable editing
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read the file: {e}")

 
    def On_Parse(self):
        logs = self.textbox.get("1.0", tk.END).strip()
        if logs:
            # Define the regex pattern for the log entry
            pattern = r'^(?P<host>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) - - \[(?P<datetime>[^\]]+)\] "(?P<method>\S+) (?P<encoded_request>[^"]+) HTTP/\d\.\d" (?P<status>\d{3}) (?P<size>\d+|-) "(?P<referrer>-|[^"]*)" "(?P<useragent>[^"]*)"'
            log_pattern = re.compile(pattern)
            
            # Lists to hold the extracted data
            ip_addrList = []  # IP address list
            dt_list = []      # Timestamp list
            mtod_lst = [] #method list
            rqst_lst = []     # Encoded request list
            rqststatus_lst = []  # Request status code list
            rqstsize_lst = []    # Request size list
            useragent_lst = []   # User agent list

            # Split logs into lines
            logs = logs.split('\n')
                
            for log in logs:
                match = log_pattern.search(log)
                if match:
                    # Extract data using named groups and then to lists
                    ip_addrList.append(match.group('host'))
                    dt_list.append(match.group('datetime'))
                    mtod_lst.append(match.group('method'))
                    rqst_lst.append(match.group('encoded_request'))
                    rqststatus_lst.append(match.group('status') if match.group('status').isdigit() else None)
                    rqstsize_lst.append(match.group('size') if match.group('size').isdigit() else None)
                    useragent_lst.append(match.group('useragent'))
                else:
                    continue

            # Create a DataFrame with the extracted data
            df = pd.DataFrame({
                'Host': ip_addrList,
                'Timestamp': dt_list,
                'Method': mtod_lst,
                'Request': rqst_lst,
                'Status': rqststatus_lst,
                'Size': rqstsize_lst,
                'Agent User': useragent_lst
            })

            #Data preprocessing
            df['Host'] = df['Host'].astype('category')
            df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%d/%b/%Y:%H:%M:%S %z')
            df['Method'] = df['Method'].astype('category')
            df['Request'] = df['Request'].astype('category')
            df['Status'] = df['Status'].astype('int16')
            df['Size'] = df['Size'].astype('int32')
            df['Agent User'] = df['Agent User'].astype('category')

            #df.info(verbose=True, show_counts=True)
            #pprint.pprint(df.shape)
            #pprint.pprint(df.head(10))
            #pprint.pprint(df['Timestamp'].unique)
            
            self.df = df
            
            #Clear the frame and create a Tksheet widget
            self.textbox.delete('1.0', tk.END)

            # Initialize Tksheet 
            if self.sheet:
                self.sheet.destroy()
            self.sheet = Sheet(self.textbox)
            self.sheet.pack(side="top", fill="both", expand=True)
          
            # Load DataFrame into Tksheet
            self.sheet.set_sheet_data(data=df.values.tolist())

            # Column headers
            self.sheet.headers(df.columns.tolist())

            self.apply_colors()
        else:
            messagebox.showinfo(title="Information", message="No data to parse.")
     
    def apply_colors(self):
        # Apply the background color across the entire column
        colors = ["#ADD8E6", "#90EE90", "#E6E6FA", "#FFFDD0", "#FFFFE0", "#F0FFFF", "#F5FFFA",'#F0F8FF']
        for col in range(self.sheet.total_columns()):
            for row in range(self.sheet.total_rows()):
                self.sheet.highlight_cells(row=row, column=col, bg=colors[col % len(colors)])
        
        # Call the function to autosize cells
        self.sheet.set_all_cell_sizes_to_text()
    
    def On_Analyze(self):
        df = self.df
        if not df.empty:
            try:
                # Disable existing buttons
                self.toggle_buttons_state('disable')

                # Remove existing buttons
                for widget in self.button_frame.winfo_children():
                    widget.destroy()
                
                 # Create new buttons for the four analysis functions
                self.create_analysis_buttons()

            except KeyError as e:
                messagebox.showerror("Error", f"Key error: {e}")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")
        else:
            messagebox.showinfo("Data need to be parse before the analysis")
            
    def toggle_buttons_state(self, state):
        for widget in self.button_frame.winfo_children():
            if isinstance(widget, tk.Button):
                widget.config(state=state)

    def previous_window(self):
       # Disable existing buttons
        self.toggle_buttons_state('disable')

        # Clear the current contents
        self.textbox.delete('1.0', tk.END)
            
        # Remove existing buttons
        for widget in self.button_frame.winfo_children():
            widget.destroy()
                
        # Create new buttons for the four analysis functions
        self.main_button()

    def create_analysis_buttons(self):
        #Toggle for the previous buttons 
        traffic_analysisButton = tk.Button(self.button_frame, text="Back", command=self.previous_window)
        traffic_analysisButton.pack(side='left', padx=5, pady=5)

         # separator as a line
        separator0 = ttk.Separator(self.button_frame, orient='vertical')
        separator0.pack(side='left', fill='y', padx=5)
    
        # traffic_analysis
        traffic_analysisButton = tk.Button(self.button_frame, text="Daily Request Analysis", command=self.traffic_analysis)
        traffic_analysisButton.pack(side='left', padx=5, pady=5)

        # separator as a line
        separator1 = ttk.Separator(self.button_frame, orient='vertical')
        separator1.pack(side='left', fill='y', padx=5)

        # user_behavior_analysis
        user_behavior_analysisButton = tk.Button(self.button_frame, text="User Behavior Analysis", command=self.user_behavior_analysis)
        user_behavior_analysisButton.pack(side='left', padx=5, pady=5)

        # separator as a line
        separator2 = ttk.Separator(self.button_frame, orient='vertical')
        separator2.pack(side='left', fill='y', padx=5)

        # performance_analysis
        performance_analysisButton = tk.Button(self.button_frame, text="Performance Analysis", command=self.performance_analysis)
        performance_analysisButton.pack(side='left', padx=5, pady=5)

        # separator as a line
        separator3 = ttk.Separator(self.button_frame, orient='vertical')
        separator3.pack(side='left', fill='y', padx=5)

        # error_analysis
        error_analysisButton = tk.Button(self.button_frame, text="Status Code Analysis", command=self.status_code_analysis)
        error_analysisButton.pack(side='left', padx=5, pady=5)

    def previous_window_analysis(self):
       # Disable existing buttons
        self.toggle_buttons_state('disable')

        # Clear the current contents
        self.textbox.delete('1.0', tk.END)
            
        # Remove existing buttons
        for widget in self.button_frame.winfo_children():
            widget.destroy()
                
        # Create new buttons for the four analysis functions
        self.create_analysis_buttons()


    def traffic_analysis(self):
        log_data = self.df

        # Remove existing buttons
        for widget in self.button_frame.winfo_children():
            widget.destroy()
        
       #resize the button frame
        self.button_frame.pack(pady=40)
        
       #Toggle for the previous buttons 
        Back_Button = tk.Button(self.button_frame, text="Back", command=self.previous_window_analysis)
        Back_Button.pack(side='left', padx=5, pady=5)
        
        # separator as a line
        separatorb = ttk.Separator(self.button_frame, orient='vertical')
        separatorb.pack(side='left', fill='y', padx=5)

        # Dropdown for IP selection
        self.ip_combobox_labela = tk.Label(self.button_frame, text='Select IP Address:')
        self.ip_combobox_labela.pack(side=tk.LEFT, fill='x')
        
        self.ip_comboboxa = ttk.Combobox(self.button_frame)
        self.ip_comboboxa['values'] =  ['All'] + list(log_data['Host'].unique())
        self.ip_comboboxa.pack(side=tk.LEFT, fill='x')

        # separator as a line
        separatorc = ttk.Separator(self.button_frame, orient='vertical')
        separatorc.pack(side='left', fill='y', padx=5)

        # Add Calendar for start date selection
        self.start_date_label = tk.Label(self.button_frame, text='Start Date:')
        self.start_date_label.pack(side=tk.LEFT)
        self.start_calendar = Calendar(self.button_frame)
        self.start_calendar.pack(side=tk.LEFT)

        # separator as a line
        separatordr = ttk.Separator(self.button_frame, orient='vertical')
        separatordr.pack(side='left', fill='y', padx=5)

        # Add Calendar for end date selection
        self.end_date_label = tk.Label(self.button_frame, text='End Date:')
        self.end_date_label.pack(side=tk.LEFT)
        self.end_calendar = Calendar(self.button_frame)
        self.end_calendar.pack(side=tk.LEFT)

        # separator as a line
        separatord = ttk.Separator(self.button_frame, orient='vertical')
        separatord.pack(side='left', fill='y', padx=5)

        # Button to confirm date selection and plot data
        self.plot_button = tk.Button(self.button_frame, text='Plot Data', command=self.show_daily_request)
        self.plot_button.pack(side=tk.LEFT)

    def show_daily_request(self):

        ip_address = self.ip_comboboxa.get()
        
        # Get selected dates
        start_date = self.start_calendar.get_date()
        end_date = self.end_calendar.get_date()

        log_df = self.df

        log_df['Timestamp'] = pd.to_datetime(log_df['Timestamp'])
        
        # Extract date from timestamp
        log_df['Date'] = log_df['Timestamp'].dt.date

        min_date = log_df['Date'].min()
        max_date = log_df['Date'].max()

        # Convert string dates to datetime objects
        start_date = datetime.strptime(start_date, '%m/%d/%y').date()
        end_date = datetime.strptime(end_date, '%m/%d/%y').date()
        
        if ip_address and  ((start_date >= min_date) and (end_date <= max_date)):

            user_requests = log_df[log_df['Host'] == ip_address]

            if ip_address != 'All':
                # Group by date and count requests
                daily_counts = user_requests.groupby('Date')['Host'].count()
            else:
                # Group by date and count the number of requests
                daily_counts = log_df.groupby('Date')['Host'].count()

            # Plot the data
            plt.figure(figsize=(12, 6))
            plt.bar(daily_counts.index.astype(str), daily_counts.values)
            plt.xlabel('Date')
            plt.ylabel('Number of Requests')
            plt.title(f'Total Number of Requests per Day for: {ip_address}')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()
        else:
            messagebox.showinfo(title="info", message="Please select an ip address or a valid date")

    #status code analysis Method
    def status_code_analysis(self):
        log_data = self.df

        # Remove existing buttons
        for widget in self.button_frame.winfo_children():
            widget.destroy()

        # Resize the button frame
        self.button_frame.pack(pady=40)

        # Toggle for the previous buttons
        Back_ButtonSC = tk.Button(self.button_frame, text="Back", command=self.previous_window_analysis)
        Back_ButtonSC.pack(side='left', padx=5, pady=5)

        # Separator as a line
        separatorsc = ttk.Separator(self.button_frame, orient='vertical')
        separatorsc.pack(side='left', fill='y', padx=5)

        # Dropdown for IP selection
        self.ip_combobox_labelsc = tk.Label(self.button_frame, text='Select IP Address:')
        self.ip_combobox_labelsc.pack(side=tk.LEFT, fill='x')

        # Add "All" to the list of IP addresses
        ip_values = ['All'] + list(log_data['Host'].unique())
        self.ip_comboboxsc = ttk.Combobox(self.button_frame, values=ip_values)
        self.ip_comboboxsc.pack(side=tk.LEFT, fill='x')

        # Separator as a line
        separatorc = ttk.Separator(self.button_frame, orient='vertical')
        separatorc.pack(side='left', fill='y', padx=5)

        # Button to show status code histogram
        self.show_buttonsc = tk.Button(self.button_frame, text='Show Status Code Summary', command=self.plot_status_code)
        self.show_buttonsc.pack(side=tk.LEFT, fill='x')

    def plot_status_code(self):
        selected_ip = self.ip_comboboxsc.get()
        log_df = self.df

        if selected_ip:
            if selected_ip != 'All':
                filtered_df = log_df[log_df['Host'] == selected_ip]
            else:
                filtered_df = log_df

            # Group data by 'Status' and count occurrences
            status_counts = filtered_df['Status'].value_counts()

            # Create a grouped bar chart
            plt.figure(figsize=(10, 6))
            sns.set_theme(style='darkgrid')
            status_counts.plot(kind='bar', color='skyblue', edgecolor='black')
            plt.title(f'Status Code Distribution for Host: {selected_ip}', fontsize=12, fontweight='bold')
            plt.xlabel('Status Codes')
            plt.ylabel('Count')
            plt.xticks(rotation=45, ha='right')
            plt.show()
        else:
            messagebox.showinfo(title="Info", message="Please select an IP address or choose 'All'.")

    #User Behavior analysis
    def user_behavior_analysis(self):
        log_data = self.df

        # Remove existing buttons
        for widget in self.button_frame.winfo_children():
            widget.destroy()

        # Resize the button frame
        self.button_frame.pack(pady=40)

        # Toggle for the previous buttons
        Back_Buttonbh= tk.Button(self.button_frame, text="Back", command=self.previous_window_analysis)
        Back_Buttonbh.pack(side='left', padx=5, pady=5)

        # Separator as a line
        separatorbh = ttk.Separator(self.button_frame, orient='vertical')
        separatorbh.pack(side='left', fill='y', padx=5)

        # Dropdown for IP selection
        self.ip_combobox_labelbh = tk.Label(self.button_frame, text='Select IP Address:')
        self.ip_combobox_labelbh.pack(side=tk.LEFT, fill='x')

        # Add "All" to the list of IP addresses
        ip_values = ['All'] + list(log_data['Host'].unique())
        self.ip_comboboxbh = ttk.Combobox(self.button_frame, values=ip_values)
        self.ip_comboboxbh.pack(side=tk.LEFT, fill='x')

        # Separator as a line
        separatorbh3 = ttk.Separator(self.button_frame, orient='vertical')
        separatorbh3.pack(side='left', fill='y', padx=5)

        # Dropdown for number of visted pages
        self.ip_combobox_labelvp= tk.Label(self.button_frame, text='Select the number of page:')
        self.ip_combobox_labelvp.pack(side=tk.LEFT, fill='x')

        #use list comprehension for data casting from int to str
        number_of_pages = [str(x) for x in range(1, 11)]
        self.np_comboboxvp = ttk.Combobox(self.button_frame, values=number_of_pages)
        self.np_comboboxvp.pack(side=tk.LEFT, fill='x')

        # Separator as a line
        separatorbh4 = ttk.Separator(self.button_frame, orient='vertical')
        separatorbh4.pack(side='left', fill='y', padx=5)

        # Button to show the plot
        self.show_buttonbh = tk.Button(self.button_frame, text='Show Top Visited Pages', command=self.top_pages)
        self.show_buttonbh.pack(side=tk.LEFT, fill='x')

    def top_pages(self):
        selected_ip = self.ip_comboboxbh.get()
        selected_num = self.np_comboboxvp.get()
        log_df = self.df

        if selected_ip and selected_num:
            if selected_ip != 'All':
                filtered_df = log_df[log_df['Host'] == selected_ip]
            else:
                filtered_df = log_df

            top_pg_counts =  filtered_df['Request'].value_counts().nlargest(int(selected_num))
            
            plt.figure(figsize=(10, 6))
            sns.countplot(x='Request', data=filtered_df, order=top_pg_counts.index)
            plt.xlabel('Most Visited Pages')
            plt.ylabel('Request Count')
            plt.title(f'Top {int(selected_num)} Pages Requests Count by {selected_ip}')
            plt.xticks(rotation=45)
            plt.show()
        else:
            messagebox.showinfo(title="Info", message="Please select an ip address and number of page.")

    #Performance analysis method
    def performance_analysis(self):
        log_data = self.df

        # Remove existing buttons
        for widget in self.button_frame.winfo_children():
            widget.destroy()

        # Resize the button frame
        self.button_frame.pack(pady=40)

        # Toggle for the previous buttons
        Back_Buttonpa = tk.Button(self.button_frame, text="Back", command=self.previous_window_analysis)
        Back_Buttonpa.pack(side='left', padx=5, pady=5)

        # Separator as a line
        separatorpa = ttk.Separator(self.button_frame, orient='vertical')
        separatorpa.pack(side='left', fill='y', padx=5)

        # Dropdown for IP selection
        self.ip_combobox_labelpa = tk.Label(self.button_frame, text='Select IP Address:')
        self.ip_combobox_labelpa.pack(side=tk.LEFT, fill='x')

        ip_values = list(log_data['Host'].unique())
        self.ip_comboboxpa = ttk.Combobox(self.button_frame, values=ip_values)
        self.ip_comboboxpa.pack(side=tk.LEFT, fill='x')

        # Separator as a line
        separatorpa2 = ttk.Separator(self.button_frame, orient='vertical')
        separatorpa2.pack(side='left', fill='y', padx=5)

        # Button to show status code histogram
        self.show_buttonrt = tk.Button(self.button_frame, text='Show Average Resquest Size', command=self.average_request_size)
        self.show_buttonrt.pack(side=tk.LEFT, fill='x')
 
    def average_request_size(self):
        selected_ip = self.ip_comboboxpa.get()
        log_df = self.df

        if selected_ip:

            # Group by method request type and compute the average of the size of requests
            avg_request_size = log_df.groupby('Method', observed=True)['Size'].mean()

            # Create a bar plot
            plt.figure(figsize=(10, 6))
            sns.set_theme(style='whitegrid')
            sns.set_palette("Set1")
            sns.barplot(x='Method', y='Size', data=avg_request_size.reset_index())
            plt.title(f'Average Request Size for IP: {selected_ip}', fontsize=12, fontweight='bold')
            plt.xlabel('HTTP Methods')
            plt.ylabel('Request Size (byte)')
            plt.xticks(rotation=45, ha='right')
            plt.show()
        else:
            messagebox.showinfo(title="Info", message="Please select an IP address")


    #Send mail method
    def Send_mail(self):
        if not self.df.empty:
            # Load email configuration
            with open('config.json', 'r') as config_file:
                self.email_config = json.load(config_file)

            # Create the root MIMEMultipart message
            message = MIMEMultipart("mixed")
            message["From"] = self.email_config["username"]
            message["To"] = self.email_config["recipient"]
            message["Subject"] = "Testing mail with our python"

            # Attach the plain text content
            message.attach(MIMEText("Please find the attached parsed data.", "plain"))

            # Create the HTML part
            html_part = MIMEMultipart("alternative")

            mail_body = f"""
            Hello, this is report of the <b>parsed document</b> here is table of content:
            {build_table(self.df, "blue_light")} for further analysis purpose.

            Thanks and best Regards
            <br>
            YACOUBA KONATE
            """
            html_part.attach(MIMEText(mail_body, "html"))

            # Attach the HTML part to the root message
            message.attach(html_part)

            df_file = self.df

            # Save it to a CSV file named parsed_log_file.csv
            df_file.to_csv('parsed_log_file.csv', index=False)

            # Read the CSV file and attach it
            with open("parsed_log_file.csv", "rb") as f:
                file_data = f.read()
                # Correct MIME type for a CSV file
                message.attach(MIMEApplication(_data=file_data, _subtype='octet-stream', Name='parsed_log_file.csv'))

            # Send the email
            try:
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(self.email_config["host"], self.email_config["port"], context=context) as server:
                    server.login(self.email_config["username"], self.email_config["password"])
                    server.send_message(message)
                messagebox.showinfo("Success", "Email sent successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")
        else:
            messagebox.showinfo( title="info", message="Please, parse the data first")

    def on_key_release(self, event=None):
        self.update_line_numbers()

    def on_mouse_wheel(self, event=None):
        self.update_line_numbers()

    def update_line_numbers(self):
        # Get the current line count
        lines = self.textbox.get('1.0', 'end-1c').split('\n')
        line_number_string = '\n'.join(str(i + 1) for i in range(len(lines)))
        
        # Update the line numbers
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', 'end')
        self.line_numbers.insert('1.0', line_number_string)
        self.line_numbers.config(state='disabled')
MyGUI()