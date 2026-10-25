"""
Agenda de llamadas para Android (Python + Kivy).

- Añade contactos (nombre + número).
- Toca un contacto para abrir el marcador del teléfono con el número ya puesto.
- Los contactos se guardan en un JSON dentro de la carpeta privada de la app.
"""
import json
import os
import re

from kivy.app import App
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.utils import platform


# ---------------------------------------------------------------------------
# Llamar: en Android lanzamos un Intent ACTION_DIAL a través de pyjnius.
# ACTION_DIAL abre el marcador con el número escrito y NO necesita permisos.
# (ACTION_CALL llamaría directamente, pero exige el permiso CALL_PHONE.)
# ---------------------------------------------------------------------------
def marcar(numero: str) -> None:
    if platform == "android":
        from jnius import autoclass

        Intent = autoclass("android.content.Intent")
        Uri = autoclass("android.net.Uri")
        PythonActivity = autoclass("org.kivy.android.PythonActivity")

        intent = Intent(Intent.ACTION_DIAL)
        intent.setData(Uri.parse("tel:" + numero))
        PythonActivity.mActivity.startActivity(intent)
    else:
        # En el PC solo lo mostramos, para poder probar la interfaz.
        print(f"[escritorio] Se marcaría el {numero}")


def limpiar_numero(texto: str) -> str:
    """Deja solo dígitos y un '+' inicial opcional."""
    texto = texto.strip()
    mas = "+" if texto.startswith("+") else ""
    return mas + re.sub(r"\D", "", texto)


# ---------------------------------------------------------------------------
# Persistencia
# ---------------------------------------------------------------------------
class Almacen:
    def __init__(self, carpeta: str):
        self.ruta = os.path.join(carpeta, "contactos.json")
        self.contactos = self._cargar()

    def _cargar(self):
        try:
            with open(self.ruta, encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def guardar(self):
        with open(self.ruta, "w", encoding="utf-8") as f:
            json.dump(self.contactos, f, ensure_ascii=False, indent=2)

    def anadir(self, nombre, numero):
        self.contactos.append({"nombre": nombre, "numero": numero})
        self.contactos.sort(key=lambda c: c["nombre"].lower())
        self.guardar()

    def borrar(self, contacto):
        self.contactos.remove(contacto)
        self.guardar()


# ---------------------------------------------------------------------------
# Interfaz
# ---------------------------------------------------------------------------
class PantallaLista(BoxLayout):
    def __init__(self, almacen: Almacen, **kwargs):
        super().__init__(orientation="vertical", padding=dp(10), spacing=dp(8), **kwargs)
        self.almacen = almacen

        # --- Formulario para añadir ---
        self.in_nombre = TextInput(hint_text="Nombre", multiline=False,
                                   size_hint_y=None, height=dp(48))
        self.in_numero = TextInput(hint_text="Número de teléfono", multiline=False,
                                   input_type="tel", size_hint_y=None, height=dp(48))
        btn_anadir = Button(text="Añadir", size_hint_y=None, height=dp(48))
        btn_anadir.bind(on_release=self.on_anadir)

        self.aviso = Label(text="", size_hint_y=None, height=dp(24),
                           color=(1, 0.4, 0.4, 1))

        for w in (self.in_nombre, self.in_numero, btn_anadir, self.aviso):
            self.add_widget(w)

        # --- Lista desplazable ---
        self.lista = GridLayout(cols=1, spacing=dp(6), size_hint_y=None)
        self.lista.bind(minimum_height=self.lista.setter("height"))
        scroll = ScrollView()
        scroll.add_widget(self.lista)
        self.add_widget(scroll)

        self.refrescar()

    def on_anadir(self, *_):
        nombre = self.in_nombre.text.strip()
        numero = limpiar_numero(self.in_numero.text)
        if not nombre or len(numero.lstrip("+")) < 3:
            self.aviso.text = "Escribe un nombre y un número válido"
            return
        self.almacen.anadir(nombre, numero)
        self.in_nombre.text = self.in_numero.text = self.aviso.text = ""
        self.refrescar()

    def refrescar(self):
        self.lista.clear_widgets()
        if not self.almacen.contactos:
            self.lista.add_widget(Label(text="Aún no hay números. Añade uno arriba.",
                                        size_hint_y=None, height=dp(60)))
            return
        for c in self.almacen.contactos:
            self.lista.add_widget(self._fila(c))

    def _fila(self, contacto):
        fila = BoxLayout(size_hint_y=None, height=dp(64), spacing=dp(6))

        btn_llamar = Button(text=f"{contacto['nombre']}\n{contacto['numero']}",
                            halign="center")
        btn_llamar.bind(on_release=lambda *_: marcar(contacto["numero"]))

        btn_borrar = Button(text="Borrar", size_hint_x=None, width=dp(80),
                            background_color=(0.8, 0.2, 0.2, 1))
        btn_borrar.bind(on_release=lambda *_: self._confirmar_borrado(contacto))

        fila.add_widget(btn_llamar)
        fila.add_widget(btn_borrar)
        return fila

    def _confirmar_borrado(self, contacto):
        caja = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(10))
        caja.add_widget(Label(text=f"¿Borrar a {contacto['nombre']}?"))
        botones = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(10))
        si, no = Button(text="Sí, borrar"), Button(text="Cancelar")
        botones.add_widget(no)
        botones.add_widget(si)
        caja.add_widget(botones)

        popup = Popup(title="Confirmar", content=caja,
                      size_hint=(0.85, None), height=dp(200))

        def borrar(*_):
            self.almacen.borrar(contacto)
            popup.dismiss()
            self.refrescar()

        si.bind(on_release=borrar)
        no.bind(on_release=popup.dismiss)
        popup.open()


class AgendaApp(App):
    title = "Mis llamadas"

    def build(self):
        # user_data_dir = carpeta privada de la app (en Android, internal storage)
        return PantallaLista(Almacen(self.user_data_dir))


if __name__ == "__main__":
    AgendaApp().run()
