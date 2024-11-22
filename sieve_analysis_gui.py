import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
import numpy as np
from sieve_analysis import generate_plot
import ttkthemes

class ModernButton(ttk.Button):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, style='Modern.TButton', **kwargs)

class SieveAnalysisGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sieve Analysis Tool")
        self.root.geometry("1200x800")
        
        # Apply modern theme
        self.style = ttkthemes.ThemedStyle(root)
        self.style.set_theme("arc")
        
        # Configure custom styles
        self.configure_styles()
        
        # Create main container
        main_frame = ttk.Frame(root)
        main_frame.pack(fill='both', expand=True)
        
        # Create canvas with scrollbar
        canvas = tk.Canvas(main_frame, bg='#f0f0f5')
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollbar_x = ttk.Scrollbar(main_frame, orient="horizontal", command=canvas.xview)
        
        # Create scrollable frame
        self.scrollable_frame = ttk.Frame(canvas, style='Main.TFrame')
        
        # Configure scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Create window in canvas
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set, xscrollcommand=scrollbar_x.set)
        
        # Pack scrollbar components
        scrollbar.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")
        canvas.pack(side="left", fill="both", expand=True)
        
        # Main container with padding
        content_frame = ttk.Frame(self.scrollable_frame, padding="20", style='Main.TFrame')
        content_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title Label
        title_label = ttk.Label(
            content_frame,
            text="Sieve Analysis Tool",
            style='Title.TLabel'
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Sample Configuration Frame
        sample_frame = ttk.LabelFrame(
            content_frame,
            text="Sample Configuration",
            padding="10",
            style='Card.TLabelframe'
        )
        sample_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(sample_frame, text="Number of Samples:", style='Subtitle.TLabel').grid(row=0, column=0, padx=5)
        self.num_samples = ttk.Spinbox(
            sample_frame,
            from_=1, to=10,
            width=5,
            style='Modern.TSpinbox'
        )
        self.num_samples.grid(row=0, column=1, padx=5)
        self.num_samples.set("1")
        
        update_btn = ModernButton(
            sample_frame,
            text="Update",
            command=self.update_sample_fields
        )
        update_btn.grid(row=0, column=2, padx=5)
        
        # Interpolation Options Frame
        interp_frame = ttk.LabelFrame(
            content_frame,
            text="Interpolation Options",
            padding="10",
            style='Card.TLabelframe'
        )
        interp_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Interpolation method
        ttk.Label(interp_frame, text="Interpolation Method:", style='Subtitle.TLabel').grid(row=0, column=0, padx=5)
        self.interp_method = ttk.Combobox(
            interp_frame,
            values=['linear', 'cubic', 'nearest'],
            width=15,
            style='Modern.TCombobox'
        )
        self.interp_method.grid(row=0, column=1, padx=5)
        self.interp_method.set('cubic')
        
        # Handle null values method
        ttk.Label(interp_frame, text="Handle Null Values:", style='Subtitle.TLabel').grid(row=0, column=2, padx=5)
        self.null_method = ttk.Combobox(
            interp_frame,
            values=['interpolate', 'ignore', 'zero'],
            width=15,
            style='Modern.TCombobox'
        )
        self.null_method.grid(row=0, column=3, padx=5)
        self.null_method.set('interpolate')
        
        # Extrapolation option
        self.extrapolate_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            interp_frame,
            text="Allow Extrapolation",
            variable=self.extrapolate_var,
            style='Modern.TCheckbutton'
        ).grid(row=0, column=4, padx=5)
        
        # Data Entry Frame
        self.data_frame = ttk.LabelFrame(
            content_frame,
            text="Sample Data",
            padding="10",
            style='Card.TLabelframe'
        )
        self.data_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Appearance Options Frame
        appearance_frame = ttk.LabelFrame(
            content_frame,
            text="Appearance Options",
            padding="10",
            style='Card.TLabelframe'
        )
        appearance_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        self.color_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            appearance_frame,
            text="Use Colors",
            variable=self.color_var,
            style='Modern.TCheckbutton'
        ).grid(row=0, column=0, padx=5)
        
        # Generate Button
        generate_btn = ModernButton(
            content_frame,
            text="Generate Plot",
            command=self.generate_plot
        )
        generate_btn.grid(row=5, column=0, columnspan=2, pady=20)
        
        self.sample_entries = []
        self.update_sample_fields()
    
    def configure_styles(self):
        # Configure custom styles
        self.style.configure(
            'Title.TLabel',
            font=('Helvetica', 24, 'bold'),
            foreground='#000000',
            background='#f0f0f5'
        )
        
        self.style.configure(
            'Subtitle.TLabel',
            font=('Helvetica', 12),
            foreground='#000000',
            background='#ffffff'
        )
        
        self.style.configure(
            'Card.TLabelframe',
            background='#ffffff',
            relief='solid',
            borderwidth=1
        )
        
        self.style.configure(
            'Card.TLabelframe.Label',
            font=('Helvetica', 12, 'bold'),
            foreground='#000000',
            background='#ffffff'
        )
        
        self.style.configure(
            'Main.TFrame',
            background='#f0f0f5'
        )
        
        self.style.configure(
            'Modern.TButton',
            font=('Helvetica', 11),
            background='#ffffff',
            foreground='#000000'
        )
        
        self.style.map('Modern.TButton',
            foreground=[('active', '#000000')],
            background=[('active', '#e6e6e6')]
        )
        
        self.style.configure(
            'Modern.TCheckbutton',
            font=('Helvetica', 11),
            background='#ffffff',
            foreground='#000000'
        )
        
        self.style.configure(
            'Modern.TCombobox',
            font=('Helvetica', 11),
            background='#ffffff',
            foreground='#000000'
        )
        
        self.style.configure(
            'Modern.TSpinbox',
            font=('Helvetica', 11),
            background='#ffffff',
            foreground='#000000'
        )
    
    def update_sample_fields(self):
        # Clear existing entries
        for widget in self.data_frame.winfo_children():
            widget.destroy()
        
        self.sample_entries.clear()
        num_samples = int(self.num_samples.get())
        
        # Standard IS sieve sizes
        sieve_sizes = [0.075, 0.15, 0.3, 0.6, 1.18, 2.36, 4.75, 10.0, 20.0, 40.0, 53.0]
        
        # Headers with modern style
        headers = ['Sample Name', 'Passing Values (%) for Each Sieve Size']
        for i, header in enumerate(headers):
            ttk.Label(
                self.data_frame,
                text=header,
                style='Subtitle.TLabel'
            ).grid(row=0, column=i, padx=10, pady=(0, 10))
        
        # Sieve size labels
        for i, size in enumerate(sieve_sizes):
            ttk.Label(
                self.data_frame,
                text=f"{size} mm",
                style='Subtitle.TLabel'
            ).grid(row=0, column=i+2, padx=5, pady=(0, 10))
        
        # Create entry fields for each sample
        for i in range(num_samples):
            sample_entry = {}
            
            # Sample name entry
            name_entry = ttk.Entry(
                self.data_frame,
                width=20,
                font=('Helvetica', 11)
            )
            name_entry.grid(row=i+1, column=0, padx=10, pady=5)
            name_entry.insert(0, f"Sample {i+1}")
            sample_entry['name'] = name_entry
            
            # Individual entry boxes for each sieve size
            value_entries = []
            for j, _ in enumerate(sieve_sizes):
                value_entry = ttk.Entry(
                    self.data_frame,
                    width=8,
                    font=('Helvetica', 11)
                )
                value_entry.grid(row=i+1, column=j+2, padx=2, pady=5)
                value_entries.append(value_entry)
            sample_entry['value_entries'] = value_entries
            
            self.sample_entries.append(sample_entry)
    
    def generate_plot(self):
        try:
            samples_data = []
            sieve_sizes = [0.075, 0.15, 0.3, 0.6, 1.18, 2.36, 4.75, 10.0, 20.0, 40.0, 53.0]
            
            for idx, entry in enumerate(self.sample_entries):
                name = entry['name'].get()
                
                # Get values from individual entry boxes
                values = []
                null_indices = []
                for i, value_entry in enumerate(entry['value_entries']):
                    val = value_entry.get().strip().lower()
                    if val in ['null', '', 'none']:
                        values.append(None)
                        null_indices.append(i)
                    else:
                        try:
                            values.append(float(val))
                        except ValueError:
                            messagebox.showerror("Error", f"Invalid value in sample {idx+1} for sieve size {sieve_sizes[i]} mm")
                            return
                
                samples_data.append({
                    'name': name,
                    'sizes': sieve_sizes,
                    'values': values,
                    'null_indices': null_indices
                })
            
            # Generate plot with interpolation options
            generate_plot(
                samples_data,
                use_color=self.color_var.get(),
                interp_method=self.interp_method.get(),
                null_method=self.null_method.get(),
                allow_extrapolation=self.extrapolate_var.get()
            )
            
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = SieveAnalysisGUI(root)
    root.mainloop()
