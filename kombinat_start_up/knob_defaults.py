import json
from pathlib import Path

import nuke
from kombinat_settings import DEFAULT_FILENAME


class KombinatDefaults:

    exclude_knob_names = ["indicators", "selected", "xpos", "ypos"]

    exclude_knobs = [
        "Channel_Knob",
        "ChannelMask_Knob",
        "Obsolete_Knob",
        "Text_Knob",
        "Tab_Knob",
        "String_Knob",
        "EvalString_Knob",
        "PythonKnob",
        "Multiline_Eval_String_Knob",
        "Font_Knob",
        "File_Knob",
    ]

    def __init__(self) -> None:
        self.stored_defaults = self.read_stored_defaults()

    def _get_defaults_file(self):
        return Path(__file__).parent.resolve() / DEFAULT_FILENAME

    def read_stored_defaults(self):
        defaults_file = self._get_defaults_file()

        # TODO sort by keys

        if defaults_file.is_file():
            with open(defaults_file, "r") as default_file:
                return json.load(default_file)
        else:
            return {}

    def write_stored_defaults(self, values):
        defaults_file = self._get_defaults_file()

        sorted_values = dict(sorted(values.items()))
        if defaults_file.is_file():
            with open(defaults_file, "w") as default_file:
                json.dump(sorted_values, default_file, indent=4)
        else:
            return {}

    def apply_knob_defaults(self):
        for key, value in self.stored_defaults.items():
            nuke.knobDefault(key, value)

    def save_knob_defaults(self):
        # TODO build export from within nuke

        session_defined_defaults = self.collect_default_values_from_within_nuke()
        self.stored_defaults.update(session_defined_defaults)
        self.write_stored_defaults(self.stored_defaults)

    def collect_default_values_from_within_nuke(self):
        defaults = {}

        for node in nuke.selectedNodes():

            node_class = node.Class()

            for knob in node.allKnobs():
                knob_class = knob.Class()
                knob_name = knob.name()

                if (
                    not knob.visible()
                    or knob.Class() in self.exclude_knobs
                    or knob_name in self.exclude_knob_names
                ):
                    continue

                if knob_class == "Enumeration_Knob":
                    current_value = knob.values().index(knob.value())
                else:
                    current_value = knob.value()

                try:
                    default_value = knob.defaultValue()
                except AttributeError as error:
                    # TODO handle error
                    pass

                if current_value == default_value:
                    continue

                defaults[f"{node_class}.{knob_name}"] = current_value

        return dict(sorted(defaults.items()))


kDefaults = KombinatDefaults()

kDefaults.save_knob_defaults()
