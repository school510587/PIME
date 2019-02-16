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
        if keyEvent.charCode in range(ord('0'), ord('9') + 1) and (self.get_chewing_cand_totalPage() > 0 or self.langMode == ENGLISH_MODE):
            # 當選擇鍵用，或者英數模式下，數字鍵交給新酷音處理
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
        if keys.startswith("`") and len(keys) > 1:
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
            super().onKeyDown(keyEvent)
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
