import kivy
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.spinner import Spinner
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
import pandas as pd
import data_loader

kivy.require('1.11.1')

class StyledLabel(Label):
    def __init__(self, **kwargs):
        super(StyledLabel, self).__init__(**kwargs)
        self.color = get_color_from_hex('#2C3E50')
        self.font_size = '16sp'
        self.bold = True
        self.size_hint_y = None
        self.height = dp(50)  # Increased height for better visibility
        self.halign = 'left'
        self.valign = 'middle'
        self.padding = [dp(10), dp(10)]  # Add padding
        self.bind(size=self.update_text_size)
        
    def update_text_size(self, instance, value):
        self.text_size = (self.width, None)  # Allow text to wrap
        self.height = max(dp(50), self.texture_size[1] + dp(20))  # Adjust height based on content

class StyledButton(Button):
    def __init__(self, **kwargs):
        super(StyledButton, self).__init__(**kwargs)
        self.background_color = get_color_from_hex('#3498DB')
        self.color = get_color_from_hex('#FFFFFF')
        self.size_hint = (None, None)
        self.size = (dp(200), dp(50))
        self.font_size = '16sp'
        self.bold = True

class ProductCheckBox(BoxLayout):
    def __init__(self, product, callback, **kwargs):
        super(ProductCheckBox, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(50)  # Increased height
        self.padding = [dp(10), dp(5)]
        self.spacing = dp(20)  # Increased spacing between checkbox and label
        
        # Custom checkbox with larger size
        self.checkbox = CheckBox(
            size_hint=(None, None),
            size=(dp(30), dp(30)),  # Larger checkbox
            color=get_color_from_hex('#3498DB')  # Blue color for visibility
        )
        self.checkbox.bind(active=callback)
        
        # Background for better visibility
        with self.canvas.before:
            Color(*get_color_from_hex('#F8F9FA'))
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        # Label with better spacing
        self.label = Label(
            text=product,
            color=get_color_from_hex('#2C3E50'),
            font_size='14sp',
            halign='left',
            valign='middle',
            size_hint_x=1,
            padding=[dp(10), dp(5)]
        )
        self.label.bind(size=self.update_label_text_size)
        
        # Add widgets with better spacing
        checkbox_container = BoxLayout(size_hint=(None, None), size=(dp(50), dp(50)))
        checkbox_container.add_widget(self.checkbox)
        self.add_widget(checkbox_container)
        self.add_widget(self.label)

    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def update_label_text_size(self, instance, value):
        instance.text_size = (instance.width, None)


class MainPage(Screen):
    def __init__(self, df_small_animals, **kwargs):
        super(MainPage, self).__init__(**kwargs)
        self.df_small_animals = df_small_animals
        self.selected_products = []
        
        # Main layout with increased padding
        main_layout = BoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(20)
        )
        
        # Title with more space
        title = StyledLabel(
            text='Product Selection',
            font_size='24sp',
            height=dp(70),
            color=get_color_from_hex('#2980B9')
        )
        main_layout.add_widget(title)

        # Content layout with better spacing
        content_layout = BoxLayout(
            orientation='horizontal',
            spacing=dp(30),
            size_hint_y=0.9
        )

        # Left column - Product selection
        left_column = BoxLayout(
            orientation='vertical',
            size_hint_x=0.4,
            spacing=dp(15)
        )
        
        # Products label with more space
        products_label = StyledLabel(
            text='Available Products',
            height=dp(60)
        )
        left_column.add_widget(products_label)

        # Scrollable product list with better spacing
        scroll_layout = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=False,
            bar_width=dp(10)
        )
        self.products_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(2)
        )
        self.products_layout.bind(minimum_height=self.products_layout.setter('height'))

        # Add products with alternating backgrounds
        for i, product in enumerate(df_small_animals['Products'].dropna().unique().tolist()):
            checkbox_layout = ProductCheckBox(product, self.on_checkbox_active)
            if i % 2 == 0:
                checkbox_layout.canvas.before.children[-2].rgba = get_color_from_hex('#F8F9FA')
            else:
                checkbox_layout.canvas.before.children[-2].rgba = get_color_from_hex('#FFFFFF')
            self.products_layout.add_widget(checkbox_layout)

        scroll_layout.add_widget(self.products_layout)
        left_column.add_widget(scroll_layout)

        # Right column with better spacing
        right_column = BoxLayout(
            orientation='vertical',
            size_hint_x=0.6,
            spacing=dp(15)
        )
        
        # Description section
        right_column.add_widget(StyledLabel(text='Product Description'))
        self.description_text = TextInput(
            readonly=True,
            multiline=True,
            size_hint=(1, 0.6),
            background_color=get_color_from_hex('#ECF0F1'),
            foreground_color=get_color_from_hex('#2C3E50'),
            padding=[dp(15), dp(15)],
            font_size='14sp'
        )
        right_column.add_widget(self.description_text)

        # Price section with more space
        right_column.add_widget(StyledLabel(text='Total Price'))
        self.price_text = TextInput(
            readonly=True,
            size_hint=(1, None),
            height=dp(60),
            background_color=get_color_from_hex('#ECF0F1'),
            foreground_color=get_color_from_hex('#27AE60'),
            font_size='18sp',
            padding=[dp(15), dp(15)]
        )
        right_column.add_widget(self.price_text)

        # Buttons with better spacing
        buttons_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(70),
            spacing=dp(20)
        )
        
        update_button = StyledButton(text='Update Details')
        update_button.bind(on_press=self.update_product_details)
        next_button = StyledButton(text='Next Page')
        next_button.bind(on_press=self.go_to_next_page)
        
        buttons_layout.add_widget(update_button)
        buttons_layout.add_widget(next_button)
        right_column.add_widget(buttons_layout)

        # Add columns to content layout
        content_layout.add_widget(left_column)
        content_layout.add_widget(right_column)
        main_layout.add_widget(content_layout)

        self.add_widget(main_layout)

    def on_checkbox_active(self, checkbox, value):
        """Handle checkbox state changes"""
        # Find the product name from the checkbox's parent (ProductCheckBox)
        product = checkbox.parent.parent.label.text
        if value:
            if product not in self.selected_products:
                self.selected_products.append(product)
        else:
            if product in self.selected_products:
                self.selected_products.remove(product)

    def update_product_details(self, instance):
        """Update the description and price based on selected products"""
        descriptions = []
        total_price = 0

        for product in self.selected_products:
            product_data = self.df_small_animals[self.df_small_animals['Products'] == product]
            if not product_data.empty:
                description = product_data['Description'].fillna('').values[0]
                descriptions.append(f"• {product}:\n  {description}")
                price = product_data['Price Opening €'].fillna(0).values[0]
                total_price += price

        if descriptions:
            self.description_text.text = "\n\n".join(descriptions)
        else:
            self.description_text.text = "No products selected"
            
        self.price_text.text = f"Total: {total_price:.2f} €"

    def go_to_next_page(self, instance):
        """Navigate to the next page"""
        self.manager.current = 'next_page'


class NextPage(Screen):
    def __init__(self, df_recur_pricing, **kwargs):
        super(NextPage, self).__init__(**kwargs)
        self.df_recur_pricing = df_recur_pricing

        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        # Title
        title = StyledLabel(
            text='Pricing Details',
            font_size='24sp',
            height=60,
            color=get_color_from_hex('#2980B9')
        )
        main_layout.add_widget(title)

        # Content layout
        content_layout = BoxLayout(orientation='vertical', spacing=15)

        # Selection area
        selection_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=100, spacing=20)
        
        # Volume selection
        volume_layout = BoxLayout(orientation='vertical', size_hint_x=0.5)
        volume_layout.add_widget(StyledLabel(text='Volume'))
        self.volume_spinner = Spinner(
            text='Select Volume',
            values=[str(volume) for volume in df_recur_pricing['Volume'].dropna().unique().tolist()],
            size_hint=(1, None),
            height=50,
            background_color=get_color_from_hex('#3498DB'),
            color=get_color_from_hex('#FFFFFF')
        )
        volume_layout.add_widget(self.volume_spinner)
        
        # Country selection
        country_layout = BoxLayout(orientation='vertical', size_hint_x=0.5)
        country_layout.add_widget(StyledLabel(text='Country'))
        self.country_spinner = Spinner(
            text='Select Country',
            values=[str(country).strip() for country in df_recur_pricing['Country'].dropna().unique().tolist()],
            size_hint=(1, None),
            height=50,
            background_color=get_color_from_hex('#3498DB'),
            color=get_color_from_hex('#FFFFFF')
        )
        country_layout.add_widget(self.country_spinner)

        selection_layout.add_widget(volume_layout)
        selection_layout.add_widget(country_layout)
        content_layout.add_widget(selection_layout)

        # Results area
        results_layout = BoxLayout(orientation='vertical', spacing=10)
        
        # Price display
        results_layout.add_widget(StyledLabel(text='Price'))
        self.price_text = TextInput(
            readonly=True,
            size_hint=(1, None),
            height=50,
            background_color=get_color_from_hex('#ECF0F1'),
            foreground_color=get_color_from_hex('#27AE60'),
            font_size='18sp',
            padding=[10, 10]
        )
        results_layout.add_widget(self.price_text)

        # Threshold fee display
        results_layout.add_widget(StyledLabel(text='Above Threshold Fee'))
        self.threshold_fee_text = TextInput(
            readonly=True,
            size_hint=(1, None),
            height=50,
            background_color=get_color_from_hex('#ECF0F1'),
            foreground_color=get_color_from_hex('#27AE60'),
            font_size='18sp',
            padding=[10, 10]
        )
        results_layout.add_widget(self.threshold_fee_text)

        content_layout.add_widget(results_layout)

        # Buttons
        buttons_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=60, spacing=10)
        update_button = StyledButton(text='Update Details')
        update_button.bind(on_press=self.update_details)
        back_button = StyledButton(text='Back')
        back_button.bind(on_press=self.go_to_main_page)
        
        buttons_layout.add_widget(back_button)
        buttons_layout.add_widget(update_button)
        
        content_layout.add_widget(buttons_layout)
        main_layout.add_widget(content_layout)

        self.add_widget(main_layout)

    def update_details(self, instance):
        selected_volume = self.volume_spinner.text
        selected_country = self.country_spinner.text.strip()

        if selected_volume != "Select Volume" and selected_country != "Select Country":
            try:
                selected_volume = float(selected_volume)
                data = self.df_recur_pricing[
                    (self.df_recur_pricing['Volume'] == selected_volume) &
                    (self.df_recur_pricing['Country'].str.strip() == selected_country)
                ]
                
                if not data.empty:
                    price = data['Price'].values[0]
                    threshold_fee = data['Above \nthreshold \nfee'].values[0]
                    self.price_text.text = f"{price:.2f} €"
                    self.threshold_fee_text.text = f"{threshold_fee:.2f} €"
                else:
                    self.price_text.text = "No data available"
                    self.threshold_fee_text.text = "No data available"
            except ValueError:
                self.price_text.text = "Invalid volume"
                self.threshold_fee_text.text = "Invalid volume"
        else:
            self.price_text.text = "Please select both volume and country"
            self.threshold_fee_text.text = "Please select both volume and country"

    def go_to_main_page(self, instance):
        self.manager.current = 'main_page'

class ProductSelectionApp(App):
    def build(self):
        # Set window size and title
        Window.size = (1024, 768)
        self.title = 'Product Selection System'
        
        # Load data
        self.df_small_animals, self.df_recur_pricing = data_loader.load_excel_data(excel_file_path)

        # Create screen manager
        sm = ScreenManager()
        sm.add_widget(MainPage(name='main_page', df_small_animals=self.df_small_animals))
        sm.add_widget(NextPage(name='next_page', df_recur_pricing=self.df_recur_pricing))

        return sm

if __name__ == "__main__":
    excel_file_path = '/Users/rishabhkankash/Library/CloudStorage/OneDrive-HawkCell/CloudFiles/MFpullLatest11.xlsx'
    ProductSelectionApp().run()