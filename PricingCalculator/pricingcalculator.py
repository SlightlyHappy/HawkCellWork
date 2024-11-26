import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
import pandas as pd
import numpy as np

class ExcelDataManager:
    def __init__(self):
        self.file_path = "/Users/rishabhkankash/Library/CloudStorage/OneDrive-HawkCell/CloudFiles/MFpullLatest.xlsx"
        self.products_df = None
        self.recurring_df = None
        self.load_data()
    
    def load_data(self):
        try:
            # Load Products sheet (SMALL ANIMALS)
            self.products_df = pd.read_excel(
                self.file_path, 
                sheet_name='SMALL ANIMALS',
                usecols=['ACI Update 2024: The pricing for 2025 will be based on the updated 2024 prices by ACI (Authority for Infrastructure Control).\nCPI Update: The Consumer Price Index (CPI) is expected to be updated with a 1.5% increase.\nAll pricing is in euros (€): Please note that all prices mentioned in this document are expressed in euros.\nExchange Rate for January 2024: The exchange rate for January 2024 is...',
                         'Unnamed: 3', 'Unnamed: 4', 'Unnamed: 5']
            )
            self.products_df.columns = ['Products', 'Description', 'Deliverables', 'Price Opening']
            
            # Load Recurring Pricing sheet
            self.recurring_df = pd.read_excel(
                self.file_path,
                sheet_name='HawkAI BackEnd Recur Pricing'
            )
            
            # Convert Country column to string
            self.recurring_df['Country'] = self.recurring_df['Country'].astype(str)
            
            # Clean the data
            self.clean_data()
            
            return True
        except Exception as e:
            print(f"Error loading Excel data: {e}")
            return False
    
    def clean_data(self):
        """Clean the loaded data"""
        # Clean products data
        self.products_df = self.products_df.fillna('')
        self.products_df = self.products_df.dropna(subset=['Products'])
        
        # Clean recurring data
        self.recurring_df = self.recurring_df.fillna(0)
        
    def get_products(self):
        """Get list of all products"""
        return sorted(self.products_df['Products'].unique())
    
    def get_countries(self):
        """Get list of all countries"""
        return sorted(self.recurring_df['Country'].unique())
    
    def get_volumes(self):
        """Get list of all volumes"""
        return sorted(self.recurring_df['Volume'].unique())
    
    def get_product_details(self, products):
        """Get details for selected products"""
        return self.products_df[self.products_df['Products'].isin(products)]
    
    def get_recurring_price(self, volume, country):
        """Get recurring price details based on volume and country"""
        mask = (self.recurring_df['Volume'] == volume) & (self.recurring_df['Country'] == country)
        return self.recurring_df[mask].iloc[0] if not self.recurring_df[mask].empty else None

class PricingCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Product Pricing Calculator")
        
        # Initialize data manager
        self.data_manager = ExcelDataManager()
        
        # Initialize variables
        self.selected_products = []
        self.selected_volume = tk.StringVar()
        self.selected_country = tk.StringVar()
        
        # Create main notebook
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(pady=10, expand=True, fill='both')
        
        # Create pages
        self.create_product_selection_page()
        self.create_recurring_price_page()
        self.create_summary_page()
        
        # Initialize total prices
        self.total_opening_price = 0
        self.total_recurring_price = 0
    
    def create_product_selection_page(self):
        """First page with multi-product selection and details"""
        page = ttk.Frame(self.notebook)
        self.notebook.add(page, text="Product Selection")
        
        # Product selection frame
        selection_frame = ttk.LabelFrame(page, text="Select Products", padding="10")
        selection_frame.pack(pady=10, padx=10, fill='both', expand=True)
        
        # Create listbox with scrollbar for multiple selection
        self.products_listbox = tk.Listbox(
            selection_frame, 
            selectmode='multiple',
            height=6
        )
        scrollbar = ttk.Scrollbar(selection_frame, orient="vertical")
        scrollbar.config(command=self.products_listbox.yview)
        self.products_listbox.config(yscrollcommand=scrollbar.set)
        
        self.products_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Populate listbox
        for product in self.data_manager.get_products():
            self.products_listbox.insert(tk.END, product)
        
        # Bind selection event
        self.products_listbox.bind('<<ListboxSelect>>', self.update_product_details)
        
        # Details frame
        self.details_frame = ttk.LabelFrame(page, text="Product Details", padding="10")
        self.details_frame.pack(pady=10, padx=10, fill='both', expand=True)
        
        # Create scrolled text widget for details
        self.details_text = scrolledtext.ScrolledText(
            self.details_frame,
            wrap=tk.WORD,
            height=10,
            width=50
        )
        self.details_text.pack(fill='both', expand=True)
        
        # Next button
        ttk.Button(
            page,
            text="Next →",
            command=lambda: self.notebook.select(1)
        ).pack(pady=10)
    
    def create_recurring_price_page(self):
        """Second page with volume and country selection"""
        page = ttk.Frame(self.notebook)
        self.notebook.add(page, text="Recurring Pricing")
        
        # Selection frame
        selection_frame = ttk.LabelFrame(page, text="Select Options", padding="10")
        selection_frame.pack(pady=10, padx=10, fill='both')
        
        # Volume selection
        ttk.Label(selection_frame, text="Select Volume:").pack(pady=5)
        volume_cb = ttk.Combobox(
            selection_frame,
            textvariable=self.selected_volume,
            values=self.data_manager.get_volumes(),
            state='readonly'
        )
        volume_cb.pack(pady=5)
        
        # Country selection
        ttk.Label(selection_frame, text="Select Country:").pack(pady=5)
        country_cb = ttk.Combobox(
            selection_frame,
            textvariable=self.selected_country,
            values=self.data_manager.get_countries(),
            state='readonly'
        )
        country_cb.pack(pady=5)
        
        # Bind selection events
        volume_cb.bind('<<ComboboxSelected>>', self.update_recurring_details)
        country_cb.bind('<<ComboboxSelected>>', self.update_recurring_details)
        
        # Details frame
        self.recurring_details_frame = ttk.LabelFrame(page, text="Pricing Details", padding="10")
        self.recurring_details_frame.pack(pady=10, padx=10, fill='both', expand=True)
        
        # Create scrolled text widget for recurring details
        self.recurring_text = scrolledtext.ScrolledText(
            self.recurring_details_frame,
            wrap=tk.WORD,
            height=10,
            width=50
        )
        self.recurring_text.pack(fill='both', expand=True)
        
        # Navigation buttons
        button_frame = ttk.Frame(page)
        button_frame.pack(pady=10, fill='x')
        
        ttk.Button(
            button_frame,
            text="← Back",
            command=lambda: self.notebook.select(0)
        ).pack(side='left', padx=20)
        
        ttk.Button(
            button_frame,
            text="Next →",
            command=self.update_summary
        ).pack(side='right', padx=20)
    
    def create_summary_page(self):
        """Third page with complete summary"""
        page = ttk.Frame(self.notebook)
        self.notebook.add(page, text="Summary")
        
        # Create scrolled text widget for summary
        self.summary_text = scrolledtext.ScrolledText(
            page,
            wrap=tk.WORD,
            height=20,
            width=60
        )
        self.summary_text.pack(pady=10, padx=10, fill='both', expand=True)
        
        # Back button
        ttk.Button(
            page,
            text="← Back",
            command=lambda: self.notebook.select(1)
        ).pack(pady=10)
    
    def update_product_details(self, event=None):
        """Update product details when selection changes"""
        self.selected_products = [
            self.products_listbox.get(idx) 
            for idx in self.products_listbox.curselection()
        ]
        
        if not self.selected_products:
            self.details_text.delete('1.0', tk.END)
            return
        
        # Get details for selected products
        details_df = self.data_manager.get_product_details(self.selected_products)
        
        # Calculate total opening price
        self.total_opening_price = details_df['Price Opening'].sum()
        
        # Format details text
        details_text = "Selected Products:\n\n"
        for _, row in details_df.iterrows():
            details_text += f"Product: {row['Products']}\n"
            details_text += f"Description: {row['Description']}\n"
            details_text += f"Deliverables: {row['Deliverables']}\n"
            details_text += f"Opening Price: ${row['Price Opening']:,.2f}\n"
            details_text += "-" * 50 + "\n"
        
        details_text += f"\nTotal Opening Price: ${self.total_opening_price:,.2f}"
        
        # Update text widget
        self.details_text.delete('1.0', tk.END)
        self.details_text.insert('1.0', details_text)
    
    # [Previous imports and ExcelDataManager class remain the same until the update_recurring_details method]

    def update_recurring_details(self, event=None):
        """Update recurring price details when volume or country changes"""
        volume = self.selected_volume.get()
        country = self.selected_country.get()
        
        if not volume or not country:
            return
        
        # Get recurring price details
        recurring_details = self.data_manager.get_recurring_price(volume, country)
        
        if recurring_details is not None:
            self.total_recurring_price = recurring_details['Price']
            
            details_text = f"Volume: {volume}\n"
            details_text += f"Country: {country}\n"
            details_text += f"Price: ${recurring_details['Price']:,.2f}\n"
            details_text += f"Discount Offered: {recurring_details['Discount offered']}%\n"
            details_text += f"Discount between plans: {recurring_details['Discount between plans (offered on the Pay-per-Scan - Standalone)']}\n"
            details_text += f"Above threshold fee: {recurring_details['Above  threshold  fee']}\n"
            # Fix the column name reference
            threshold_diff_col = 'Difference between threshold fees'  # Update this to match exact column name
            details_text += f"Difference between threshold fees: {recurring_details[threshold_diff_col]}\n"
            
            self.recurring_text.delete('1.0', tk.END)
            self.recurring_text.insert('1.0', details_text)

# [Rest of the code remains the same]
    
    def update_summary(self):
        """Update final summary page"""
        if not self.selected_products:
            tk.messagebox.showwarning("Warning", "Please select at least one product")
            return
        
        if not self.selected_volume.get() or not self.selected_country.get():
            tk.messagebox.showwarning("Warning", "Please select volume and country")
            return
        
        # Get all details
        product_details = self.data_manager.get_product_details(self.selected_products)
        recurring_details = self.data_manager.get_recurring_price(
            self.selected_volume.get(),
            self.selected_country.get()
        )
        
        # Calculate total
        total_price = self.total_opening_price + self.total_recurring_price
        
        # Format summary
        summary = "FINAL PRICING SUMMARY\n"
        summary += "=" * 50 + "\n\n"
        
        summary += "SELECTED PRODUCTS:\n"
        summary += "-" * 20 + "\n"
        for _, row in product_details.iterrows():
            summary += f"• {row['Products']}\n"
            summary += f"  Deliverables: {row['Deliverables']}\n"
            summary += f"  Opening Price: ${row['Price Opening']:,.2f}\n\n"
        
        summary += "RECURRING PRICING:\n"
        summary += "-" * 20 + "\n"
        summary += f"Volume: {self.selected_volume.get()}\n"
        summary += f"Country: {self.selected_country.get()}\n"
        summary += f"Recurring Price: ${self.total_recurring_price:,.2f}\n\n"
        
        summary += "TOTAL PRICING:\n"
        summary += "-" * 20 + "\n"
        summary += f"Opening Price Total: ${self.total_opening_price:,.2f}\n"
        summary += f"Recurring Price: ${self.total_recurring_price:,.2f}\n"
        summary += f"Total Price: ${total_price:,.2f}\n"
        
        # Update summary text
        self.summary_text.delete('1.0', tk.END)
        self.summary_text.insert('1.0', summary)
        
        # Switch to summary page
        self.notebook.select(2)

def main():
    root = tk.Tk()
    app = PricingCalculator(root)
    root.geometry("800x600")
    root.mainloop()

if __name__ == "__main__":
    main()