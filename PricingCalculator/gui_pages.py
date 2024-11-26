import kivy
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.spinner import Spinner
import pandas as pd
import data_loader

kivy.require('1.11.1')  # Ensure you have a compatible Kivy version

class MainPage(Screen):
    def __init__(self, df_small_animals, **kwargs):
        super(MainPage, self).__init__(**kwargs)
        self.df_small_animals = df_small_animals
        self.selected_products = []

        layout = GridLayout(cols=1, spacing=10, padding=20)

        # Product selection checkboxes
        self.checkboxes = []
        for product in df_small_animals['Products'].dropna().unique().tolist():
            checkbox = CheckBox()
            checkbox.bind(active=self.on_checkbox_active)
            self.checkboxes.append((checkbox, product))
            layout.add_widget(Label(text=product, size_hint=(None, None), size=(200, 40)))
            layout.add_widget(checkbox)

        # Labels for product details
        self.description_label = Label(text="Description:", size_hint=(None, None), size=(200, 40))
        layout.add_widget(self.description_label)

        self.description_text = TextInput(readonly=True, multiline=True, size_hint=(None, None), size=(400, 100))
        layout.add_widget(self.description_text)

        self.price_label = Label(text="Price Opening (€):", size_hint=(None, None), size=(200, 40))
        layout.add_widget(self.price_label)

        self.price_text = TextInput(readonly=True, multiline=True, size_hint=(None, None), size=(400, 40))
        layout.add_widget(self.price_text)

        # Update button
        update_button = Button(text="Update Details", size_hint=(None, None), size=(200, 40))
        update_button.bind(on_press=self.update_product_details)
        layout.add_widget(update_button)

        # Next page button
        next_page_button = Button(text="Next Page", size_hint=(None, None), size=(200, 40))
        next_page_button.bind(on_press=self.go_to_next_page)
        layout.add_widget(next_page_button)

        self.add_widget(layout)

    def on_checkbox_active(self, checkbox, value):
        product = next(product for cb, product in self.checkboxes if cb == checkbox)
        if value:
            self.selected_products.append(product)
        else:
            self.selected_products.remove(product)

    def update_product_details(self, instance):
        selected_products = self.selected_products
        print(f"Selected products: {selected_products}")

        descriptions = []
        total_price = 0

        for product in selected_products:
            product_data = self.df_small_animals[self.df_small_animals['Products'] == product]
            if not product_data.empty:
                descriptions.append(product_data['Description'].fillna('').values[0])
                price = product_data['Price Opening €'].fillna(0).values[0]
                total_price += price

                # Debug prints to check the content of Price
                print(f"Price for {product}: {price}")

        self.description_text.text = "\n".join(descriptions)
        self.price_text.text = f"Total: {total_price:.2f} €"

    def go_to_next_page(self, instance):
        self.manager.current = 'next_page'

class NextPage(Screen):
    def __init__(self, df_recur_pricing, **kwargs):
        super(NextPage, self).__init__(**kwargs)
        self.df_recur_pricing = df_recur_pricing

        layout = GridLayout(cols=1, spacing=10, padding=20)

        # Volume dropdown
        self.volume_label = Label(text="Volume:", size_hint=(None, None), size=(200, 40))
        layout.add_widget(self.volume_label)

        self.volume_spinner = Spinner(
            text="Select Volume",
            values=[str(volume) for volume in df_recur_pricing['Volume'].dropna().unique().tolist()],
            size_hint=(None, None),
            size=(200, 40)
        )
        layout.add_widget(self.volume_spinner)

        # Country dropdown
        self.country_label = Label(text="Country:", size_hint=(None, None), size=(200, 40))
        layout.add_widget(self.country_label)

        self.country_spinner = Spinner(
            text="Select Country",
            values=[str(country).strip() for country in df_recur_pricing['Country'].dropna().unique().tolist()],
            size_hint=(None, None),
            size=(200, 40)
        )
        layout.add_widget(self.country_spinner)

        # Labels for price and above threshold fee
        self.price_label = Label(text="Price:", size_hint=(None, None), size=(200, 40))
        layout.add_widget(self.price_label)

        self.price_text = TextInput(readonly=True, multiline=True, size_hint=(None, None), size=(400, 40))
        layout.add_widget(self.price_text)

        self.threshold_fee_label = Label(text="Above Threshold Fee:", size_hint=(None, None), size=(200, 40))
        layout.add_widget(self.threshold_fee_label)

        self.threshold_fee_text = TextInput(readonly=True, multiline=True, size_hint=(None, None), size=(400, 40))
        layout.add_widget(self.threshold_fee_text)

        # Update button
        update_button = Button(text="Update Details", size_hint=(None, None), size=(200, 40))
        update_button.bind(on_press=self.update_details)
        layout.add_widget(update_button)

        # Back button
        back_button = Button(text="Back", size_hint=(None, None), size=(200, 40))
        back_button.bind(on_press=self.go_to_main_page)
        layout.add_widget(back_button)

        self.add_widget(layout)

    def update_details(self, instance):
        selected_volume = self.volume_spinner.text
        selected_country = self.country_spinner.text.strip()
        print(f"Selected volume: {selected_volume} (type: {type(selected_volume)})")
        print(f"Selected country: {selected_country} (type: {type(selected_country)})")

        print(f"DataFrame columns: {self.df_recur_pricing.columns}")
        print(f"Sample data:\n{self.df_recur_pricing.head()}")

        if selected_volume != "Select Volume" and selected_country != "Select Country":
            try:
                selected_volume = float(selected_volume)
            except ValueError:
                print("Invalid volume selected")
                self.price_text.text = "N/A"
                self.threshold_fee_text.text = "N/A"
                return

            data = self.df_recur_pricing[
                (self.df_recur_pricing['Volume'] == selected_volume) &
                (self.df_recur_pricing['Country'].str.strip() == selected_country)
            ]
            print(f"Filtered data: {data}")  # Debug print to check the filtered data
            if not data.empty:
                price = data['Price'].values[0]
                threshold_fee = data['Above \nthreshold \nfee'].values[0]

                self.price_text.text = f"{price:.2f} €"
                self.threshold_fee_text.text = f"{threshold_fee:.2f} €"
            else:
                self.price_text.text = "N/A"
                self.threshold_fee_text.text = "N/A"
        else:
            self.price_text.text = "N/A"
            self.threshold_fee_text.text = "N/A"

    def go_to_main_page(self, instance):
        self.manager.current = 'main_page'

class ProductSelectionApp(App):
    def build(self):
        self.df_small_animals, self.df_recur_pricing = data_loader.load_excel_data(excel_file_path)

        sm = ScreenManager()
        sm.add_widget(MainPage(name='main_page', df_small_animals=self.df_small_animals))
        sm.add_widget(NextPage(name='next_page', df_recur_pricing=self.df_recur_pricing))

        return sm

if __name__ == "__main__":
    excel_file_path = '/Users/rishabhkankash/Library/CloudStorage/OneDrive-HawkCell/CloudFiles/MFpullLatest11.xlsx'
    ProductSelectionApp().run()