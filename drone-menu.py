# Drone mod menu for Hamster Hunter on Steam
# Imports

import customtkinter as ctk
import pymem
import pymem.process

try:
    from pynput import keyboard as pynput_kb, mouse as pynput_mouse
    PYNPUT_OK = True
except Exception:
    pynput_kb = pynput_mouse = None
    PYNPUT_OK = False


# Constants

APP_SIZE = "560x560"
FONT = ("Montserrat ExtraBold", 13)


# Memory / Process Setup

pm = pymem.Pymem("Hamster Hunter.exe")

gameassembly_base = pymem.process.module_from_name(
    pm.process_handle, "GameAssembly.dll"
).lpBaseOfDll


# Drone (FPV) Pointer Offsets

FPV_BASE_OFFSET   = 0x041048E0
FPV_CHAIN_OFFSETS = [0xB8, 0x0, 0xD8]

FPV_FIELDS = {
    "thrustSpeed":   0x20,
    "strafeSpeed":   0x24,
    "verticalSpeed": 0x28,
    "acceleration":  0x30,
    "deceleration":  0x34,
    "currentPitch":  0x1DC,
    "currentYaw":    0x1E0,
}


# Memory Helpers

def _read_ptr(addr: int) -> int:
    return pm.read_longlong(addr)

def _resolve_fpv_field_address(field: str) -> int:
    # Walk the FPV pointer chain; raises if the drone isn't active
    addr = _read_ptr(gameassembly_base + FPV_BASE_OFFSET)
    if addr == 0:
        raise RuntimeError("FPV base pointer is null (enter drone mode first)")
    for off in FPV_CHAIN_OFFSETS:
        addr = _read_ptr(addr + off)
        if addr == 0:
            raise RuntimeError("FPV pointer chain resolved to null")
    return addr + FPV_FIELDS[field]

def _read_fpv_safe(field: str, default: float) -> float:
    """Read a drone field; returns default if the pointer chain isn't ready yet."""
    try:
        return pm.read_float(_resolve_fpv_field_address(field))
    except Exception:
        return default


# Value Setters

def _set_fpv_field(field: str, v: float):
    a = _resolve_fpv_field_address(field)
    pm.write_float(a, float(v))
    rb = pm.read_float(a)
    return f"{field} {rb} @ {hex(a)}", "lightgreen"

def set_thrust_speed(v: float):    return _set_fpv_field("thrustSpeed",    v)
def set_strafe_speed(v: float):    return _set_fpv_field("strafeSpeed",    v)
def set_vertical_speed(v: float):  return _set_fpv_field("verticalSpeed",  v)
def set_acceleration(v: float):    return _set_fpv_field("acceleration",   v)
def set_deceleration(v: float):    return _set_fpv_field("deceleration",   v)
def set_current_pitch(v: float):   return _set_fpv_field("currentPitch",   v)
def set_current_yaw(v: float):     return _set_fpv_field("currentYaw",     v)


# GUI Initialization

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Drone Menu")
app.geometry(APP_SIZE)
app.attributes("-topmost", True)

frame = ctk.CTkScrollableFrame(app)
frame.pack(pady=20, padx=20, fill="both", expand=True)


# Status Bar

status = ctk.StringVar(value="Ready")
status_label = ctk.CTkLabel(frame, textvariable=status, font=FONT, text_color="lightgreen")
status_label.pack(anchor="w", pady=(10, 2))


# Always-on-Top Toggle (tilde key)

_topmost      = True
_topmost_hint = ctk.StringVar(value="Press ~ to unlock from top")

ctk.CTkLabel(frame, textvariable=_topmost_hint, font=FONT, text_color="gray").pack(anchor="w", pady=(0, 10))

def _toggle_topmost():
    global _topmost
    _topmost = not _topmost
    app.attributes("-topmost", _topmost)
    _topmost_hint.set("Press ~ to unlock from top" if _topmost else "Press ~ to lock on top")


# Hotkey Helper

_RECORDABLE_MOUSE_BUTTONS = (
    {pynput_mouse.Button.x1, pynput_mouse.Button.x2} if PYNPUT_OK else set()
)

def _key_name(key) -> str:
    if PYNPUT_OK and isinstance(key, pynput_mouse.Button):
        return {
            pynput_mouse.Button.x1: "Mouse X1",
            pynput_mouse.Button.x2: "Mouse X2",
        }.get(key, f"mouse:{key.name}")
    char = getattr(key, "char", None)
    if char:
        return char
    name = getattr(key, "name", None)
    if name:
        return name
    return str(key)


# Binding Section

_active_recorder = None

class BindingSection:

    def __init__(self, parent, label: str, action_func, value_placeholder: str = "value"):
        self.action_func  = action_func
        self.bindings     = []
        self.recorded_key = None
        self.is_recording = False

        ctk.CTkLabel(parent, text=label, font=FONT).pack(anchor="w", pady=(12, 2))

        # Not packed until the first binding is added — avoids an empty gap
        self.bindings_frame = ctk.CTkFrame(parent, fg_color="transparent")

        self._add_row = ctk.CTkFrame(parent, fg_color="transparent")
        self._add_row.pack(fill="x", pady=(4, 0))

        self.record_btn = ctk.CTkButton(
            self._add_row, text="Record", width=80, font=FONT, command=self._toggle_record,
        )
        self.record_btn.pack(side="left", padx=(0, 6))

        self.key_label = ctk.CTkLabel(self._add_row, text="—", width=90, font=FONT, anchor="w")
        self.key_label.pack(side="left", padx=(0, 6))

        self.value_entry = ctk.CTkEntry(self._add_row, placeholder_text=value_placeholder)
        self.value_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))

        self.add_btn = ctk.CTkButton(
            self._add_row, text="Add", width=60, font=FONT,
            state="disabled", command=self._add_binding,
        )
        self.add_btn.pack(side="right")

    # Recording

    def _toggle_record(self):
        if self.is_recording:
            self._stop_recording()
        else:
            self._start_recording()

    def _start_recording(self):
        global _active_recorder
        if not PYNPUT_OK:
            status.set("Hotkeys unavailable: run  pip install pynput")
            status_label.configure(text_color="yellow")
            return
        # Pull focus away from any entry so the recorded key isn't also typed there
        app.focus_set()
        _active_recorder  = self
        self.is_recording = True
        self.recorded_key = None
        self.record_btn.configure(text="Stop")
        self.key_label.configure(text="listening…")
        self.add_btn.configure(state="disabled")
        status.set("Recording — press a key or mouse side button")
        status_label.configure(text_color="yellow")

    def _stop_recording(self):
        global _active_recorder
        if _active_recorder is self:
            _active_recorder = None
        self.is_recording = False
        self.record_btn.configure(text="Record")
        if self.recorded_key is None:
            self.key_label.configure(text="—")
            status.set("Recording cancelled")
            status_label.configure(text_color="yellow")
        else:
            self.key_label.configure(text=_key_name(self.recorded_key))
            status.set(f"Recorded: {_key_name(self.recorded_key)}")
            status_label.configure(text_color="lightgreen")

    def on_key_recorded(self, key):
        global _active_recorder
        _active_recorder  = None
        self.is_recording = False
        self.recorded_key = key
        self.record_btn.configure(text="Record")
        self.key_label.configure(text=_key_name(key))
        self.add_btn.configure(state="normal")
        status.set(f"Recorded: {_key_name(key)}")
        status_label.configure(text_color="lightgreen")

    # Add / Remove

    def _add_binding(self):
        if self.recorded_key is None:
            return
        try:
            value = float(self.value_entry.get() or 0.0)
        except ValueError:
            status.set("Invalid number")
            status_label.configure(text_color="yellow")
            return

        key     = self.recorded_key
        name    = _key_name(key)
        binding = {"key": key, "value": value, "frame": None}

        # Lazy-pack the bindings frame the first time a binding is added
        if not self.bindings:
            self.bindings_frame.pack(fill="x", before=self._add_row)

        row = ctk.CTkFrame(self.bindings_frame, fg_color="transparent")
        row.pack(fill="x", pady=2)
        binding["frame"] = row

        ctk.CTkLabel(row, text=name,       width=90, font=FONT, anchor="w").pack(side="left", padx=(0, 6))
        ctk.CTkLabel(row, text=str(value),           font=FONT, anchor="w").pack(side="left", fill="x", expand=True)
        ctk.CTkButton(
            row, text="Remove", width=70, font=FONT,
            fg_color="#8B0000", hover_color="#5C0000",
            command=lambda b=binding: self._remove_binding(b),
        ).pack(side="right")

        self.bindings.append(binding)

        self.recorded_key = None
        self.key_label.configure(text="—")
        self.value_entry.delete(0, "end")
        self.add_btn.configure(state="disabled")
        status.set(f"Binding added: {name} → {value}")
        status_label.configure(text_color="lightgreen")

    def _remove_binding(self, binding):
        if binding in self.bindings:
            self.bindings.remove(binding)
        binding["frame"].destroy()
        # Hide the bindings frame again when empty to close the gap
        if not self.bindings:
            self.bindings_frame.pack_forget()
        status.set("Binding removed")
        status_label.configure(text_color="yellow")

    # Firing

    def fire_if_match(self, key):
        for b in list(self.bindings):
            if b["key"] == key:
                try:
                    self.action_func(b["value"])
                except Exception:
                    pass


# GUI Row Builder

def _build_float_setter_row(parent, label_text: str, placeholder: str, setter_func, initial_val=None):
    # Header line: label + optional live current-value display
    header = ctk.CTkFrame(parent, fg_color="transparent")
    header.pack(fill="x", pady=(6, 0))
    ctk.CTkLabel(header, text=label_text, font=FONT).pack(side="left")

    if initial_val is not None:
        current_label = ctk.CTkLabel(
            header, text=f"Current: {initial_val:g}", font=FONT, text_color="lightgreen",
        )
        current_label.pack(side="left", padx=(8, 0))
    else:
        current_label = None

    row = ctk.CTkFrame(parent, fg_color="transparent")
    row.pack(fill="x", pady=6)

    entry = ctk.CTkEntry(row, placeholder_text=placeholder)
    entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

    def _on_confirm():
        try:
            value = float(entry.get() or 0.0)
            msg, color = setter_func(value)
            status.set(msg)
            status_label.configure(text_color=color)
            if current_label is not None:
                current_label.configure(text=f"Current: {value:g}")
        except ValueError:
            status.set("Invalid number")
            status_label.configure(text_color="yellow")
        except Exception as e:
            status.set(f"Error: {type(e).__name__}")
            status_label.configure(text_color="red")

    ctk.CTkButton(row, text="Confirm", font=FONT, command=_on_confirm).pack(side="right")


# Layout
# Pitch/Yaw hotkeys first, most commonly used

pitch_section = BindingSection(frame, "Pitch Hotkeys", set_current_pitch, "ex -90 for up, 90 for down, 0 for level")
yaw_section   = BindingSection(frame, "Yaw Hotkeys",   set_current_yaw,   "ex. 0 for north, 90 for east")

_build_float_setter_row(frame, "Thrust Speed",   "Default: 10", set_thrust_speed,   _read_fpv_safe("thrustSpeed",   10))
_build_float_setter_row(frame, "Strafe Speed",   "Default: 8",  set_strafe_speed,   _read_fpv_safe("strafeSpeed",   8))
_build_float_setter_row(frame, "Vertical Speed", "Default: 5",  set_vertical_speed, _read_fpv_safe("verticalSpeed", 5))
_build_float_setter_row(frame, "Acceleration",   "Default: 2",  set_acceleration,   _read_fpv_safe("acceleration",  2))
_build_float_setter_row(frame, "Deceleration",   "Default: 1",  set_deceleration,   _read_fpv_safe("deceleration",  1))

if not PYNPUT_OK:
    status.set("Hotkeys unavailable. Run: pip install pynput")
    status_label.configure(text_color="yellow")


# Global pynput Listeners

def _on_global_key_press(key):
    global _active_recorder

    if getattr(key, "char", None) in ("`", "~"):
        app.after(0, _toggle_topmost)
        return

    if _active_recorder is not None:
        recorder         = _active_recorder
        _active_recorder = None
        app.after(0, lambda: recorder.on_key_recorded(key))
        return

    pitch_section.fire_if_match(key)
    yaw_section.fire_if_match(key)

def _on_global_mouse_click(_x, _y, button, pressed):
    if not pressed:
        return
    global _active_recorder

    if _active_recorder is not None and button in _RECORDABLE_MOUSE_BUTTONS:
        recorder         = _active_recorder
        _active_recorder = None
        app.after(0, lambda: recorder.on_key_recorded(button))
        return

    pitch_section.fire_if_match(button)
    yaw_section.fire_if_match(button)


# Window Close Handler

def _on_close():
    if PYNPUT_OK:
        try: kb_listener.stop()
        except Exception: pass
        try: mouse_listener.stop()
        except Exception: pass
    app.destroy()

app.protocol("WM_DELETE_WINDOW", _on_close)


# Start Listeners & Main Loop

if PYNPUT_OK:
    kb_listener    = pynput_kb.Listener(on_press=_on_global_key_press)
    mouse_listener = pynput_mouse.Listener(on_click=_on_global_mouse_click)
    kb_listener.start()
    mouse_listener.start()

app.mainloop()
