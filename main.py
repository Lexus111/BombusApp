import sqlite3
import datetime
import os
from kivy.config import Config
from kivy.utils import platform

Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '780')

from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFillRoundFlatButton, MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.textfield import MDTextField
from kivymd.toast import toast
from kivy.uix.image import AsyncImage

try:
    from kivy_garden.mapview import MapView, MapMarkerPopup
    MAPS_AVAILABLE = True
except ImportError:
    MAPS_AVAILABLE = False

class DatabaseWorker:
    def __init__(self):
        self.db_path = "bombus_final.db"
        if platform == 'android':
            try:
                from android.storage import primary_external_storage_path
                storage = primary_external_storage_path()
                my_dir = os.path.join(storage, 'BombusPro')
                if not os.path.exists(my_dir):
                    os.makedirs(my_dir)
                self.db_path = os.path.join(my_dir, "bombus_final.db")
            except:
                pass
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS registry (id INTEGER PRIMARY KEY, user_date TEXT, taxon TEXT, caste TEXT, size TEXT, image_path TEXT)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS nests (id INTEGER PRIMARY KEY, species TEXT, image_path TEXT, date_time TEXT)")
        for t in ['infections', 'biotopes', 'hibernation']:
            self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {t} (id INTEGER PRIMARY KEY, lat REAL, lon REAL, descr TEXT)")
        self.conn.commit()

    def add_registry(self, date_text, taxon, caste, size, img):
        self.cursor.execute("INSERT INTO registry (user_date, taxon, caste, size, image_path) VALUES (?, ?, ?, ?, ?)", (date_text, taxon, caste, size, img))
        self.conn.commit()

    def add_nest(self, species, img):
        dt = datetime.datetime.now().strftime("%Y-%m-%d")
        self.cursor.execute("INSERT INTO nests (species, image_path, date_time) VALUES (?, ?, ?)", (species, img, dt))
        self.conn.commit()

    def add_marker(self, table, lat, lon, text):
        self.cursor.execute(f"INSERT INTO {table} (lat, lon, descr) VALUES (?, ?, ?)", (lat, lon, text))
        self.conn.commit()
        return self.cursor.lastrowid

    def delete_marker(self, table, item_id):
        self.cursor.execute(f"DELETE FROM {table} WHERE id=?", (item_id,))
        self.conn.commit()

    def get_all(self, table):
        self.cursor.execute(f"SELECT * FROM {table} ORDER BY id DESC")
        return self.cursor.fetchall()

db = DatabaseWorker()

class CustomMarker(MapMarkerPopup):
    def __init__(self, marker_id, table_type, desc_text, **kwargs):
        super().__init__(**kwargs)
        self.marker_id = marker_id
        self.table_type = table_type
        box = MDBoxLayout(orientation="vertical", size_hint=(None, None), size=("160dp", "90dp"), padding="10dp", spacing="5dp")
        box.md_bg_color = [0.15, 0.15, 0.15, 1]
        lbl = MDLabel(text=desc_text, theme_text_color="Custom", text_color=[1,1,1,1], font_size="13sp", halign="center")
        btn = MDFillRoundFlatButton(text="УДАЛИТЬ", font_size="11sp", pos_hint={'center_x': 0.5})
        btn.md_bg_color = [0.8, 0, 0, 1]
        btn.bind(on_release=self.delete_me)
        box.add_widget(lbl)
        box.add_widget(btn)
        self.add_widget(box)

    def delete_me(self, instance):
        db.delete_marker(self.table_type, self.marker_id)
        if self.parent:
            self.parent.remove_marker(self)
        toast("Метка удалена")

KV = '''
#:import MapView kivy_garden.mapview.MapView
<MapTabItem@MDBottomNavigationItem>:
    map_context: "" 
    MDFloatLayout:
        MapView:
            id: map_view
            lat: 55.75
            lon: 37.61
            zoom: 10
            double_tap_zoom: True
        MDIconButton:
            icon: "crosshairs"
            user_font_size: "30sp"
            pos_hint: {"center_x": 0.5, "center_y": 0.5}
            theme_text_color: "Custom"
            text_color: 1, 0, 0, 1
        MDIconButton:
            icon: "plus-circle"
            user_font_size: "64sp"
            pos_hint: {"right": 0.95, "bottom": 0.15}
            theme_text_color: "Custom"
            text_color: 0, 0.8, 0.5, 1
            md_bg_color: 0.1, 0.1, 0.1, 0.8
            on_release: app.open_add_dialog(root.map_context, map_view)

ScreenManager:
    MDScreen:
        name: "main"
        MDFloatLayout:
            MDBoxLayout:
                orientation: 'vertical'
                md_bg_color: 0.1, 0.1, 0.1, 1
                MDBoxLayout:
                    size_hint_y: None
                    height: dp(50)
                    md_bg_color: 0.05, 0.05, 0.05, 1
                    padding: dp(15)
                    MDLabel:
                        text: "BOMBUS LAB PRO"
                        bold: True
                        halign: "center"
                        theme_text_color: "Custom"
                        text_color: 0, 1, 0.8, 1
                        font_style: "H6"
                MDBottomNavigation:
                    panel_color: 0.15, 0.15, 0.15, 1
                    text_color_active: 0, 0.8, 0.5, 1
                    MDBottomNavigationItem:
                        name: 'tab_reg'
                        text: 'Реестр'
                        icon: 'notebook-edit'
                        on_tab_press: app.update_lists()
                        MDBoxLayout:
                            orientation: 'vertical'
                            padding: dp(10)
                            spacing: dp(10)
                            MDBoxLayout:
                                orientation: 'horizontal'
                                spacing: dp(10)
                                size_hint_y: None
                                height: dp(60)
                                MDTextField:
                                    id: reg_date
                                    hint_text: "Дата"
                                    mode: "rectangle"
                                MDTextField:
                                    id: reg_size
                                    hint_text: "Размер"
                                    mode: "rectangle"
                            MDBoxLayout:
                                orientation: 'horizontal'
                                spacing: dp(10)
                                size_hint_y: None
                                height: dp(60)
                                MDTextField:
                                    id: reg_taxon
                                    hint_text: "Вид"
                                    mode: "rectangle"
                                MDTextField:
                                    id: reg_caste
                                    hint_text: "Каста"
                                    mode: "rectangle"
                            MDBoxLayout:
                                orientation: 'horizontal'
                                size_hint_y: None
                                height: dp(50)
                                spacing: dp(10)
                                MDRoundFlatIconButton:
                                    text: "Фото"
                                    icon: "camera"
                                    size_hint_x: 0.5
                                    on_release: app.open_file_manager("registry")
                                MDFillRoundFlatButton:
                                    text: "СОХРАНИТЬ"
                                    size_hint_x: 0.5
                                    md_bg_color: 0, 0.6, 0.4, 1
                                    on_release: app.save_registry()
                            MDLabel:
                                id: lbl_reg_file
                                text: ""
                                font_size: "10sp"
                                theme_text_color: "Hint"
                                size_hint_y: None
                                height: dp(10)
                            MDScrollView:
                                MDBoxLayout:
                                    id: list_registry
                                    orientation: 'vertical'
                                    adaptive_height: True
                                    spacing: dp(10)
                                    padding: dp(5)
                    MDBottomNavigationItem:
                        name: 'tab_nest'
                        text: 'Гнезда'
                        icon: 'home'
                        on_tab_press: app.update_lists()
                        MDBoxLayout:
                            orientation: 'vertical'
                            padding: dp(10)
                            spacing: dp(10)
                            MDTextField:
                                id: nest_species
                                hint_text: "Вид гнезда"
                                mode: "rectangle"
                            MDRoundFlatIconButton:
                                text: "Фото"
                                icon: "image"
                                on_release: app.open_file_manager("nests")
                            MDLabel:
                                id: lbl_nest_file
                                text: "..."
                                font_size: "10sp"
                                theme_text_color: "Hint"
                            MDFillRoundFlatButton:
                                text: "СОХРАНИТЬ"
                                on_release: app.save_nest()
                            MDScrollView:
                                MDBoxLayout:
                                    id: list_nests
                                    orientation: 'vertical'
                                    adaptive_height: True
                                    spacing: dp(10)
                    MapTabItem:
                        name: 'tab_bio'
                        text: 'Биотопы'
                        icon: 'tree'
                        map_context: 'biotopes'
                        on_tab_press: app.load_markers('biotopes', self.ids.map_view)
                    MapTabItem:
                        name: 'tab_hib'
                        text: 'Зимовка'
                        icon: 'snowflake'
                        map_context: 'hibernation'
                        on_tab_press: app.load_markers('hibernation', self.ids.map_view)
                    MapTabItem:
                        name: 'tab_inf'
                        text: 'Инфекции'
                        icon: 'biohazard'
                        map_context: 'infections'
                        on_tab_press: app.load_markers('infections', self.ids.map_view)
            MDCard:
                id: add_dialog
                orientation: "vertical"
                size_hint: 0.85, None
                height: dp(180)
                pos_hint: {"center_x": 0.5, "center_y": -0.5}
                md_bg_color: 0.2, 0.2, 0.2, 1
                radius: [20]
                elevation: 10
                padding: dp(20)
                spacing: dp(10)
                MDLabel:
                    id: dialog_title
                    text: "Новая точка"
                    halign: "center"
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
                    bold: True
                MDTextField:
                    id: dialog_text
                    hint_text: "Описание"
                MDBoxLayout:
                    spacing: dp(10)
                    adaptive_height: True
                    pos_hint: {"center_x": 0.5}
                    MDFlatButton:
                        text: "ОТМЕНА"
                        theme_text_color: "Custom"
                        text_color: 1, 0, 0, 1
                        on_release: app.close_dialog()
                    MDFillRoundFlatButton:
                        text: "СОХРАНИТЬ"
                        md_bg_color: 0, 0.7, 0.4, 1
                        on_release: app.confirm_add()
'''

class BumblebeeApp(MDApp):
    file_manager = None
    selected_image = None
    file_context = "" 
    current_map_widget = None
    current_table = ""

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Teal"
        start_path = os.path.expanduser("~")
        if platform == 'android':
            from android.storage import primary_external_storage_path
            start_path = primary_external_storage_path()
        self.file_manager = MDFileManager(exit_manager=self.exit_manager, select_path=self.select_path)
        self.start_path = start_path 
        return Builder.load_string(KV)

    def on_start(self):
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE, Permission.ACCESS_FINE_LOCATION, Permission.ACCESS_COARSE_LOCATION])
        self.update_lists()

    def load_markers(self, table, map_widget):
        if not MAPS_AVAILABLE:
            toast("MapView Error")
            return
        to_remove = [child for child in map_widget.children if isinstance(child, MapMarkerPopup)]
        for m in to_remove:
            map_widget.remove_marker(m)
        data = db.get_all(table)
        for row in data:
            m = CustomMarker(row[0], table, row[3], lat=row[1], lon=row[2])
            map_widget.add_marker(m)

    def open_add_dialog(self, table, map_widget):
        self.current_table = table
        self.current_map_widget = map_widget
        titles = {'biotopes': "Состояние биотопа", 'hibernation': "Место зимовки", 'infections': "Инфекция"}
        self.root.ids.dialog_title.text = titles.get(table, "Новая метка")
        self.root.ids.dialog_text.text = ""
        self.root.ids.add_dialog.pos_hint = {"center_x": 0.5, "center_y": 0.5}

    def close_dialog(self):
        self.root.ids.add_dialog.pos_hint = {"center_x": 0.5, "center_y": -0.5}

    def confirm_add(self):
        text = self.root.ids.dialog_text.text
        if not text:
            toast("Введите текст!")
            return
        lat = self.current_map_widget.lat
        lon = self.current_map_widget.lon
        new_id = db.add_marker(self.current_table, lat, lon, text)
        m = CustomMarker(new_id, self.current_table, text, lat=lat, lon=lon)
        self.current_map_widget.add_marker(m)
        self.close_dialog()
        toast("Сохранено!")

    def update_lists(self):
        box = self.root.ids.list_registry
        box.clear_widgets()
        for row in db.get_all('registry'):
            card = MDCard(orientation='horizontal', size_hint_y=None, height="90dp", radius=[15], md_bg_color=[0.1, 0.12, 0.15, 1], elevation=2, padding="10dp")
            text_box = MDBoxLayout(orientation='vertical', spacing="4dp")
            lbl_taxon = MDLabel(text=row[2], bold=True, theme_text_color="Custom", text_color=[0, 1, 0.8, 1], font_style="Subtitle1")
            details = f"Каста: {row[3]} | Размер: {row[4]} мм"
            lbl_details = MDLabel(text=details, theme_text_color="Custom", text_color=[0.9, 0.9, 0.9, 1], font_style="Caption")
            lbl_date = MDLabel(text=f"Дата: {row[1]}", theme_text_color="Hint", font_style="Overline")
            text_box.add_widget(lbl_taxon)
            text_box.add_widget(lbl_details)
            text_box.add_widget(lbl_date)
            card.add_widget(text_box)
            img_path = row[5]
            if img_path and img_path != "no_image":
                img = AsyncImage(source=img_path, keep_ratio=True, size_hint_x=0.3)
                card.add_widget(img)
            else:
                card.add_widget(MDLabel(text="NO IMG", halign="center", theme_text_color="Hint", size_hint_x=0.2, font_size="10sp"))
            box.add_widget(card)

        box2 = self.root.ids.list_nests
        box2.clear_widgets()
        for row in db.get_all('nests'):
            c = MDCard(orientation='vertical', size_hint_y=None, height="140dp", padding="5dp", radius=[15], md_bg_color=[0.2,0.2,0.2,1])
            c.add_widget(MDLabel(text=f"Гнездо: {row[1]}", theme_text_color="Custom", text_color=[1,0.8,0,1], bold=True, size_hint_y=0.2))
            c.add_widget(MDLabel(text=f"Дата: {row[3]}", theme_text_color="Hint", font_style="Caption", size_hint_y=0.1))
            img_path = row[2]
            if img_path and img_path != "no_image":
                c.add_widget(AsyncImage(source=img_path, keep_ratio=True, size_hint_y=0.7))
            else:
                c.add_widget(MDLabel(text="Без фото", halign="center", size_hint_y=0.7))
            box2.add_widget(c)

    def save_registry(self):
        if self.root.ids.reg_taxon.text and self.root.ids.reg_date.text:
            img = self.selected_image if self.selected_image else "no_image"
            db.add_registry(self.root.ids.reg_date.text, self.root.ids.reg_taxon.text, self.root.ids.reg_caste.text, self.root.ids.reg_size.text, img)
            self.root.ids.reg_taxon.text = ""
            self.root.ids.reg_caste.text = ""
            self.root.ids.reg_size.text = ""
            self.selected_image = None
            self.root.ids.lbl_reg_file.text = ""
            self.update_lists()
            toast("Добавлено")
        else:
            toast("Заполните Дату и Вид!")

    def save_nest(self):
        if self.root.ids.nest_species.text:
            img = self.selected_image if self.selected_image else "no_image"
            db.add_nest(self.root.ids.nest_species.text, img)
            self.root.ids.nest_species.text = ""
            self.selected_image = None
            self.root.ids.lbl_nest_file.text = "..."
            self.update_lists()

    def open_file_manager(self, context):
        self.file_context = context
        self.file_manager.show(self.start_path)

    def select_path(self, path):
        self.selected_image = path
        self.file_manager.close()
        name = os.path.basename(path)
        if self.file_context == 'registry': self.root.ids.lbl_reg_file.text = name
        else: self.root.ids.lbl_nest_file.text = name

    def exit_manager(self, *args):
        self.file_manager.close()

if __name__ == '__main__':
    BumblebeeApp().run()
