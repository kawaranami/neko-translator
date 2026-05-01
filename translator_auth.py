import base64
import io
import json
import os
import sys
import threading
import time

import urllib.request
import urllib.parse
import mss
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageOps
try:
    from deep_translator import GoogleTranslator
except:
    GoogleTranslator = None

VERSION = "0.2.4"

HIRAGANA_ROMAJI = {
    'あ': 'a', 'い': 'i', 'う': 'u', 'え': 'e', 'お': 'o',
    'か': 'ka', 'き': 'ki', 'く': 'ku', 'け': 'ke', 'こ': 'ko',
    'さ': 'sa', 'し': 'shi', 'す': 'su', 'せ': 'se', 'そ': 'so',
    'た': 'ta', 'ち': 'chi', 'つ': 'tsu', 'て': 'te', 'と': 'to',
    'な': 'na', 'に': 'ni', 'ぬ': 'nu', 'ね': 'ne', 'の': 'no',
    'は': 'ha', 'ひ': 'hi', 'ふ': 'fu', 'へ': 'he', 'ほ': 'ho',
    'ま': 'ma', 'み': 'mi', 'む': 'mu', 'め': 'me', 'も': 'mo',
    'や': 'ya', 'ゆ': 'yu', 'よ': 'yo',
    'ら': 'ra', 'り': 'ri', 'る': 'ru', 'れ': 're', 'ろ': 'ro',
    'わ': 'wa', 'を': 'wo', 'ん': 'n',
    'が': 'ga', 'ぎ': 'gi', 'ぐ': 'gu', 'げ': 'ge', 'ご': 'go',
    'ざ': 'za', 'じ': 'ji', 'ず': 'zu', 'ぜ': 'ze', 'ぞ': 'zo',
    'だ': 'da', 'ぢ': 'ji', 'づ': 'zu', 'で': 'de', 'ど': 'do',
    'ば': 'ba', 'び': 'bi', 'ぶ': 'bu', 'べ': 'be', 'ぼ': 'bo',
    'ぱ': 'pa', 'ぴ': 'pi', 'ぷ': 'pu', 'ぺ': 'pe', 'ぽ': 'po',
}

KATAKANA_ROMAJI = {
    'ア': 'a', 'イ': 'i', 'ウ': 'u', 'エ': 'e', 'オ': 'o',
    'カ': 'ka', 'キ': 'ki', 'ク': 'ku', 'ケ': 'ke', 'コ': 'ko',
    'サ': 'sa', 'シ': 'shi', 'ス': 'su', 'セ': 'se', 'ソ': 'so',
    'タ': 'ta', 'チ': 'chi', 'ツ': 'tsu', 'テ': 'te', 'ト': 'to',
    'ナ': 'na', 'ニ': 'ni', 'ヌ': 'nu', 'ネ': 'ne', 'ノ': 'no',
    'ハ': 'ha', 'ヒ': 'hi', 'フ': 'fu', 'ヘ': 'he', 'ホ': 'ho',
    'マ': 'ma', 'ミ': 'mi', 'ム': 'mu', 'メ': 'me', 'モ': 'mo',
    'ヤ': 'ya', 'ユ': 'yu', 'ヨ': 'yo',
    'ラ': 'ra', 'リ': 'ri', 'ル': 'ru', 'レ': 're', 'ロ': 'ro',
    'ワ': 'wa', 'ヲ': 'wo', 'ン': 'n',
    'ガ': 'ga', 'ギ': 'gi', 'グ': 'gu', 'ゲ': 'ge', 'ゴ': 'go',
    'ザ': 'za', 'ジ': 'ji', 'ズ': 'zu', 'ゼ': 'ze', 'ゾ': 'zo',
    'ダ': 'da', 'ヂ': 'ji', 'ヅ': 'zu', 'デ': 'de', 'ド': 'do',
    'バ': 'ba', 'ビ': 'bi', 'ブ': 'bu', 'ベ': 'be', 'ボ': 'bo',
    'パ': 'pa', 'ピ': 'pi', 'プ': 'pu', 'ペ': 'pe', 'ポ': 'po',
}

def text_to_romaji(text):
    result = []
    i = 0
    while i < len(text):
        c = text[i]
        if c in HIRAGANA_ROMAJI:
            result.append(HIRAGANA_ROMAJI[c])
        elif c in KATAKANA_ROMAJI:
            result.append(KATAKANA_ROMAJI[c])
        elif c == 'ー':
            if result:
                result[-1] += result[-1][-1]
        elif c in '.,!?;:()[]{}""''':
            result.append(c)
        elif c == ' ':
            result.append(' ')
        elif '\u4e00' <= c <= '\u9fff':
            result.append(c)
        else:
            result.append(c)
        i += 1
    return ' '.join(result)

LANG = {
    "ja": {
        "auth_title": "APIキー設定",
        "auth_subtitle": "翻訳機の動作に必要なAPIキーを入力してください",
        "translate_section": " 翻訳  ",
        "provider": "プロバイダー:",
        "api_key": "APIキー:",
        "ocr_section": " OCR（オプション）  ",
        "ocr_key_label": "Google Vision APIキー:",
        "confirm": "確認",
        "skip_ocr": "OCRなし",
        "enter_key": "翻訳用のAPIキーを入力してください",
        "checking": "キーを確認中...",
        "invalid_key": "無効なキー: ",
        "app_title": "Neko Translator",
        "direction": "方向:",
        "ja_to_ru": "JP → RU",
        "ru_to_ja": "RU → JP",
        "style": "スタイル:",
        "select_area": "📷 領域選択",
        "preview": "プレビュー:",
        "recognize": "✓ 認識",
        "cancel": "✗ キャンセル",
        "input": "入力:",
        "translate": "翻訳",
        "clear": "クリア",
        "switch_dir": "方向切替",
        "result": "結果:",
        "history": "翻訳履歴:",
        "clear_history": "クリア",
        "no_history": "まだ翻訳がありません",
        "ready": "準備完了",
        "enter_text": "テキストを入力してください",
        "translating": "翻訳中...",
        "error_ja_for_jaru": "エラー: JP→RUには日本語を入力してください",
        "error_ru_for_ruja": "エラー: RU→JPにはロシア語を入力してください",
        "error_unknown_lang": "エラー: 言語を判定できません（日本語またはロシア語を入力）",
        "copied": "クリップボードにコピーしました！",
        "history_cleared": "履歴をクリアしました",
        "ocr_not_set": "OCRが設定されていません",
        "select_region": "画面の領域を選択してください...",
        "cancelled": "キャンセルしました",
        "capturing": "領域をキャプチャ中...",
        "region_selected": "領域を選択しました。「認識」または「キャンセル」を押してください",
        "recognizing": "テキストを認識中...",
        "no_japanese": "日本語テキストが見つかりません",
        "error": "エラー",
        "no_text": "テキストなし",
        "style_neutral": "スタイル: ニュートラル",
        "style_casual": "スタイル: カジュアル（非公式）",
        "style_formal": "スタイル: ポライト（公式）",
        "style_mixed": "スタイル: 混合",
        "lang_label": "言語:",
        "japanese": "日本語",
        "russian": "Русский",
        "english": "English",
        "formality_neutral": "ニュートラル",
        "formality_casual": "カジュアル",
        "formality_formal": "ポライト",
        "romaji": "ローマ字",
        "tooltip_text": "制限: 遅延1-3秒、頻繁な使用で一時停止の可能性。\n対応形式: desu/masu形のみ",
        "save_key": "キーを保存",
        "saved_key_loaded": "保存されたキーをロードしました",
    },
    "ru": {
        "auth_title": "Настройка API ключей",
        "auth_subtitle": "Введите ключи для работы переводчика",
        "translate_section": " Перевод  ",
        "provider": "Провайдер:",
        "api_key": "API ключ:",
        "ocr_section": " OCR (опционально)  ",
        "ocr_key_label": "Google Vision API ключ:",
        "confirm": "Подтвердить",
        "skip_ocr": "Без OCR",
        "enter_key": "Введите API ключ для перевода",
        "checking": "Проверяю ключи...",
        "invalid_key": "Неверный ключ: ",
        "app_title": "Neko Translator",
        "direction": "Направление:",
        "ja_to_ru": "JP → RU",
        "ru_to_ja": "RU → JP",
        "style": "Стиль:",
        "select_area": " Выбрать область",
        "preview": "Предпросмотр:",
        "recognize": "✓ Распознать",
        "cancel": "✗ Отмена",
        "input": "Ввод:",
        "translate": "Перевести",
        "clear": "Очистить",
        "switch_dir": "Сменить направление",
        "result": "Результат:",
        "history": "История переводов:",
        "clear_history": "Очистить",
        "no_history": "Пока нет переводов",
        "ready": "Готов",
        "enter_text": "Введите текст",
        "translating": "Перевожу...",
        "error_ja_for_jaru": "Ошибка: для JP→RU введите японский текст",
        "error_ru_for_ruja": "Ошибка: для RU→JP введите русский текст",
        "error_unknown_lang": "Ошибка: не удалось определить язык (введите японский или русский)",
        "copied": "Скопировано в буфер обмена!",
        "history_cleared": "История очищена",
        "ocr_not_set": "OCR не настроен",
        "select_region": "Выберите область экрана...",
        "cancelled": "Отменено",
        "capturing": "Захватываю область...",
        "region_selected": "Область выбрана. Нажмите 'Распознать' или 'Отмена'",
        "recognizing": "Распознаю текст...",
        "no_japanese": "Японский текст не найден",
        "error": "Ошибка",
        "no_text": "Нет текста",
        "style_neutral": "Стиль: нейтральный",
        "style_casual": "Стиль: дружеский (неформальный)",
        "style_formal": "Стиль: вежливый (формальный)",
        "style_mixed": "Стиль: смешанный",
        "lang_label": "Язык:",
        "japanese": "日本語",
        "russian": "Русский",
        "english": "English",
        "formality_neutral": "Нейтральный",
        "formality_casual": "Дружеский",
        "formality_formal": "Вежливый",
        "romaji": "Ромадзи",
        "tooltip_text": "Ограничения: задержка 1-3с, возможны временные блокировки при частых запросах.\nПоддерживается только форма desu/masu",
        "save_key": "Сохранить ключ",
        "saved_key_loaded": "Загружен сохранённый ключ",
    },
    "en": {
        "auth_title": "API Key Setup",
        "auth_subtitle": "Enter API keys for the translator to work",
        "translate_section": " Translation  ",
        "provider": "Provider:",
        "api_key": "API Key:",
        "ocr_section": " OCR (optional)  ",
        "ocr_key_label": "Google Vision API Key:",
        "confirm": "Confirm",
        "skip_ocr": "No OCR",
        "enter_key": "Enter translation API key",
        "checking": "Checking keys...",
        "invalid_key": "Invalid key: ",
        "app_title": "Neko Translator",
        "direction": "Direction:",
        "ja_to_ru": "JP → RU",
        "ru_to_ja": "RU → JP",
        "style": "Style:",
        "select_area": "📷 Select Area",
        "preview": "Preview:",
        "recognize": "✓ Recognize",
        "cancel": "✗ Cancel",
        "input": "Input:",
        "translate": "Translate",
        "clear": "Clear",
        "switch_dir": "Switch Direction",
        "result": "Result:",
        "history": "Translation History:",
        "clear_history": "Clear",
        "no_history": "No translations yet",
        "ready": "Ready",
        "enter_text": "Enter text",
        "translating": "Translating...",
        "error_ja_for_jaru": "Error: enter Japanese text for JP→RU",
        "error_ru_for_ruja": "Error: enter Russian text for RU→JP",
        "error_unknown_lang": "Error: cannot detect language (enter Japanese or Russian)",
        "copied": "Copied to clipboard!",
        "history_cleared": "History cleared",
        "ocr_not_set": "OCR not configured",
        "select_region": "Select screen region...",
        "cancelled": "Cancelled",
        "capturing": "Capturing region...",
        "region_selected": "Region selected. Press 'Recognize' or 'Cancel'",
        "recognizing": "Recognizing text...",
        "no_japanese": "No Japanese text found",
        "error": "Error",
        "no_text": "No text",
        "style_neutral": "Style: neutral",
        "style_casual": "Style: casual (informal)",
        "style_formal": "Style: polite (formal)",
        "style_mixed": "Style: mixed",
        "lang_label": "Language:",
        "japanese": "日本語",
        "russian": "Русский",
        "english": "English",
        "formality_neutral": "Neutral",
        "formality_casual": "Casual",
        "formality_formal": "Polite",
        "romaji": "Romaji",
        "tooltip_text": "Limits: 1-3s delay, possible temporary blocks on frequent requests.\nOnly desu/masu form supported",
        "save_key": "Save Key",
        "saved_key_loaded": "Loaded saved key",
    },
}

FORMALITY_LEVELS = {
    "neutral": "formality_neutral",
    "casual": "formality_casual",
    "formal": "formality_formal",
}

HISTORY_FILE = "translation_history.json"
LOG_FILE = "translator_debug.log"
CONFIG_FILE = "config.json"
MAX_HISTORY = 10

TRANSLATE_API_KEY = ""
TRANSLATE_PROVIDER = "deepl"
OCR_API_KEY = ""
OCR_PROVIDER = "google"

def _log(msg):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {msg}\n")
    except:
        pass

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_history(history):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history[:MAX_HISTORY], f, ensure_ascii=False, indent=2)
    except:
        pass

def t(lang, key):
    return LANG.get(lang, LANG["ja"]).get(key, key)

def translate_with_deepl(text, source, target, formality="default"):
    url = "https://api-free.deepl.com/v2/translate"
    payload = {
        "text": text,
        "source_lang": source.upper(),
        "target_lang": target.upper(),
        "formality": formality
    }
    req = urllib.request.Request(
        url,
        data=urllib.parse.urlencode(payload).encode("utf-8"),
        headers={
            "Authorization": f"DeepL-Auth-Key {TRANSLATE_API_KEY}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
    )
    response = urllib.request.urlopen(req)
    result = json.loads(response.read().decode("utf-8"))
    return result["translations"][0]["text"]

def translate_with_google(text, source, target):
    url = f"https://translation.googleapis.com/language/translate/v2?key={TRANSLATE_API_KEY}"
    payload = {
        "q": text,
        "source": source,
        "target": target,
        "format": "text"
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    response = urllib.request.urlopen(req)
    result = json.loads(response.read().decode("utf-8"))
    return result["data"]["translations"][0]["translatedText"]

def translate_free(text, source, target):
    if GoogleTranslator is None:
        raise Exception("deep-translator library not installed. Run: pip install deep-translator")
    try:
        translator = GoogleTranslator(source=source, target=target)
        result = translator.translate(text)
        if not result:
            raise Exception("Empty translation result")
        return result
    except Exception as e:
        raise Exception(f"Free API error: {e}")

def translate_text(text, source, target, formality="default"):
    if TRANSLATE_PROVIDER == "deepl":
        return translate_with_deepl(text, source, target, formality)
    elif TRANSLATE_PROVIDER == "google":
        return translate_with_google(text, source, target)
    else:
        return translate_free(text, source, target)

def save_config(provider, api_key, ocr_key, save_key):
    try:
        config = {}
        if save_key:
            config = {"provider": provider, "api_key": api_key, "ocr_key": ocr_key}
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except:
        pass

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {}

def ocr_with_google_vision(image_b64):
    url = f"https://vision.googleapis.com/v1/images:annotate?key={OCR_API_KEY}"
    payload = {
        "requests": [{
            "image": {"content": image_b64},
            "features": [{"type": "TEXT_DETECTION", "maxResults": 50}],
            "imageContext": {"languageHints": ["ja"]}
        }]
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    response = urllib.request.urlopen(req)
    return json.loads(response.read().decode("utf-8"))

class AuthWindow:
    def __init__(self, callback):
        self.callback = callback
        self.ui_lang = "ja"
        self.root = tk.Tk()
        self.root.title(t(self.ui_lang, "auth_title"))
        self.root.geometry("540x750")
        self.root.resizable(False, False)
        self.root.configure(bg="#0f172a")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.saved_config = load_config()
        self._build_ui()

    def _build_ui(self):
        main = tk.Frame(self.root, bg="#0f172a", padx=30, pady=20)
        main.pack(fill=tk.BOTH, expand=True)

        lang_frame = tk.Frame(main, bg="#0f172a")
        lang_frame.pack(fill=tk.X, pady=(0, 8))
        tk.Label(lang_frame, text=t(self.ui_lang, "lang_label"), bg="#0f172a", fg="#64748b",
                font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 6))
        self.lang_var = tk.StringVar(value="ja")
        lang_combo = ttk.Combobox(lang_frame, state="readonly", values=["ja", "ru", "en"],
                                  textvariable=self.lang_var, width=8)
        lang_combo.pack(side=tk.LEFT)
        lang_combo.bind("<<ComboboxSelected>>", lambda e: self._switch_lang())

        header_frame = tk.Frame(main, bg="#0f172a")
        header_frame.pack(fill=tk.X, pady=(0, 8))
        self.title_label = tk.Label(header_frame, text=t(self.ui_lang, "auth_title"),
                                    font=("Segoe UI", 18, "bold"), bg="#0f172a", fg="#e2e8f0")
        self.title_label.pack()
        self.subtitle_label = tk.Label(header_frame, text=t(self.ui_lang, "auth_subtitle"),
                                       font=("Segoe UI", 9), bg="#0f172a", fg="#64748b")
        self.subtitle_label.pack(pady=(2, 0))

        separator = tk.Frame(main, bg="#1e293b", height=1)
        separator.pack(fill=tk.X, pady=(8, 16))

        translate_frame = tk.LabelFrame(main, text=t(self.ui_lang, "translate_section"),
                                       bg="#0f172a", fg="#818cf8", font=("Segoe UI", 9, "bold"),
                                       padx=15, pady=12, bd=0)
        translate_frame.pack(fill=tk.X, pady=(0, 12))

        translate_inner = tk.Frame(translate_frame, bg="#1e293b", bd=0)
        translate_inner.pack(fill=tk.X)

        self.provider_label = tk.Label(translate_inner, text=t(self.ui_lang, "provider"),
                                       bg="#1e293b", fg="#64748b", font=("Segoe UI", 9))
        self.provider_label.pack(anchor="w", padx=(12, 0), pady=(8, 4))

        self.translate_provider = tk.StringVar(value="deepl")
        provider_frame = tk.Frame(translate_inner, bg="#1e293b")
        provider_frame.pack(fill=tk.X, padx=(12, 0), pady=(0, 8))

        self.provider_var = tk.StringVar(value="public")
        provider_frame = tk.Frame(translate_inner, bg="#1e293b")
        provider_frame.pack(fill=tk.X, padx=(12, 0), pady=(0, 8))

        self.provider_btns = {}
        for p, label in [("deepl", "DeepL"), ("google", "Google"), ("public", "Google (free)")]:
            btn = tk.Button(provider_frame, text=label, font=("Segoe UI", 9), bd=0, padx=10, pady=4,
                           bg="#0f172a", fg="#64748b", activebackground="#334155", cursor="hand2",
                           command=lambda prov=p: self._select_provider(prov))
            btn.pack(side=tk.LEFT, padx=(0, 8))
            self.provider_btns[p] = btn
        
        self.save_key_var = tk.BooleanVar(value=bool(self.saved_config.get("api_key")))
        self.save_key_cb = tk.Checkbutton(provider_frame, text=t(self.ui_lang, "save_key"), variable=self.save_key_var,
                                         bg="#1e293b", fg="#64748b", selectcolor="#0f172a", activebackground="#1e293b",
                                          font=("Segoe UI", 9))
        self.save_key_cb.pack(side=tk.RIGHT)
        
        self.info_icon = tk.Label(provider_frame, text="!", bg="#1e293b", fg="#f59e0b", 
                                 font=("Segoe UI", 9, "bold"), cursor="hand2")
        self.info_icon.pack(side=tk.LEFT, padx=(4, 0))
        
        self.tooltip_window = tk.Toplevel(self.root)
        self.tooltip_window.withdraw()
        self.tooltip_window.overrideredirect(True)
        self.tooltip_label = tk.Label(self.tooltip_window, text="",
                  bg="#1e293b", fg="#e2e8f0", font=("Segoe UI", 9), relief="solid", bd=1, padx=4, pady=2)
        self.tooltip_label.pack()
        
        def show_tooltip(event):
            self._update_tooltip_text()
            x = self.info_icon.winfo_rootx() + 10
            y = self.info_icon.winfo_rooty() + 20
            self.tooltip_window.geometry(f"+{x}+{y}")
            self.tooltip_window.deiconify()
            
        def hide_tooltip(event):
            self.tooltip_window.withdraw()
            
        self.info_icon.bind("<Enter>", show_tooltip)
        self.info_icon.bind("<Leave>", hide_tooltip)

        self.api_key_label = tk.Label(translate_inner, text=t(self.ui_lang, "api_key"),
                                      bg="#1e293b", fg="#64748b", font=("Segoe UI", 8))
        self.api_key_label.pack(anchor="w", padx=(12, 0), pady=(4, 4))

        self.translate_key_entry = tk.Entry(translate_inner, font=("Segoe UI", 10),
                                            bg="#0f172a", fg="#e2e8f0", insertbackground="#818cf8",
                                            bd=0, highlightthickness=1, highlightbackground="#334155")
        self.translate_key_entry.pack(fill=tk.X, padx=(12, 12), pady=(0, 8))
        self.translate_key_entry.bind("<Return>", lambda e: self._confirm_and_start())
        self._add_right_click_menu(self.translate_key_entry)
        self.translate_key_entry.focus_set()

        self.translate_hint = tk.Label(translate_inner, text="fe86ec71-xxxx-xxxx-xxxx-xxxxxxxxxxxx:fx",
                                      bg="#1e293b", fg="#475569", font=("Segoe UI", 7))
        self.translate_hint.pack(anchor="w", padx=(12, 0), pady=(0, 8))

        ocr_frame = tk.LabelFrame(main, text=t(self.ui_lang, "ocr_section"),
                                 bg="#0f172a", fg="#818cf8", font=("Segoe UI", 9, "bold"),
                                 padx=15, pady=12, bd=0)
        ocr_frame.pack(fill=tk.X, pady=(0, 16))

        ocr_inner = tk.Frame(ocr_frame, bg="#1e293b", bd=0)
        ocr_inner.pack(fill=tk.X)

        self.ocr_key_label = tk.Label(ocr_inner, text=t(self.ui_lang, "ocr_key_label"),
                                      bg="#1e293b", fg="#64748b", font=("Segoe UI", 8))
        self.ocr_key_label.pack(anchor="w", padx=(12, 0), pady=(8, 4))

        self.ocr_key_entry = tk.Entry(ocr_inner, font=("Segoe UI", 10),
                                     bg="#0f172a", fg="#e2e8f0", insertbackground="#818cf8",
                                     bd=0, highlightthickness=1, highlightbackground="#334155")
        self.ocr_key_entry.pack(fill=tk.X, padx=(12, 12), pady=(0, 4))
        self._add_right_click_menu(self.ocr_key_entry)

        tk.Label(ocr_inner, text="AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                bg="#1e293b", fg="#475569", font=("Segoe UI", 7)).pack(anchor="w", padx=(12, 0), pady=(0, 8))

        self.status_label = tk.Label(main, text="", bg="#0f172a", fg="#ef4444", font=("Segoe UI", 9))
        self.status_label.pack(pady=(8, 0))

        btn_frame = tk.Frame(main, bg="#0f172a")
        btn_frame.pack(fill=tk.X, pady=(24, 0))

        self.confirm_btn = tk.Button(btn_frame, text=t(self.ui_lang, "confirm"),
                                     command=self._confirm_and_start,
                                     bg="#6366f1", fg="white", font=("Segoe UI", 10, "bold"),
                                     bd=0, padx=24, pady=10, activebackground="#818cf8", cursor="hand2")
        self.confirm_btn.pack(side=tk.LEFT)
        
        self._select_provider("public")

    def _select_provider(self, provider):
        self.provider_var.set(provider)
        for p, btn in self.provider_btns.items():
            if p == provider:
                btn.config(bg="#6366f1", fg="white")
            else:
                btn.config(bg="#0f172a", fg="#64748b")
        saved = self.saved_config
        if provider == "deepl" and saved.get("provider") == "deepl" and saved.get("api_key"):
            self.translate_key_entry.delete(0, tk.END)
            self.translate_key_entry.insert(0, saved["api_key"])
        elif provider == "google" and saved.get("provider") == "google" and saved.get("api_key"):
            self.translate_key_entry.delete(0, tk.END)
            self.translate_key_entry.insert(0, saved["api_key"])
        if saved.get("ocr_key"):
            self.ocr_key_entry.delete(0, tk.END)
            self.ocr_key_entry.insert(0, saved["ocr_key"])
        self._update_provider_ui()

    def _update_tooltip_text(self):
        self.tooltip_label.config(text=t(self.ui_lang, "tooltip_text"))

    def _update_provider_ui(self):
        provider = self.provider_var.get()
        if provider == "public":
            self.translate_key_entry.pack_forget()
            self.api_key_label.pack_forget()
            self.translate_hint.pack_forget()
            self.tooltip_window.withdraw()
        else:
            self.api_key_label.pack(anchor="w", padx=(12, 0), pady=(4, 4))
            self.translate_key_entry.pack(fill=tk.X, padx=(12, 12), pady=(0, 8))
            if provider == "deepl":
                self.translate_hint.config(text="fe86ec71-xxxx-xxxx-xxxx-xxxxxxxxxxxx:fx")
            else:
                self.translate_hint.config(text="AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
            self.translate_hint.pack(anchor="w", padx=(12, 0), pady=(0, 8))

    def _switch_lang(self):
        self.ui_lang = self.lang_var.get()
        self.root.title(t(self.ui_lang, "auth_title"))
        self.title_label.config(text=t(self.ui_lang, "auth_title"))
        self.subtitle_label.config(text=t(self.ui_lang, "auth_subtitle"))
        translate_frame = self.provider_label.master.master
        translate_frame.config(text=t(self.ui_lang, "translate_section"))
        self.provider_label.config(text=t(self.ui_lang, "provider"))
        self.api_key_label.config(text=t(self.ui_lang, "api_key"))
        ocr_frame = self.ocr_key_label.master.master
        ocr_frame.config(text=t(self.ui_lang, "ocr_section"))
        self.ocr_key_label.config(text=t(self.ui_lang, "ocr_key_label"))
        self.confirm_btn.config(text=t(self.ui_lang, "confirm"))
        self.skip_ocr_btn.config(text=t(self.ui_lang, "skip_ocr"))

    def _add_right_click_menu(self, widget):
        menu = tk.Menu(widget, tearoff=False, bg="#1e293b", fg="#e2e8f0", activebackground="#6366f1")
        menu.add_command(label="Copy", command=lambda: widget.event_generate("<<Copy>>"))
        menu.add_command(label="Paste", command=lambda: widget.event_generate("<<Paste>>"))
        menu.add_command(label="Select All", command=lambda: widget.event_generate("<<SelectAll>>"))
        widget.bind("<Button-3>", lambda e: menu.tk_popup(e.x_root, e.y_root))

    def _confirm_and_start(self):
        global TRANSLATE_API_KEY, TRANSLATE_PROVIDER, OCR_API_KEY, OCR_PROVIDER
        
        provider = self.provider_var.get()
        translate_key = self.translate_key_entry.get().strip()
        ocr_key = self.ocr_key_entry.get().strip()
        save_key = self.save_key_var.get()

        if provider != "public" and not translate_key:
            saved = self.saved_config
            if saved.get("provider") == provider and saved.get("api_key"):
                translate_key = saved["api_key"]
            else:
                self.status_label.config(text=t(self.ui_lang, "enter_key"), fg="#ef4444")
                return

        if provider != "public" and not self.saved_config.get("api_key"):
            self.status_label.config(text=t(self.ui_lang, "checking"), fg="#f59e0b")
            self.root.update()
            self.confirm_btn.config(state="disabled")

            translate_ok = False
            translate_error = ""
            try:
                TRANSLATE_API_KEY = translate_key
                TRANSLATE_PROVIDER = provider
                if provider == "deepl":
                    translate_with_deepl("test", "en", "ru")
                else:
                    translate_with_google("test", "en", "ru")
                translate_ok = True
            except Exception as e:
                translate_error = str(e)

            if not translate_ok:
                self.status_label.config(text=t(self.ui_lang, "invalid_key") + translate_error[:80], fg="#ef4444")
                self.confirm_btn.config(state="normal")
                return
            
            TRANSLATE_API_KEY = translate_key
            TRANSLATE_PROVIDER = provider
        else:
            if provider != "public":
                TRANSLATE_API_KEY = translate_key
                TRANSLATE_PROVIDER = provider
            else:
                TRANSLATE_PROVIDER = "public"
                TRANSLATE_API_KEY = ""

        if ocr_key:
            try:
                OCR_API_KEY = ocr_key
                OCR_PROVIDER = "google"
                url = f"https://vision.googleapis.com/v1/images:annotate?key={OCR_API_KEY}"
                payload = {"requests": [{"image": {"content": ""}, "features": [{"type": "TEXT_DETECTION"}]}]}
                req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"),
                                           headers={"Content-Type": "application/json"})
                urllib.request.urlopen(req, timeout=5)
            except:
                pass

        OCR_API_KEY = ocr_key
        OCR_PROVIDER = "google" if ocr_key else ""

        save_config(provider, translate_key, ocr_key, save_key)

        self._finish(True, bool(ocr_key))

    def _finish(self, translate_ok, ocr_ok):
        self.root.destroy()
        self.callback(translate_ok, ocr_ok, self.ui_lang, self.provider_var.get())

    def on_close(self):
        self.root.destroy()
        sys.exit()

class RegionSelector:
    def __init__(self, callback):
        self.callback = callback
        self.start_x = 0
        self.start_y = 0
        self.current_x = 0
        self.current_y = 0
        self.rect = None

        self.root = tk.Toplevel()
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-alpha", 0.3)
        self.root.configure(bg="#000000")
        self.root.bind("<Escape>", lambda e: self.cancel())

        self.canvas = tk.Canvas(self.root, cursor="crosshair", bg="#000000", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        self.root.focus_force()

    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline="#6366f1", width=3, fill=""
        )

    def on_drag(self, event):
        self.current_x = event.x
        self.current_y = event.y
        if self.rect:
            self.canvas.coords(self.rect, self.start_x, self.start_y, self.current_x, self.current_y)

    def on_release(self, event):
        self.root.destroy()
        x1, y1 = min(self.start_x, self.current_x), min(self.start_y, self.current_y)
        x2, y2 = max(self.start_x, self.current_x), max(self.start_y, self.current_y)
        if abs(x2 - x1) > 10 and abs(y2 - y1) > 10:
            self.callback(x1, y1, x2, y2)

    def cancel(self):
        self.root.destroy()
        self.callback(None, None, None, None)

class TranslatorApp:
    def __init__(self, has_ocr, ui_lang="ja", provider="deepl"):
        self.root = tk.Tk()
        self.ui_lang = ui_lang
        self.provider = provider
        self.root.title(t(self.ui_lang, "app_title") + f" {VERSION}")
        self.root.geometry("900x900")
        self.root.resizable(False, False)
        self.root.configure(bg="#0f172a")

        self.has_ocr = has_ocr
        self.direction = tk.StringVar(value="ja-ru")
        self.formality = tk.StringVar(value="neutral")
        self.status = tk.StringVar(value=t(self.ui_lang, "ready"))
        self.preview_photo = None
        self.history = load_history()

        self._setup_styles()
        self._build_ui()

        import keyboard
        if has_ocr:
            keyboard.add_hotkey("ctrl+t", self.start_region_select)
        keyboard.add_hotkey("ctrl+d", self.switch_direction)
        keyboard.add_hotkey("ctrl+c", self.copy_translation)

        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)
        self._create_tray()

    def _setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TFrame", background="#0f172a")
        self.style.configure("TLabelframe", background="#0f172a", borderwidth=0)
        self.style.configure("TLabelframe.Label", background="#0f172a", foreground="#818cf8",
                            font=("Segoe UI", 10, "bold"))
        self.style.configure("TLabel", background="#0f172a", foreground="#94a3b8", font=("Segoe UI", 10))
        self.style.configure("Accent.TLabel", background="#0f172a", foreground="#818cf8", font=("Segoe UI", 9, "bold"))
        self.style.configure("TButton", background="#6366f1", foreground="white", font=("Segoe UI", 10),
                            borderwidth=0, focuscolor="none", padding=(12, 6))
        self.style.map("TButton", background=[("active", "#818cf8"), ("pressed", "#4f46e5")])
        self.style.configure("Secondary.TButton", background="#0f172a", foreground="#64748b", font=("Segoe UI", 10),
                            borderwidth=0, focuscolor="none", padding=(8, 4))
        self.style.map("Secondary.TButton", background=[("active", "#1e293b")], foreground=[("active", "#94a3b8")])
        self.style.configure("Success.TButton", background="#10b981", foreground="white", font=("Segoe UI", 10),
                            borderwidth=0, focuscolor="none", padding=(12, 6))
        self.style.map("Success.TButton", background=[("active", "#34d399")])
        self.style.configure("Danger.TButton", background="#0f172a", foreground="#ef4444", font=("Segoe UI", 10),
                            borderwidth=0, focuscolor="none", padding=(8, 4))
        self.style.map("Danger.TButton", foreground=[("active", "#f87171")])
        self.style.configure("TRadiobutton", background="#0f172a", foreground="#94a3b8", font=("Segoe UI", 10))
        self.style.configure("TCombobox", fieldbackground="#1e293b", background="#1e293b",
                            foreground="#e2e8f0", borderwidth=0, arrowcolor="#818cf8", font=("Segoe UI", 10))
        self.style.map("TCombobox", fieldbackground=[("readonly", "#1e293b")])

    def _build_ui(self):
        main = tk.Frame(self.root, bg="#0f172a", padx=24, pady=20)
        main.pack(fill=tk.BOTH, expand=True)

        header = tk.Frame(main, bg="#0f172a")
        header.pack(fill=tk.X, pady=(0, 16))

        self.app_title_label = tk.Label(header, text="  " + t(self.ui_lang, "app_title"), font=("Segoe UI", 16, "bold"),
                bg="#0f172a", fg="#e2e8f0")
        self.app_title_label.pack(side=tk.LEFT)

        lang_frame = tk.Frame(header, bg="#0f172a")
        lang_frame.pack(side=tk.RIGHT)
        tk.Label(lang_frame, text=t(self.ui_lang, "lang_label"), bg="#0f172a", fg="#64748b",
                font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 6))
        self.lang_var = tk.StringVar(value=self.ui_lang)
        lang_combo = ttk.Combobox(lang_frame, state="readonly", values=["ja", "ru", "en"],
                                  textvariable=self.lang_var, width=7)
        lang_combo.pack(side=tk.LEFT)
        lang_combo.bind("<<ComboboxSelected>>", lambda e: self._switch_lang())

        controls = tk.Frame(main, bg="#0f172a")
        controls.pack(fill=tk.X, pady=(0, 14))

        self.dir_label = tk.Label(controls, text=t(self.ui_lang, "direction"), bg="#0f172a", fg="#64748b", font=("Segoe UI", 9))
        self.dir_label.pack(side=tk.LEFT, padx=(0, 8))

        dir_frame = tk.Frame(controls, bg="#1e293b", bd=0)
        dir_frame.pack(side=tk.LEFT, padx=(0, 16))

        self.dir_jp_ru = tk.Radiobutton(dir_frame, text=t(self.ui_lang, "ja_to_ru"), variable=self.direction, value="ja-ru",
                      bg="#1e293b", fg="#e2e8f0", selectcolor="#6366f1", activebackground="#1e293b",
                      font=("Segoe UI", 9), bd=0, highlightthickness=0)
        self.dir_jp_ru.pack(side=tk.LEFT, padx=(4, 8))
        self.dir_ru_jp = tk.Radiobutton(dir_frame, text=t(self.ui_lang, "ru_to_ja"), variable=self.direction, value="ru-ja",
                      bg="#1e293b", fg="#e2e8f0", selectcolor="#6366f1", activebackground="#1e293b",
                      font=("Segoe UI", 9), bd=0, highlightthickness=0)
        self.dir_ru_jp.pack(side=tk.LEFT, padx=(0, 4))

        self.form_label = tk.Label(controls, text=t(self.ui_lang, "style"), bg="#0f172a", fg="#64748b", font=("Segoe UI", 9))
        self.form_label.pack(side=tk.LEFT, padx=(0, 8))

        formality_values = [t(self.ui_lang, v) for v in ["formality_casual", "formality_formal"]]
        self.formality_combo = ttk.Combobox(controls, state="readonly", values=formality_values, width=14)
        self.formality_combo.current(1)
        self.formality_combo.pack(side=tk.LEFT, padx=(0, 16))

        if self.provider == "public":
            self.form_label.pack_forget()
            self.formality_combo.pack_forget()

        if self.has_ocr:
            self.ocr_btn = tk.Button(controls, text=t(self.ui_lang, "select_area"), command=self.start_region_select,
                               bg="#6366f1", fg="white", font=("Segoe UI", 9), bd=0, padx=12, pady=4,
                               activebackground="#818cf8", cursor="hand2")
            self.ocr_btn.pack(side=tk.RIGHT)

        self.input_label = tk.Label(main, text=t(self.ui_lang, "input"), bg="#0f172a", fg="#818cf8",
                               font=("Segoe UI", 9, "bold"))
        self.input_label.pack(anchor="w", pady=(0, 4))

        self.manual_text = tk.Text(main, height=4, wrap=tk.WORD, font=("Segoe UI", 11),
                                  bg="#1e293b", fg="#e2e8f0", insertbackground="#818cf8",
                                  bd=0, highlightthickness=0, selectbackground="#6366f1",
                                   selectforeground="white", padx=10, pady=8)
        self.manual_text.pack(fill=tk.X, pady=(0, 6))

        input_actions = tk.Frame(main, bg="#0f172a")
        input_actions.pack(fill=tk.X, pady=(0, 12))

        self.translate_btn = tk.Button(input_actions, text=t(self.ui_lang, "translate"), command=self.translate_manual,
                 bg="#6366f1", fg="white", font=("Segoe UI", 9), bd=0, padx=12, pady=3,
                 activebackground="#818cf8", cursor="hand2")
        self.translate_btn.pack(side=tk.LEFT, padx=(0, 6))
        self.clear_input_btn = tk.Button(input_actions, text=t(self.ui_lang, "clear"), command=lambda: self.manual_text.delete("1.0", tk.END),
                 bg="#0f172a", fg="#64748b", font=("Segoe UI", 9), bd=0, padx=6, pady=3,
                 activebackground="#1e293b", cursor="hand2")
        self.clear_input_btn.pack(side=tk.LEFT, padx=(0, 6))
        self.switch_dir_btn = tk.Button(input_actions, text=t(self.ui_lang, "switch_dir"), command=self.switch_direction,
                 bg="#0f172a", fg="#64748b", font=("Segoe UI", 9), bd=0, padx=6, pady=3,
                 activebackground="#1e293b", cursor="hand2")
        self.switch_dir_btn.pack(side=tk.LEFT)

        self.results_label = tk.Label(main, text=t(self.ui_lang, "result"), bg="#0f172a", fg="#818cf8",
                                font=("Segoe UI", 9, "bold"))
        self.results_label.pack(anchor="w", pady=(0, 4))

        self.original_text = tk.Text(main, height=5, wrap=tk.WORD, font=("Segoe UI", 11),
                                    bg="#1e293b", fg="#e2e8f0", bd=0, highlightthickness=0,
                                    selectbackground="#6366f1", selectforeground="white",
                                      padx=10, pady=8)
        self.original_text.pack(fill=tk.X, pady=(0, 6))

        self.translated_text = tk.Text(main, height=5, wrap=tk.WORD, font=("Segoe UI", 11),
                                      bg="#1e293b", fg="#e2e8f0", bd=0, highlightthickness=0,
                                      selectbackground="#6366f1", selectforeground="white",
                                    padx=10, pady=8)
        self.translated_text.pack(fill=tk.X, pady=(0, 6))

        romaji_frame = tk.Frame(main, bg="#0f172a")
        romaji_frame.pack(fill=tk.X, pady=(0, 6))

        self.romaji_btn = tk.Button(romaji_frame, text=t(self.ui_lang, "romaji"), command=self._to_romaji,
                 bg="#0f172a", fg="#818cf8", font=("Segoe UI", 9), bd=0, padx=12, pady=3,
                 activebackground="#1e293b", cursor="hand2")
        self.romaji_btn.pack(side=tk.LEFT)
        self.romaji_btn.bind("<Enter>", lambda e: self.romaji_btn.config(fg="#a5b4fc"))
        self.romaji_btn.bind("<Leave>", lambda e: self.romaji_btn.config(fg="#818cf8"))

        self.romaji_text = tk.Text(main, height=2, wrap=tk.WORD, font=("Segoe UI", 9),
                                  bg="#0f172a", fg="#64748b", bd=0, highlightthickness=0,
                                  padx=8, pady=4)
        self.romaji_text.pack(fill=tk.X, pady=(0, 6))
        self.romaji_text.pack_forget()

        reverse_frame = tk.Frame(main, bg="#0f172a")
        reverse_frame.pack(fill=tk.X)

        self.reverse_text = tk.Text(reverse_frame, height=3, wrap=tk.WORD, font=("Segoe UI", 9),
                                   bg="#0f172a", fg="#64748b", bd=0, highlightthickness=0,
                                   padx=0, pady=0)
        self.reverse_text.pack(fill=tk.X)

        self.formality_label = tk.Label(reverse_frame, text="", bg="#0f172a", fg="#818cf8",
                                       font=("Segoe UI", 9, "italic"))
        self.formality_label.pack(anchor="w", pady=(2, 0))

        history_header = tk.Frame(main, bg="#0f172a")
        history_header.pack(fill=tk.X, pady=(14, 6))

        self.history_label = tk.Label(history_header, text=t(self.ui_lang, "history"), bg="#0f172a", fg="#818cf8",
                font=("Segoe UI", 9, "bold"))
        self.history_label.pack(side=tk.LEFT)

        self.clear_history_btn = tk.Button(history_header, text=t(self.ui_lang, "clear_history"), command=self._clear_history,
                  bg="#0f172a", fg="#ef4444", font=("Segoe UI", 9), bd=0, padx=8, pady=2,
                 activebackground="#1e293b", cursor="hand2")
        self.clear_history_btn.pack(side=tk.RIGHT)

        self.history_frame = tk.Frame(main, bg="#0f172a")
        self.history_frame.pack(fill=tk.X)

        self._update_history_display()

        status_bar = tk.Frame(main, bg="#0f172a")
        status_bar.pack(fill=tk.X, pady=(10, 0))

        tk.Label(status_bar, textvariable=self.status, bg="#0f172a", fg="#64748b",
                 font=("Segoe UI", 9)).pack(side=tk.LEFT)

    def _switch_lang(self):
        self.ui_lang = self.lang_var.get()
        self.root.title(t(self.ui_lang, "app_title") + f" {VERSION}")
        if self.app_title_label:
            self.app_title_label.config(text="  " + t(self.ui_lang, "app_title"))

        self.dir_label.config(text=t(self.ui_lang, "direction"))
        self.dir_jp_ru.config(text=t(self.ui_lang, "ja_to_ru"))
        self.dir_ru_jp.config(text=t(self.ui_lang, "ru_to_ja"))
        self.form_label.config(text=t(self.ui_lang, "style"))

        current_formality_idx = self.formality_combo.current()
        formality_values = [t(self.ui_lang, v) for v in ["formality_casual", "formality_formal"]]
        self.formality_combo.config(values=formality_values)
        if 0 <= current_formality_idx < len(formality_values):
            self.formality_combo.current(current_formality_idx)

        if self.has_ocr:
            self.ocr_btn.config(text=t(self.ui_lang, "select_area"))
        if self.provider != "public":
            self.form_label.config(text=t(self.ui_lang, "style"))
        self.input_label.config(text=t(self.ui_lang, "input"))
        self.translate_btn.config(text=t(self.ui_lang, "translate"))
        self.clear_input_btn.config(text=t(self.ui_lang, "clear"))
        self.switch_dir_btn.config(text=t(self.ui_lang, "switch_dir"))
        self.romaji_btn.config(text=t(self.ui_lang, "romaji"))
        self.results_label.config(text=t(self.ui_lang, "result"))
        self.history_label.config(text=t(self.ui_lang, "history"))
        self.clear_history_btn.config(text=t(self.ui_lang, "clear_history"))
        self.status.set(t(self.ui_lang, "ready"))
        self._update_history_display()

    def _update_history_display(self):
        for widget in self.history_frame.winfo_children():
            widget.destroy()
        if not self.history:
            tk.Label(self.history_frame, text=t(self.ui_lang, "no_history"), bg="#0f172a", fg="#475569",
                    font=("Segoe UI", 8, "italic")).pack(anchor="w")
            return
        for i, item in enumerate(self.history[:5]):
            item_frame = tk.Frame(self.history_frame, bg="#1e293b", bd=0)
            item_frame.pack(fill=tk.X, pady=(0, 4))
            tk.Label(item_frame, text=f"{item['source'][:30]}...", bg="#1e293b", fg="#94a3b8",
                     font=("Segoe UI", 9), anchor="w", width=30).pack(side=tk.LEFT, padx=(8, 8), pady=4)
            tk.Label(item_frame, text="→", bg="#1e293b", fg="#6366f1", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 8))
            tk.Label(item_frame, text=f"{item['target'][:30]}...", bg="#1e293b", fg="#e2e8f0",
                     font=("Segoe UI", 9), anchor="w").pack(side=tk.LEFT, padx=(0, 8))
            tk.Button(item_frame, text="📋", command=lambda t=item['target']: self._copy_to_clipboard(t),
                      bg="#1e293b", fg="#64748b", font=("Segoe UI", 9), bd=0, padx=4, pady=2,
                     activebackground="#334155", cursor="hand2").pack(side=tk.RIGHT, padx=(0, 8))

    def _clear_history(self):
        self.history = []
        save_history(self.history)
        self._update_history_display()
        self.status.set(t(self.ui_lang, "history_cleared"))
        self.root.after(2000, lambda: self.status.set(t(self.ui_lang, "ready")))

    def _copy_to_clipboard(self, text):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.status.set(t(self.ui_lang, "copied"))
        self.root.after(2000, lambda: self.status.set(t(self.ui_lang, "ready")))

    def copy_translation(self, *args):
        text = self.translated_text.get("1.0", tk.END).strip()
        if text:
            self._copy_to_clipboard(text)

    def _to_romaji(self):
        text = self.translated_text.get("1.0", tk.END).strip()
        if not text:
            return
        has_ja = any('\u3040' <= c <= '\u309f' or '\u30a0' <= c <= '\u30ff' for c in text)
        if not has_ja:
            self.status.set("No Japanese text to convert")
            self.root.after(2000, lambda: self.status.set(t(self.ui_lang, "ready")))
            return
        romaji = text_to_romaji(text)
        self.romaji_text.delete("1.0", tk.END)
        self.romaji_text.insert("1.0", romaji)
        self.romaji_text.pack(fill=tk.X, pady=(0, 6))
        self.status.set("Converted to Romaji")
        self.root.after(3000, lambda: self.status.set(t(self.ui_lang, "ready")))

    def _create_tray(self):
        try:
            from infi.systray import SysTrayIcon
            base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            icon_path = os.path.join(base_path, 'neko_icon.ico')
            menu_items = [(t(self.ui_lang, "app_title"), self.show_window), ("Exit", self.quit_app)]
            self.tray = SysTrayIcon(icon_path, t(self.ui_lang, "app_title"), menu_items)
            self.tray.start()
        except:
            pass

    def show_window(self, *args):
        self.root.deiconify()
        self.root.lift()

    def switch_direction(self, *args):
        self.direction.set("ru-ja" if self.direction.get() == "ja-ru" else "ja-ru")
        self.status.set(f"{t(self.ui_lang, 'direction')}: {self.direction.get()}")

    def _detect_language(self, text):
        has_japanese = any('\u3040' <= c <= '\u309f' or '\u30a0' <= c <= '\u30ff' or '\u4e00' <= c <= '\u9fff' for c in text)
        has_russian = any('\u0400' <= c <= '\u04FF' for c in text)
        if has_japanese and not has_russian:
            return "ja"
        elif has_russian and not has_japanese:
            return "ru"
        elif has_japanese and has_russian:
            return "mixed"
        return "unknown"

    def translate_manual(self):
        text = self.manual_text.get("1.0", tk.END).strip()
        if not text:
            self.status.set(t(self.ui_lang, "enter_text"))
            return
        direction = self.direction.get()
        detected = self._detect_language(text)
        if direction == "ja-ru" and detected == "ru":
            self.status.set(t(self.ui_lang, "error_ja_for_jaru"))
            return
        if direction == "ru-ja" and detected == "ja":
            self.status.set(t(self.ui_lang, "error_ru_for_ruja"))
            return
        if detected == "unknown":
            self.status.set(t(self.ui_lang, "error_unknown_lang"))
            return
        self.status.set(t(self.ui_lang, "translating"))
        threading.Thread(target=self._translate_thread, args=(text,), daemon=True).start()

    def _translate_thread(self, text):
        try:
            direction = self.direction.get()
            style_key = self.formality_combo.get()
            style_map = {t(self.ui_lang, "formality_casual"): "less", t(self.ui_lang, "formality_formal"): "more"}
            formality = style_map.get(style_key, "default")
            
            _log(f"Direction: {direction}, Style: {style_key}, Formality: {formality}")
            
            if direction == "ru-ja":
                result = translate_text(text, "ru", "ja", formality)
            else:
                result = translate_text(text, "ja", "ru", formality)
            
            if direction == "ru-ja":
                reverse = translate_text(result, "ja", "ru", formality)
                formality_info = self._analyze_formality(result)
            else:
                reverse = translate_text(result, "ru", "ja", "default")
                formality_info = self._analyze_formality(result)

            self.history.insert(0, {
                "source": text,
                "target": result,
                "direction": direction,
                "time": time.strftime("%H:%M")
            })
            save_history(self.history)

            self.root.after(0, lambda: self.update_results(text, result, reverse, formality_info, t(self.ui_lang, "ready")))
            self.root.after(0, self._update_history_display)
        except Exception as e:
            _log(f"Translation error: {e}")
            self.root.after(0, lambda: self.update_results(text, f"{t(self.ui_lang, 'error')}: {e}", "", "", t(self.ui_lang, "error")))

    def _analyze_formality(self, japanese_text):
        try:
            casual = translate_text(japanese_text, "ja", "ru", "less")
            formal = translate_text(japanese_text, "ja", "ru", "more")
            if casual == formal:
                return t(self.ui_lang, "style_neutral")
            original_ru = translate_text(japanese_text, "ja", "ru", "default")
            if original_ru == casual:
                return t(self.ui_lang, "style_casual")
            elif original_ru == formal:
                return t(self.ui_lang, "style_formal")
            else:
                return t(self.ui_lang, "style_mixed")
        except:
            return ""

    def update_results(self, original, translated, reverse, formality_info, status):
        self.original_text.delete("1.0", tk.END)
        self.original_text.insert("1.0", original)
        self.translated_text.delete("1.0", tk.END)
        self.translated_text.insert("1.0", translated)
        self.reverse_text.delete("1.0", tk.END)
        self.reverse_text.insert("1.0", reverse if reverse else "")
        self.formality_label.config(text=formality_info)
        self.status.set(status)

    def start_region_select(self):
        if not self.has_ocr:
            self.status.set(t(self.ui_lang, "ocr_not_set"))
            return
        self.status.set(t(self.ui_lang, "select_region"))
        def on_region_selected(x1, y1, x2, y2):
            if x1 is None:
                self.status.set(t(self.ui_lang, "cancelled"))
                return
            self.status.set(t(self.ui_lang, "recognizing"))
            with mss.mss() as sct:
                monitor = {"top": y1, "left": x1, "width": x2-x1, "height": y2-y1}
                screenshot_data = sct.grab(monitor)
                screenshot = Image.frombytes("RGB", screenshot_data.size, screenshot_data.rgb)
            threading.Thread(target=self._ocr_thread, args=(screenshot,), daemon=True).start()
        self.root.after(100, lambda: RegionSelector(on_region_selected))

    def _ocr_thread(self, image):
        try:
            max_size = 1280
            if max(image.size) > max_size:
                ratio = max_size / max(image.size)
                new_size = (int(image.width * ratio), int(image.height * ratio))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
            image = ImageOps.grayscale(image)
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")
            image_b64 = base64.b64encode(buffer.getvalue()).decode("ascii")
            _log(f"OCR image size: {len(image_b64)} bytes")
            data = ocr_with_google_vision(image_b64)
            _log(f"Vision response: {str(data)[:500]}")
            lines = []
            for resp in data.get("responses", []):
                if "error" in resp:
                    _log(f"Vision API error: {resp['error']}")
                    continue
                for ann in resp.get("textAnnotations", []):
                    text = ann.get("description", "")
                    if text:
                        has_japanese = any('\u3040' <= c <= '\u309f' or '\u30a0' <= c <= '\u30ff' or '\u4e00' <= c <= '\u9fff' for c in text)
                        if has_japanese:
                            lines.append(text)
                            break
            original = "\n".join(lines) if lines else ""
            if not original:
                _log("No Japanese text found")
                self.root.after(0, lambda: self.update_results("", t(self.ui_lang, "no_japanese"), "", "", t(self.ui_lang, "no_text")))
                return
            _log(f"OCR found: {original[:100]}...")
            direction = self.direction.get()
            style_key = self.formality_combo.get()
            style_map = {t(self.ui_lang, "formality_casual"): "less", t(self.ui_lang, "formality_formal"): "more"}
            formality = style_map.get(style_key, "default")
            
            _log(f"OCR Direction: {direction}, Style: {style_key}, Formality: {formality}")
            
            if direction == "ru-ja":
                result = translate_text(original, "ru", "ja", formality)
            else:
                result = translate_text(original, "ja", "ru", formality)
            
            if direction == "ru-ja":
                reverse = translate_text(result, "ja", "ru", formality)
                formality_info = self._analyze_formality(result)
            else:
                reverse = translate_text(result, "ru", "ja", "default")
                formality_info = self._analyze_formality(result)
            self.history.insert(0, {
                "source": original,
                "target": result,
                "direction": direction,
                "time": time.strftime("%H:%M")
            })
            save_history(self.history)
            self.root.after(0, lambda: self.update_results(original, result, reverse, formality_info, t(self.ui_lang, "ready")))
            self.root.after(0, self._update_history_display)
        except Exception as e:
            _log(f"OCR error: {e}")
            self.root.after(0, lambda: self.update_results("", f"{t(self.ui_lang, 'error')}: {e}", "", "", t(self.ui_lang, "error")))

    def quit_app(self):
        try:
            if hasattr(self, 'tray'):
                self.tray.shutdown()
        except:
            pass
        self.root.destroy()
        sys.exit()

def main():
    def on_auth_complete(translate_ok, ocr_ok, ui_lang, provider):
        if translate_ok:
            app = TranslatorApp(ocr_ok, ui_lang, provider)
            app.root.mainloop()
    auth = AuthWindow(on_auth_complete)
    auth.root.mainloop()

if __name__ == "__main__":
    main()
