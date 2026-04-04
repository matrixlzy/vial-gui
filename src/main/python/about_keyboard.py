from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QPlainTextEdit

from protocol.constants import VIAL_PROTOCOL_DYNAMIC, VIAL_PROTOCOL_KEY_OVERRIDE, VIAL_PROTOCOL_ADVANCED_MACROS, \
    VIAL_PROTOCOL_EXT_MACROS, VIAL_PROTOCOL_QMK_SETTINGS


class AboutKeyboard(QDialog):

    def want_min_vial_fw(self, ver):
        if self.keyboard.sideload:
            return "unsupported - sideloaded keyboard"
        if self.keyboard.vial_protocol < 0:
            return "unsupported - VIA keyboard"
        if self.keyboard.vial_protocol < ver:
            return "unsupported - Vial firmware too old"
        return "unsupported - disabled in firmware"

    def about_tap_dance(self):
        if self.keyboard.tap_dance_count > 0:
            return str(self.keyboard.tap_dance_count)
        return self.want_min_vial_fw(VIAL_PROTOCOL_DYNAMIC)

    def about_combo(self):
        if self.keyboard.combo_count > 0:
            return str(self.keyboard.combo_count)
        return self.want_min_vial_fw(VIAL_PROTOCOL_DYNAMIC)

    def about_key_override(self):
        if self.keyboard.key_override_count > 0:
            return str(self.keyboard.key_override_count)
        return self.want_min_vial_fw(VIAL_PROTOCOL_KEY_OVERRIDE)

    def about_alt_repeat_key(self):
        if self.keyboard.alt_repeat_key_count > 0:
            return str(self.keyboard.alt_repeat_key_count)
        return self.want_min_vial_fw(VIAL_PROTOCOL_KEY_OVERRIDE)

    def about_macro_delays(self):
        if self.keyboard.vial_protocol >= VIAL_PROTOCOL_ADVANCED_MACROS:
            return "yes"
        return self.want_min_vial_fw(VIAL_PROTOCOL_ADVANCED_MACROS)

    def about_macro_ext_keycodes(self):
        if self.keyboard.vial_protocol >= VIAL_PROTOCOL_EXT_MACROS:
            return "yes"
        return self.want_min_vial_fw(VIAL_PROTOCOL_EXT_MACROS)

    def about_qmk_settings(self):
        if self.keyboard.vial_protocol >= VIAL_PROTOCOL_QMK_SETTINGS:
            if len(self.keyboard.supported_settings) == 0:
                return "disabled in firmware"
            return "yes"
        return self.want_min_vial_fw(VIAL_PROTOCOL_QMK_SETTINGS)

    def about_feature(self, feature_name):
        if feature_name in self.keyboard.supported_features:
            return "yes"
        return self.want_min_vial_fw(VIAL_PROTOCOL_DYNAMIC)

    def __init__(self, device):
        super().__init__()

        self.keyboard = device.keyboard
        self.setWindowTitle("关于 {}".format(device.title()))

        text = ""
        desc = device.desc
        text += "制造商: {}\n".format(desc["manufacturer_string"])
        text += "产品: {}\n".format(desc["product_string"])
        text += "厂商VID: {:04X}\n".format(desc["vendor_id"])
        text += "产品PID: {:04X}\n".format(desc["product_id"])
        text += "设备: {}\n".format(desc["path"])
        text += "\n"

        if self.keyboard.sideload:
            text += "使用旁加载的JSON配置，部分功能受限\n\n"
        elif self.keyboard.vial_protocol < 0:
            text += "仅支持VIA协议，不支持Vial高级功能\n\n"

        text += "VIA 协议: {}\n".format(self.keyboard.via_protocol)
        text += "Vial 协议: {}\n".format(self.keyboard.vial_protocol)
        text += "Vial 键盘ID: {:08X}\n".format(self.keyboard.keyboard_id)
        text += "\n"

        text += "宏条目数: {}\n".format(self.keyboard.macro_count)
        text += "宏存储: {} bytes\n".format(self.keyboard.macro_memory)
        text += "宏延迟: {}\n".format(self.about_macro_delays())
        text += "(2-byte) 复杂宏键码: {}\n".format(self.about_macro_ext_keycodes())
        text += "\n"

        text += "多方式触发: {}\n".format(self.about_tap_dance())
        text += "组合键触发: {}\n".format(self.about_combo())
        text += "按键覆盖/替换: {}\n".format(self.about_key_override())
        text += "Alt替代重复键: {}\n".format(self.about_alt_repeat_key())
        text += "智能大写锁定: {}\n".format(self.about_feature("caps_word"))
        text += "层锁: {}\n".format(self.about_feature("layer_lock"))
        text += "\n"

        text += "QMK设置: {}\n".format(self.about_qmk_settings())

        font = QFont("monospace")
        font.setStyleHint(QFont.TypeWriter)
        self.textarea = QPlainTextEdit()
        self.textarea.setReadOnly(True)
        self.textarea.setFont(font)

        self.textarea.setPlainText(text)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.textarea)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
