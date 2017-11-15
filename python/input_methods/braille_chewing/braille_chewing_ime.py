#! python3
# Copyright (C) 2017 Hong Jen Yee (PCMan) <pcman.tw@gmail.com>
# Copyright (C) 2017 Logo-Kuo <logo@forblind.org.tw>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

import winsound  # for PlaySound
import os

from keycodes import * # for VK_XXX constants
from textService import *
from ..chewing.chewing_ime import *
from .brl_tables import brl_ascii_dic, brl_buf_state


class BrailleChewingTextService(ChewingTextService):

    # 9 個字元代表點字鍵盤的空白跟 1-8 點在標準鍵盤的位置
    braille_keys = " FDSJKLA;"

    # 注音符號對實體鍵盤英數按鍵
    bopomofo_to_keys = {
        # 標準注音鍵盤
        "ㄅ": "1",
        "ㄆ": "q",
        "ㄇ": "a",
        "ㄈ": "z",
        "ㄉ": "2",
        "ㄊ": "w",
        "ㄋ": "s",
        "ㄌ": "x",
        "ㄍ": "e",
        "ㄎ": "d",
        "ㄏ": "c",
        "ㄐ": "r",
        "ㄑ": "f",
        "ㄒ": "v",
        "ㄓ": "5",
        "ㄔ": "t",
        "ㄕ": "g",
        "ㄖ": "b",
        "ㄗ": "y",
        "ㄘ": "h",
        "ㄙ": "n",
        "ㄧ": "u",
        "ㄨ": "j",
        "ㄩ": "m",
        "ㄚ": "8",
        "ㄛ": "i",
        "ㄜ": "k",
        "ㄝ": ",",
        "ㄞ": "9",
        "ㄟ": "o",
        "ㄠ": "l",
        "ㄡ": ".",
        "ㄢ": "0",
        "ㄣ": "p",
        "ㄤ": ";",
        "ㄥ": "/",
        "ㄦ": "-",
        "˙": "7",
        "ˊ": "6",
        "ˇ": "3",
        "ˋ": "4",
        # 標點、特殊符號鍵盤序列
        "，": "`31",
        "、": "`32",
        "。": "`33",
        "；": "`37",
        "：": "`38",
        "？": "`35",
        "！": "`36",
        "…": "`1",
        "—": "` 49",
        "（": "`41",
        "）": "`42",
        "《": "`4 4",
        "》": "`4 5",
        "〔": "`45",
        "〕": "`46",
        "〈": "`49",
        "〉": "`4 1",
        "「": "`43",
        "」": "`44",
        "『": "`4 2",
        "』": "`4 3",
        "＆": "`3   1",
        "＊": "`3   3",
        "×": "`73",
        "÷": "`74",
        "±": "`79",
        "≠": "`76",
        "∞": "`78",
        "≒": "`77",
        "≦": "`7 6",
        "≧": "`7 7",
        "∩": "`7 8",
        "∪": "`7 9",
        "⊥": "`7  2",
        "∠": "`7  3",
        "∵": "`7   1",
        "∴": "`7   2",
        "≡": "` 43",
        "∥": "` 46",
        "↑": "`81",
        "↓": "`82",
        "←": "`83",
        "→": "`84",
        "△": "`8 8",
        "□": "`8  5",
            # 希臘字母大寫 24 個
        "Α": "`6  7",
        "Β": "`6  8",
        "Γ": "`6  9",
        "Δ": "`6   1",
        "Ε": "`6   2",
        "Ζ": "`6   3",
        "Η": "`6   4",
        "Θ": "`6   5",
        "Ι": "`6   6",
        "Κ": "`6   7",
        "Λ": "`6   8",
        "Μ": "`6   9",
        "Ν": "`6    1",
        "Ξ": "`6    2",
        "Ο": "`6    3",
        "Π": "`6    4",
        "Ρ": "`6    5",
        "Σ": "`6    6",
        "Τ": "`6    7",
        "Υ": "`6    8",
        "Φ": "`6    9",
        "Χ": "`6     1",
        "Ψ": "`6     2",
        "Ω": "`6     3",
            # 希臘字母小寫 24 個
        "α": "`61",
        "β": "`62",
        "γ": "`63",
        "δ": "`64",
        "ε": "`65",
        "ζ": "`66",
        "η": "`67",
        "θ": "`68",
        "ι": "`69",
        "κ": "`6 1",
        "λ": "`6 2",
        "μ": "`6 3",
        "ν": "`6 4",
        "ξ": "`6 5",
        "ο": "`6 6",
        "π": "`6 7",
        "ρ": "`6 8",
        "σ": "`6 9",
        "τ": "`6  1",
        "υ": "`6  2",
        "φ": "`6  3",
        "χ": "`6  4",
        "ψ": "`6  5",
        "ω": "`6  6",
    }
    current_dir = os.path.dirname(__file__)
    sounds_dir = os.path.join(current_dir, "sounds")

    # 內部狀態的表達方式
    state_representations = (
        "BPMF_AP", # 盡量用注音表示內部狀態，除非接下來只可能打出符號
        "BRL_UNC", # 組字區完全使用點字 (Braille Unicode) 表示未完成的字符
        "NOTHING", # 不顯示內部狀態，組字區只在組完一個字符時改變內容
    )

    def __init__(self, client):
        super().__init__(client)
        self.dots_cumulative_state = 0
        self.dots_pressed_state = 0
        self.keys_handled = set()
        self.keys_notified = set()
        self.bpmf_cumulative_str = ""
        self.state = brl_buf_state()
        self.state_representation = 0
        self.output_brl_unc = False

    def applyConfig(self):
        # 攔截 ChewingTextService 的 applyConfig，以便強制關閉某些設定選項
        super().applyConfig()

        # 強制使用預設 keyboard layout
        self.chewingContext.set_KBType(0);

        # 強制按下空白鍵時不當做選字指令
        self.chewingContext.set_spaceAsSelection(0)

        # TODO: 強制關閉新酷音某些和點字輸入相衝的功能

    # 使用者離開輸入法
    def onDeactivate(self):
        super().onDeactivate()
        # 丟棄輸入法狀態
        self.keys_handled.clear()
        self.keys_notified.clear()
        self.reset_braille_mode()

    # 當中文編輯結束時會被呼叫。若中文編輯不是正常結束，而是因為使用者
    # 切換到其他應用程式或其他原因，導致我們的輸入法被強制關閉，此時
    # forced 參數會是 True，在這種狀況下，要清除一些 buffer
    def onCompositionTerminated(self, forced):
        super().onCompositionTerminated(forced)
        if forced:
            # 中文組字到一半被系統強制關閉，清除編輯區內容
            self.keys_handled.clear()
            self.keys_notified.clear()
            self.reset_braille_mode()

    def reset_braille_mode(self, clear_pending=True):
        # 清除點字按鍵的追蹤狀態，準備打下一個字
        self.dots_cumulative_state = 0
        self.dots_pressed_state = 0
        if clear_pending:
            self.bpmf_cumulative_str = ""
            self.state.reset()

    def has_modifiers(self, keyEvent):
        # 檢查是否 Ctrl, Shift, Alt 的任一個有被按下
        return keyEvent.isKeyDown(VK_SHIFT) or keyEvent.isKeyDown(VK_CONTROL) or keyEvent.isKeyDown(VK_MENU)

    def needs_braille_handling(self, keyEvent):
        # 檢查是否需要處理點字
        # 若修飾鍵 (Ctrl, Shift, Alt) 都沒有被按下，且按鍵是「可打印」（空白、英數、標點符號等），當成點字鍵處理
        has_modifiers = self.has_modifiers(keyEvent)
        if not has_modifiers and keyEvent.isPrintableChar():
            return True
        # 其他按鍵會打斷正在記錄的點字輸入
        if has_modifiers:
            # 若按壓修飾鍵，會清除所有內部點字狀態
            self.reset_braille_mode()
        else:
            # 其他的不可打印按鍵僅重設八點的輸入狀態，不影響點字組字的部份
            self.reset_braille_mode(False)
        # 未按下修飾鍵，且點字正在組字，仍然當點字鍵處理
        # 許多不可打印按鍵如 Delete 及方向鍵，會於處理點字時忽略，不讓它有異常行為
        # 但是，修飾鍵本身應排除，而讓新酷音處理
        return not has_modifiers and self.state.brl_check() and keyEvent.keyCode not in (VK_SHIFT, VK_CONTROL, VK_MENU)

    def filterKeyDown(self, keyEvent):
        self.hideMessage() # 收到任何鍵入都隱藏之前顯示的任何提示訊息
        if self.needs_braille_handling(keyEvent):
            return True
        self.keys_notified.add(keyEvent.keyCode)
        return super().filterKeyDown(keyEvent)

    def onKeyDown(self, keyEvent):
        # 記下「之前是否處理過」的狀態，確保 keys_handled 記錄的是至少處理過一次的 keys
        previously_handled = keyEvent.keyCode in self.keys_handled
        self.keys_handled.add(keyEvent.keyCode)
        if keyEvent.charCode in range(ord('0'), ord('9') + 1) and self.get_chewing_cand_totalPage() > 0: # selection keys
            pass
        elif keyEvent.keyCode == VK_BACK:
            # 將倒退鍵經過內部狀態處理，取得鍵入序列轉送新酷音
            if self.handle_braille_keys(keyEvent):
                return True
        elif keyEvent.keyCode == VK_ESCAPE:
            # 點字打到一半，清除內部狀態
            if self.state.brl_check():
                self.state.reset()
                self.bpmf_cumulative_str = ""
                self.update_composition_display()
                return True
        elif self.needs_braille_handling(keyEvent):
            # 點字模式，檢查到是點字鍵被按下就記錄起來，忽略其餘按鍵
            if keyEvent.isPrintableChar():
                i = self.braille_keys.find(chr(keyEvent.charCode).upper())
                if i >= 0:
                    self.dots_cumulative_state |= 1 << i
                    self.dots_pressed_state |= 1 << i
            return True
        # 之前沒有處理過，這次也不打算處理
        if not previously_handled:
            self.keys_handled.remove(keyEvent.keyCode)
        return super().onKeyDown(keyEvent)

    def filterKeyUp(self, keyEvent):
        # 記下上層類別的決定是否處理該 key, 讓 onKeyUp 收到並轉送自己不處理而上層要的 keys
        want_to_handle = False
        # 這個按鍵曾經進入上層類別的 filterKeyDown, 上層類別可能會預期它的 filterKeyUp 訊息
        if keyEvent.keyCode in self.keys_notified:
            self.keys_notified.remove(keyEvent.keyCode)
            want_to_handle = super().filterKeyUp(keyEvent)
        return want_to_handle or (keyEvent.keyCode in self.keys_handled)

    def onKeyUp(self, keyEvent):
        if keyEvent.keyCode in self.keys_handled:
            # 發現點字鍵被釋放，更新追蹤狀態
            if keyEvent.isPrintableChar():
                i = self.braille_keys.find(chr(keyEvent.charCode).upper())
                if i >= 0:
                    self.dots_pressed_state &= ~(1 << i)
            # 點字鍵已全數釋放，讀取目前記錄的點字輸入並處理
            # 如果在點字組字期間按下 Delete 或方向鍵等也會執行到此
            if not self.dots_pressed_state and keyEvent.keyCode != VK_BACK:
                self.handle_braille_keys(keyEvent)
            self.keys_handled.remove(keyEvent.keyCode)
            return True
        return super().onKeyUp(keyEvent)

    # 模擬實體鍵盤的英數按鍵送到新酷音
    def send_keys_to_chewing(self, keys, keyEvent):
        if not self.chewingContext:
            print("send_keys_to_chewing:", "chewingContext not initialized")
            return
        # 輸入標點符號，不使用模擬按鍵的方法，因為涉及較多 GUI 反應
        if 0 and keys.startswith("`") and len(keys) > 1:
            # 直接將按鍵送給 libchewing, 此時與 GUI 顯示非同步
            for key in keys:
                self.chewingContext.handle_Default(ord(key))
            compStr = ""
            if self.chewingContext.buffer_Check():
                compStr = self.chewingContext.buffer_String().decode("UTF-8")
            # 根據 libchewing 緩衝區的狀態，更新組字區內容與游標位置
            self.setCompositionString(compStr)
            self.setCompositionCursor(self.chewingContext.cursor_Current())
            return
        # 其餘的按鍵，使用模擬的方式，會跟 GUI 顯示同步
        keyCode_backup = keyEvent.keyCode
        for key in keys:
            keyEvent.keyCode = ord(key.upper())  # 英文數字的 virtual keyCode 正好 = 大寫 ASCII code
            keyEvent.charCode = ord(key)  # charCode 為字元內碼
            # 讓新酷音引擎處理按鍵，模擬按下再放開
            super().filterKeyDown(keyEvent)
            self.fake_onKeyDown(keyEvent, not(keys.startswith("`") and len(keys) > 1))
            super().filterKeyUp(keyEvent)
            super().onKeyUp(keyEvent)
        keyEvent.keyCode = keyCode_backup

    def get_chewing_cand_totalPage(self):
        # access the chewingContext created by ChewingTextService
        return self.chewingContext.cand_TotalPage() if self.chewingContext else 0

    # 將點字 8 點轉換成注音按鍵，送給新酷音處理
    def handle_braille_keys(self, keyEvent):
        current_braille = None
        if keyEvent.keyCode == VK_BACK:
            current_braille = "\b"
        elif self.dots_cumulative_state:
            # 將點字鍵盤狀態轉成用數字表示，例如位元 0-8 為 (8) 010111100 (0) 就轉成 "23457"
            current_braille = "".join([str(i) for i in range(len(self.braille_keys)) if self.dots_cumulative_state & (1 << i)])
        bopomofo_seq = None
        # 點字鍵入轉換成 ASCII 字元、熱鍵或者注音
        if current_braille is None:
            # current_braille 是 None 表示（點字組字過程中）按了無效的鍵
            pass
        elif current_braille == "\b":
            key = self.state.append_brl("\b")
            if key:
                bopomofo_seq = "\b" * key["VK_BACK"] + key["bopomofo"]
            else:
                return False
        elif current_braille == "0245":
            # 熱鍵 245+space 能夠在點字狀態失去控制時將它重設，不遺失已經存在組字區的中文
            # 正在輸入注音，就把注音去掉
            self.bpmf_cumulative_str = ""
            self.state.reset()
            bopomofo_seq = ""
        elif current_braille == "0456":
            # 熱鍵 456+space 與 Shift 一樣能切換中打、英打模式
            self.force_commit()
            self.toggleLanguageMode()
            bopomofo_seq = ""
        elif current_braille == "01":
            # 熱鍵 1+space 用來產生肉眼可讀的輸入狀態提示訊息
            message = self.state.hint_msg()
            if message:
                self.showMessage(message, 8)
            bopomofo_seq = ""
        elif current_braille == "0145":
            # 熱鍵 145+space 用來切換未組成字的狀態顯示方式
            self.state_representation = (self.state_representation + 1) % len(self.state_representations)
            bopomofo_seq = ""
        elif current_braille == "0136":
            # 熱鍵 136+space 用來切換英數模式時點字酷音該輸出英數字元或 Braille Unicode
            # 如果英數模式下使用此熱鍵，必須清除留在組字區的內容
            if self.langMode == ENGLISH_MODE and self.isComposing():
                self.force_commit()
            self.output_brl_unc = not self.output_brl_unc
            bopomofo_seq = ""
        elif current_braille == "024567":
            # 熱鍵 24567+space 用來打開新酷音官方網站
            super().onCommand(ID_WEBSITE, COMMAND_LEFT_CLICK)
            bopomofo_seq = ""
        elif current_braille == "012457":
            # 熱鍵 12457+space 用來打開新酷音線上討論區
            super().onCommand(ID_GROUP, COMMAND_LEFT_CLICK)
            bopomofo_seq = ""
        elif current_braille == "0127":
            # 熱鍵 127+space 用來打開「軟體本身的建議及錯誤回報」
            super().onCommand(ID_BUGREPORT, COMMAND_LEFT_CLICK)
            bopomofo_seq = ""
        elif current_braille == "012347":
            # 熱鍵 12347+space 用來打開「注音及選字選詞錯誤回報」
            super().onCommand(ID_DICT_BUGREPORT, COMMAND_LEFT_CLICK)
            bopomofo_seq = ""
        elif current_braille == "0157":
            # 熱鍵 157+space 用來打開「編輯使用者詞庫」
            super().onCommand(ID_USER_PHRASE_EDITOR, COMMAND_LEFT_CLICK)
            bopomofo_seq = ""
        elif current_braille == "02347":
            # 熱鍵 2347+space 用來點擊「輸出簡體中文」
            super().onCommand(ID_OUTPUT_SIMP_CHINESE, COMMAND_LEFT_CLICK)
            bopomofo_seq = ""
        elif current_braille.startswith("0") and len(current_braille) > 1:
            # 未定義的熱鍵，直接離開這個 if-else, 因為 bopomofo_seq 是 None 而發出警告聲（空白 "0" 不屬此類）
            pass
        elif self.langMode == ENGLISH_MODE:
            if self.output_brl_unc:
                bopomofo_seq = chr(0x2800 | (self.dots_cumulative_state >> 1))
            else:
                bopomofo_seq = brl_ascii_dic.get(current_braille)
                if bopomofo_seq and keyEvent.isKeyToggled(VK_CAPITAL):  # capslock
                    bopomofo_seq = bopomofo_seq.upper()  # convert to upper case
        else:
            # 如果正在選字，允許使用點字數字
            if self.get_chewing_cand_totalPage():
                bopomofo_seq = brl_ascii_dic.get(current_braille, "")
                if bopomofo_seq and bopomofo_seq not in "0123456789":
                    bopomofo_seq = None
            # 否則，將點字送給內部進行組字
            else:
                key = self.state.append_brl(current_braille)
                if key:
                    bopomofo_seq = "\b" * key["VK_BACK"] + key["bopomofo"]

        if current_braille is None:
            print("Invalid input during braille composition. keyCode:", keyEvent.keyCode)
        else:
            print(current_braille.replace("\b", r"\b"), "=>", bopomofo_seq.replace("\b", r"\b") if bopomofo_seq else bopomofo_seq)
        # bopomofo_seq 維持 None 表示輸入被拒，發出警告聲
        if bopomofo_seq is None:
            winsound.MessageBeep()
        # bopomofo_seq 是一個非空字串，才轉送輸入給新酷音
        elif bopomofo_seq:
            # 輸入 Braille Unicode 模式，直接丟出點字字元
            if self.output_brl_unc and self.langMode == ENGLISH_MODE:
                self.setCommitString(bopomofo_seq)
            else:
                bopomofo_seq = "".join(self.bopomofo_to_keys.get(c, c) for c in bopomofo_seq)
                # 將這次按下點字該送給新酷音的按鍵先暫存在 bpmf_cumulative_str
                for c in bopomofo_seq:
                    if c == "\b":
                        self.bpmf_cumulative_str = self.bpmf_cumulative_str[:-1]
                    else:
                        self.bpmf_cumulative_str += c
                # 遇到輸入符號，直接丟棄之前要打注音的鍵入序列
                if bopomofo_seq.startswith("`"):
                    self.bpmf_cumulative_str = bopomofo_seq
                # 內部點字累積狀態被重設，表示鍵入序列必須轉送給新酷音了
                if not self.state.brl_check():
                    # 把注音送給新酷音
                    self.send_keys_to_chewing(self.bpmf_cumulative_str, keyEvent)
                    self.bpmf_cumulative_str = ""

        self.update_composition_display()

        # 清除點字 buffer，準備打下一個字
        self.reset_braille_mode(False)
        return True # braille input processed

    # 切換中英文模式
    def toggleLanguageMode(self):
        # 當英數模式輸出 Braille Unicode 時，組字區非空會禁止切換模式
        if self.output_brl_unc and self.isComposing():
            print("Language toggling request is rejected.")
            winsound.MessageBeep()
            return
        super().toggleLanguageMode()
        if self.chewingContext:
            # 播放語音檔，說明目前是中文/英文
            mode = self.chewingContext.get_ChiEngMode()
            snd_file = os.path.join(self.sounds_dir, "chi.wav" if mode == CHINESE_MODE else "eng.wav")
            winsound.PlaySound(snd_file, winsound.SND_FILENAME|winsound.SND_ASYNC|winsound.SND_NODEFAULT)
            if mode == ENGLISH_MODE:
                self.bpmf_cumulative_str = ""
                self.state.reset()

    # 切換全形/半形
    def toggleShapeMode(self):
        super().toggleShapeMode()
        if self.chewingContext:
            # 播放語音檔，說明目前是全形/半形
            mode = self.chewingContext.get_ShapeMode()
            snd_file = os.path.join(self.sounds_dir, "full.wav" if mode == FULLSHAPE_MODE else "half.wav")
            winsound.PlaySound(snd_file, winsound.SND_FILENAME|winsound.SND_ASYNC|winsound.SND_NODEFAULT)

    # 強迫新酷音丟棄所有注音、選字狀態，直接 commit
    def force_commit(self):
        if not self.chewingContext:
            return
        if self.showCandidates:
            self.setShowCandidates(False)
            self.chewingContext.cand_close()
        if self.chewingContext.buffer_Check():
            self.chewingContext.commit_preedit_buf()
            self.setCompositionCursor(0)
            self.setCompositionString("")
            if self.chewingContext.commit_Check():
                self.setCommitString(self.chewingContext.commit_String().decode("UTF-8"))

    # 更新組字區顯示正在組字的狀態
    def update_composition_display(self):
        if self.chewingContext:
            compStr = ""
            if self.chewingContext.buffer_Check():
                compStr = self.chewingContext.buffer_String().decode("UTF-8")
            pos = self.chewingContext.cursor_Current()
            display_method = self.state_representations[self.state_representation]
            brl_buf_str = "" if display_method == "NOTHING" else self.state.display_str(display_method == "BRL_UNC")
            compStr = compStr[:pos] + brl_buf_str + compStr[pos:]
            self.setCompositionCursor(self.chewingContext.cursor_Current() + len(brl_buf_str))
            self.setCompositionString(compStr)

    def fake_onKeyDown(self, keyEvent, disp=True):
        chewingContext = self.chewingContext
        cfg = chewingConfig
        charCode = keyEvent.charCode
        keyCode = keyEvent.keyCode
        charStr = chr(charCode)

        # 某些狀況下，需要暫時強制切成英文模式，之後再恢復
        temporaryEnglishMode = False
        oldLangMode = chewingContext.get_ChiEngMode()
        ignoreKey = False  # 新酷音是否須忽略這個按鍵
        keyHandled = False # 輸入法是否有處理這個按鍵

        # 使用 Ctrl 或 Shift 鍵做快速符號輸入 (easy symbol input)
        # 這裡的 easy symbol input，是定義在 swkb.dat 設定檔中的符號
        if cfg.easySymbolsWithShift and keyEvent.isKeyDown(VK_SHIFT):
            chewingContext.set_easySymbolInput(1)
        elif cfg.easySymbolsWithCtrl and keyEvent.isKeyDown(VK_CONTROL):
            chewingContext.set_easySymbolInput(1)
        else:
            chewingContext.set_easySymbolInput(0)

        # 若目前輸入的按鍵是可見字元 (字母、數字、標點...等)
        if keyEvent.isPrintableChar():
            keyHandled = True
            invertCase = False  # 是否需要反轉大小寫

            # 中文模式下須特別處理 CapsLock 和 Shift 鍵
            if self.langMode == CHINESE_MODE:
                # 若開啟 Caps lock，需要暫時強制切換成英文模式
                if cfg.enableCapsLock and keyEvent.isKeyToggled(VK_CAPITAL):
                    temporaryEnglishMode = True
                    invertCase = True  # 大寫字母轉成小寫

                # 如果啟動半形符號模式，且輸入符號，則暫時切換為英文模式
                if not cfg.fullShapeSymbols and keyEvent.isSymbols():
                    temporaryEnglishMode = True

                # 若按下 Shift 鍵
                if keyEvent.isKeyDown(VK_SHIFT):
                    if charStr.isalpha():  # 如果是英文字母
                        # 如果不使用快速輸入符號功能，則暫時切成英文模式
                        if not cfg.easySymbolsWithShift:
                            temporaryEnglishMode = True  # 暫時切換成英文模式
                            if not cfg.upperCaseWithShift:  # 如果沒有開啟 Shift 輸入大寫英文
                                invertCase = True # 大寫字母轉成小寫
                    else: # 如果不是英文字母
                        # 如果不使用 Shift 輸入全形標點，則暫時切成英文模式
                        if not cfg.fullShapeSymbolsWithShift:
                            temporaryEnglishMode = True

            if self.langMode == ENGLISH_MODE: # 英文模式
                chewingContext.handle_Default(charCode)
            elif temporaryEnglishMode: # 原為中文模式，暫時強制切成英文
                chewingContext.set_ChiEngMode(ENGLISH_MODE)
                if invertCase: # 先反轉大小寫，再送給新酷音引擎
                    charCode = ord(charStr.lower() if charStr.isupper() else charStr.upper())
                chewingContext.handle_Default(charCode)
            else : # 中文模式
                if charStr.isalpha(): # 英文字母 A-Z
                    # 如果開啟 Ctrl 或 Shift + A-Z 快速輸入符號 (easy symbols，定義在 swkb.dat)
                    # 則只接受大寫英文字母
                    if chewingContext.get_easySymbolInput():
                        charCode = ord(charStr.upper())
                    else:
                        charCode = ord(charStr.lower())
                    chewingContext.handle_Default(charCode)
                elif keyEvent.keyCode == VK_SPACE: # 空白鍵
                    # NOTE: libchewing 有 bug: 當啟用 "使用空白鍵選字" 時，chewing_handle_Space()
                    # 會忽略空白鍵，造成打不出空白。因此在此只有當 composition string 有內容
                    # 有需要選字時，才呼叫 handle_Space()，否則改用 handle_Default()，以免空白鍵被吃掉
                    if self.isComposing():
                        chewingContext.handle_Space()
                    else:
                        chewingContext.handle_Default(charCode)
                elif keyEvent.isKeyDown(VK_CONTROL) and charStr.isdigit(): # Ctrl + 數字(0-9)
                    chewingContext.handle_CtrlNum(charCode)
                elif keyEvent.isKeyToggled(VK_NUMLOCK) and keyCode >= VK_NUMPAD0 and keyCode <= VK_DIVIDE:
                    # numlock 開啟，處理 NumPad 按鍵
                    chewingContext.handle_Numlock(charCode)
                else : # 其他按鍵不需要特殊處理
                    chewingContext.handle_Default(charCode)
        else:  # 不可見字元 (方向鍵, Enter, Page Down...等等)
            # 如果有啟用在選字視窗內移動游標選字，而且目前正在選字
            if self.showCandidates:
                candCursor = self.candidateCursor  # 目前的游標位置
                candCount = len(self.candidateList)  # 目前選字清單項目數
                if keyCode == VK_HOME:  # 處理Home、End鍵，移到選字視窗的第一和最後一個字
                    candCursor = 0
                    ignoreKey = keyHandled = True
                elif keyCode == VK_END:
                    candCursor = candCount - 1
                    ignoreKey = keyHandled = True

                if cfg.leftRightAction == 0:    # 使用左右鍵游標選字
                    if keyCode == VK_LEFT:  # 游標左移
                        if candCursor > 0:
                            candCursor -= 1
                            ignoreKey = keyHandled = True
                    elif keyCode == VK_RIGHT:  # 游標右移
                        if (candCursor + 1) < candCount:
                            candCursor += 1
                            ignoreKey = keyHandled = True

                if cfg.upDownAction == 0:   # 使用上下鍵游標選字
                    if keyCode == VK_UP:  # 游標上移
                        if candCursor >= cfg.candPerRow:
                            candCursor -= cfg.candPerRow
                            ignoreKey = keyHandled = True
                    elif keyCode == VK_DOWN:  # 游標下移
                        if (candCursor + cfg.candPerRow) < candCount:
                            candCursor += cfg.candPerRow
                            ignoreKey = keyHandled = True

                if cfg.upDownAction == 1:   # 使用上下鍵翻頁，左右鍵新酷音預設為翻頁動作
                    if keyCode == VK_UP:    # 向上翻頁
                        chewingContext.handle_PageUp()
                        keyHandled = True
                    elif keyCode == VK_DOWN:  # 如果還有字詞可以選擇，向下翻頁
                        if chewingContext.cand_hasNext():
                            chewingContext.handle_PageDown()
                            keyHandled = True

                if keyCode == VK_RETURN:  # 按下 Enter 鍵
                    # 找出目前游標位置的選字鍵 (1234..., asdf...等等)
                    selKey = cfg.getSelKeys()[self.candidateCursor]
                    # 代替使用者送出選字鍵給新酷音引擎，進行選字
                    chewingContext.handle_Default(ord(selKey))
                    keyHandled = True
                # 更新選字視窗游標位置
                if disp:
                    self.setCandidateCursor(candCursor)

            if not keyHandled:  # 按鍵還沒被處理過
                # the candidate window does not need the key. pass it to libchewing.
                keyName = keyNames.get(keyCode)  #  取得按鍵的名稱
                if keyName: # call libchewing method for the key
                    # 依照按鍵名稱，找 libchewing 對應的 handle_按鍵() method 呼叫
                    methodName = "handle_" + keyName
                    method = getattr(chewingContext, methodName)
                    method()
                    keyHandled = True
                else: # 我們不需要處理的按鍵，直接忽略
                    ignoreKey = True

        # 新酷音引擎忽略不處理此按鍵
        if keyHandled and chewingContext.keystroke_CheckIgnore():
            ignoreKey = True

        if not ignoreKey:  # 如果這個按鍵是有意義的，新酷音有做處理 (不可忽略)
            # 處理選字清單
            if chewingContext.cand_TotalChoice() > 0: # 若有候選字/詞
                candidates = []
                # 要求新酷音引擎列出每個候選字
                chewingContext.cand_Enumerate()
                for i in range(chewingContext.cand_ChoicePerPage()):
                    if not chewingContext.cand_hasNext():
                        break
                    # 新酷音返回的是 UTF-8 byte string，須轉成 python 字串
                    cand = chewingContext.cand_String().decode("UTF-8")
                    candidates.append(cand)

                # 檢查選字清單是否改變 (沒效率但是簡單)
                if candidates != self.candidateList:
                    if disp:
                        self.setCandidateList(candidates)  # 更新候選字清單
                        self.setShowCandidates(True)
                        if cfg.leftRightAction == 0 or cfg.upDownAction == 0:  # 如果啟用選字清單內使用游標選字
                            self.setCandidateCursor(0)  # 重設游標位置

                if not self.showCandidates:  # 如果目前沒有顯示選字視窗
                    if disp:
                        self.setShowCandidates(True)  # 顯示選字視窗
            else:  # 沒有候選字
                if self.showCandidates:
                    if disp:
                        self.setShowCandidates(False)  # 隱藏選字視窗
                        self.setCandidateList([])  # 更新候選字清單

            # 有輸入完成的中文字串要送出(commit)到應用程式
            if chewingContext.commit_Check():
                commitStr = chewingContext.commit_String().decode("UTF-8")

                # 如果使用打繁出簡，就轉成簡體中文
                if self.outputSimpChinese:
                    commitStr = self.opencc.convert(commitStr)

                self.setCommitString(commitStr)  # 設定要輸出的 commit string

            # 編輯區正在輸入中，尚未送出的中文字串 (composition string)
            compStr = ""
            if chewingContext.buffer_Check():
                compStr = chewingContext.buffer_String().decode("UTF-8")

            # 輸入到一半，還沒組成字的注音符號 (bopomofo)
            if disp:
                if chewingContext.bopomofo_Check():
                    bopomofoStr = ""
                    bopomofoStr = chewingContext.bopomofo_String(None).decode("UTF-8")
                    # 把輸入到一半，還沒組成字的注音字串，也插入到編輯區內，並且更新游標位置
                    pos = chewingContext.cursor_Current()
                    compStr = compStr[:pos] + bopomofoStr + compStr[pos:]
                    self.setCompositionCursor(chewingContext.cursor_Current() + len(bopomofoStr))
                else:
                    self.setCompositionCursor(chewingContext.cursor_Current())

                # 更新編輯區內容 (composition string)
                self.setCompositionString(compStr)

            # 顯示額外提示訊息 (例如：Ctrl+數字加入自訂詞之後，會顯示提示)
            if chewingContext.aux_Check():
                message = chewingContext.aux_String().decode("UTF-8")
                # FIXME: sometimes libchewing shows the same aux info
                # for subsequent key events... I think this is a bug.
                self.showMessage(message, 2)

        # 若先前有暫時強制切成英文模式，需要復原
        if temporaryEnglishMode:
            chewingContext.set_ChiEngMode(oldLangMode)

        # 依照目前狀態，更新語言列顯示的圖示
        self.updateLangButtons()

        return keyHandled  # 告知系統我們是否有處理這個按鍵
