from __future__ import annotations

import asyncio
import json
import locale
import os
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import flet as ft


APP_TITLE = "Continue Config Generator"
CONTINUE_CONFIG_PATH = Path.home() / ".continue" / "config.yaml"
CONTINUE_SETTINGS_DIR = Path.home() / ".continue"
LANGUAGE_CONFIG_PATH = CONTINUE_SETTINGS_DIR / "vscode-ollama-config-generator.json"
STATUS_PENDING = "pending"
STATUS_INSPECTING = "inspecting"
STATUS_READY = "ready"
STATUS_ERROR = "error"

TRANSLATIONS = {
    "en": {
        "app_title": "Continue Config Generator",
        "language": "Language",
        "language_en": "English",
        "language_de": "German",
        "language_zh": "Chinese",
        "config_name": "ollama local config",
        "input_label": "Paste `ollama list` output",
        "input_hint": "NAME            ID              SIZE      MODIFIED\nllama3.2:latest abc123          2.0 GB    2 days ago",
        "output_label": "Generated Continue config",
        "collapse": "Click to collapse",
        "expand": "Click to expand",
        "step1": "Step 1. Load Ollama List",
        "step2": "Step 2. Inspect Models",
        "step3": "Step 3. Generate Config",
        "intro": "Run `ollama list` or paste its output, parse the model names, inspect them with `ollama show` when requested, review the sortable model table, then generate the Continue YAML only when requested.",
        "run_ollama_list": "Run ollama list",
        "inspect_models": "Inspect models",
        "generate_config": "Generate config",
        "copy_config": "Copy config",
        "write_config": "Write ~/.continue/config.yaml",
        "inspected_models": "Inspected models",
        "sort_reset": "Reset sort",
        "order_reset": "Reset columns",
        "sorting": "Sorting",
        "column_order": "Column order",
        "sorting_title": "Sorting: click a column header to add or toggle sorting. Third click removes it.",
        "column_order_title": "Column order: drag chips to reorder table columns.",
        "column_order_hint": "Drag chips to reorder table columns.",
        "sort_state_none": "No active sort",
        "sort_state_prefix": "Sort order: {value}",
        "sort_hint": "Click a column header to add or toggle sorting. Third click removes it.",
        "col_default": "Default",
        "col_name": "Name",
        "col_source": "Source",
        "col_type": "Type",
        "col_status": "Status",
        "col_architecture": "Architecture",
        "col_parameters": "Parameters",
        "col_context": "Context",
        "col_embedding": "Embedding",
        "col_quantization": "Quantization",
        "col_roles": "Roles",
        "col_continue_capabilities": "Continue capabilities",
        "type_embedding_only": "embedding-only",
        "type_normal": "normal",
        "source_local": "local",
        "source_cloud": "cloud",
        "status_pending": "Pending",
        "status_inspecting": "Inspecting...",
        "status_ready": "Ready",
        "status_error": "Error",
        "tooltip_select_default": "Select as default model",
        "tooltip_embedding_default": "Embedding-only models cannot be default",
        "status_embedding_default_error": "Embedding-only models cannot be selected as default.",
        "status_selected_default": "Selected default model: {model}",
        "status_cleared_default": "Cleared default model selection.",
        "status_inspecting_models": "Inspecting {count} model(s) with `ollama show`...",
        "status_loading_model": "Loading {index}/{count}: {model}",
        "status_loaded_metadata": "Loaded metadata for {count} model(s).{suffix} Choose one normal model in the table.",
        "status_filtered_embeddings": " Filtered out {count} embedding-only model(s).",
        "status_no_normal_models": "Loaded metadata, but no normal chat/edit/apply models were found.",
        "status_no_models_found": "No model names found in the provided text.",
        "status_parsed_models": "Parsed {count} model(s). Starting inspection...",
        "status_running_ollama_list": "Running `ollama list`...",
        "status_loaded_ollama_list": "Loaded `ollama list` output. Click `Inspect models` to parse and inspect.",
        "status_select_model_first": "Inspect models first and select one normal model in the table.",
        "status_selected_model_missing": "The selected model has no inspected metadata yet.",
        "status_no_ready_models": "No inspected models are available to generate config.",
        "status_generated_config": "Generated Continue config for {count} model(s). Selected default: {model}.",
        "status_generate_before_copy": "Generate a config before copying.",
        "status_copied": "Config copied to clipboard.",
        "status_generate_before_write": "Generate a config before writing the file.",
        "status_write_failed": "Failed to write config: {error}",
        "status_written_with_backup": "Wrote config to {path} and created backup {backup}",
        "status_written": "Wrote config to {path}",
        "ollama_not_found": "Could not find `ollama` in PATH.",
        "ollama_failed": "Failed to run `ollama {args}`: {error}",
        "ollama_timeout": "`ollama {args}` timed out after {timeout} seconds.",
        "ollama_command_failed": "`ollama {args}` failed: {error}",
        "unknown_error": "Unknown error.",
        "error_prefix": "Error: {err}",
    },
    "de": {
        "app_title": "Continue-Konfigurationsgenerator",
        "language": "Sprache",
        "language_en": "Englisch",
        "language_de": "Deutsch",
        "language_zh": "Chinesisch",
        "config_name": "ollama local config",
        "input_label": "`ollama list`-Ausgabe einfügen",
        "input_hint": "NAME            ID              SIZE      MODIFIED\nllama3.2:latest abc123          2.0 GB    2 days ago",
        "output_label": "Generierte Continue-Konfiguration",
        "collapse": "Zum Einklappen klicken",
        "expand": "Zum Ausklappen klicken",
        "step1": "Schritt 1. Ollama-Liste laden",
        "step2": "Schritt 2. Modelle prüfen",
        "step3": "Schritt 3. Konfiguration erzeugen",
        "intro": "`ollama list` ausführen oder die Ausgabe einfügen, Modellnamen parsen, Modelle bei Bedarf mit `ollama show` prüfen, die sortierbare Tabelle ansehen und die Continue-YAML erst dann erzeugen.",
        "run_ollama_list": "Ollama-Liste ausführen",
        "inspect_models": "Modelle prüfen",
        "generate_config": "Konfiguration erzeugen",
        "copy_config": "Konfiguration kopieren",
        "write_config": "Nach ~/.continue/config.yaml schreiben",
        "inspected_models": "Geprüfte Modelle",
        "sort_reset": "Sortierung zurücksetzen",
        "order_reset": "Spalten zurücksetzen",
        "sorting": "Sortierung",
        "column_order": "Spaltenreihenfolge",
        "sorting_title": "Sortierung: Klicke auf eine Spaltenüberschrift, um Sortierung hinzuzufügen oder umzuschalten. Ein dritter Klick entfernt sie.",
        "column_order_title": "Spaltenreihenfolge: Ziehe die Chips, um die Tabellenreihenfolge zu ändern.",
        "column_order_hint": "Ziehe die Chips, um die Tabellenreihenfolge zu ändern.",
        "sort_state_none": "Keine aktive Sortierung",
        "sort_state_prefix": "Sortierung: {value}",
        "sort_hint": "Klicke auf eine Spaltenüberschrift, um Sortierung hinzuzufügen oder umzuschalten. Ein dritter Klick entfernt sie.",
        "col_default": "Standard",
        "col_name": "Name",
        "col_source": "Quelle",
        "col_type": "Typ",
        "col_status": "Status",
        "col_architecture": "Architektur",
        "col_parameters": "Parameter",
        "col_context": "Kontext",
        "col_embedding": "Embedding",
        "col_quantization": "Quantisierung",
        "col_roles": "Rollen",
        "col_continue_capabilities": "Continue-Fähigkeiten",
        "type_embedding_only": "nur Embedding",
        "type_normal": "normal",
        "source_local": "lokal",
        "source_cloud": "cloud",
        "status_pending": "Ausstehend",
        "status_inspecting": "Wird geprüft...",
        "status_ready": "Bereit",
        "status_error": "Fehler",
        "tooltip_select_default": "Als Standardmodell auswählen",
        "tooltip_embedding_default": "Embedding-Modelle können kein Standard sein",
        "status_embedding_default_error": "Embedding-Modelle können nicht als Standard ausgewählt werden.",
        "status_selected_default": "Standardmodell gewählt: {model}",
        "status_cleared_default": "Standardmodellauswahl gelöscht.",
        "status_inspecting_models": "{count} Modell(e) werden mit `ollama show` geprüft...",
        "status_loading_model": "Lade {index}/{count}: {model}",
        "status_loaded_metadata": "Metadaten für {count} Modell(e) geladen.{suffix} Wähle ein normales Modell in der Tabelle.",
        "status_filtered_embeddings": " {count} reine Embedding-Modelle wurden herausgefiltert.",
        "status_no_normal_models": "Metadaten wurden geladen, aber es wurden keine normalen Chat/Edit/Apply-Modelle gefunden.",
        "status_no_models_found": "Im angegebenen Text wurden keine Modellnamen gefunden.",
        "status_parsed_models": "{count} Modell(e) geparst. Prüfung startet...",
        "status_running_ollama_list": "`ollama list` wird ausgeführt...",
        "status_loaded_ollama_list": "`ollama list`-Ausgabe geladen. Klicke auf `Modelle prüfen`, um zu parsen und zu prüfen.",
        "status_select_model_first": "Prüfe zuerst die Modelle und wähle dann ein normales Modell in der Tabelle.",
        "status_selected_model_missing": "Für das ausgewählte Modell liegen noch keine geprüften Metadaten vor.",
        "status_no_ready_models": "Es sind keine geprüften Modelle zum Erzeugen der Konfiguration verfügbar.",
        "status_generated_config": "Continue-Konfiguration für {count} Modell(e) erzeugt. Gewählter Standard: {model}.",
        "status_generate_before_copy": "Erzeuge zuerst eine Konfiguration, bevor du kopierst.",
        "status_copied": "Konfiguration in die Zwischenablage kopiert.",
        "status_generate_before_write": "Erzeuge zuerst eine Konfiguration, bevor du die Datei schreibst.",
        "status_write_failed": "Konfiguration konnte nicht geschrieben werden: {error}",
        "status_written_with_backup": "Konfiguration nach {path} geschrieben und Backup {backup} erstellt",
        "status_written": "Konfiguration nach {path} geschrieben",
        "ollama_not_found": "`ollama` wurde im PATH nicht gefunden.",
        "ollama_failed": "`ollama {args}` konnte nicht ausgeführt werden: {error}",
        "ollama_timeout": "`ollama {args}` hat nach {timeout} Sekunden das Zeitlimit erreicht.",
        "ollama_command_failed": "`ollama {args}` fehlgeschlagen: {error}",
        "unknown_error": "Unbekannter Fehler.",
        "error_prefix": "Fehler: {err}",
    },
    "zh": {
        "app_title": "Continue 配置生成器",
        "language": "语言",
        "language_en": "英语",
        "language_de": "德语",
        "language_zh": "中文",
        "config_name": "ollama local config",
        "input_label": "粘贴 `ollama list` 输出",
        "input_hint": "NAME            ID              SIZE      MODIFIED\nllama3.2:latest abc123          2.0 GB    2 days ago",
        "output_label": "生成的 Continue 配置",
        "collapse": "点击折叠",
        "expand": "点击展开",
        "step1": "步骤 1：加载 Ollama 列表",
        "step2": "步骤 2：检查模型",
        "step3": "步骤 3：生成配置",
        "intro": "运行 `ollama list` 或粘贴其输出，解析模型名，按需用 `ollama show` 检查模型，查看可排序表格，然后再生成 Continue YAML。",
        "run_ollama_list": "运行 ollama list",
        "inspect_models": "检查模型",
        "generate_config": "生成配置",
        "copy_config": "复制配置",
        "write_config": "写入 ~/.continue/config.yaml",
        "inspected_models": "已检查的模型",
        "sort_reset": "重置排序",
        "order_reset": "重置列顺序",
        "sorting": "排序",
        "column_order": "列顺序",
        "sorting_title": "排序：点击列表头可添加或切换排序；第三次点击会移除该排序。",
        "column_order_title": "列顺序：拖动标签以调整表格列顺序。",
        "column_order_hint": "拖动标签以调整表格列顺序。",
        "sort_state_none": "当前没有启用排序",
        "sort_state_prefix": "排序顺序：{value}",
        "sort_hint": "点击列表头可添加或切换排序；第三次点击会移除该排序。",
        "col_default": "默认",
        "col_name": "名称",
        "col_source": "来源",
        "col_type": "类型",
        "col_status": "状态",
        "col_architecture": "架构",
        "col_parameters": "参数",
        "col_context": "上下文",
        "col_embedding": "Embedding",
        "col_quantization": "量化",
        "col_roles": "角色",
        "col_continue_capabilities": "Continue 能力",
        "type_embedding_only": "仅嵌入",
        "type_normal": "普通",
        "source_local": "本地",
        "source_cloud": "云端",
        "status_pending": "待处理",
        "status_inspecting": "检查中...",
        "status_ready": "就绪",
        "status_error": "错误",
        "tooltip_select_default": "设为默认模型",
        "tooltip_embedding_default": "Embedding 模型不能设为默认",
        "status_embedding_default_error": "Embedding 模型不能被选为默认模型。",
        "status_selected_default": "已选择默认模型：{model}",
        "status_cleared_default": "已清除默认模型选择。",
        "status_inspecting_models": "正在使用 `ollama show` 检查 {count} 个模型...",
        "status_loading_model": "正在加载 {index}/{count}: {model}",
        "status_loaded_metadata": "已加载 {count} 个模型的元数据。{suffix} 请在表格中选择一个普通模型。",
        "status_filtered_embeddings": " 已过滤掉 {count} 个仅 embedding 模型。",
        "status_no_normal_models": "已加载元数据，但没有找到可用于 chat/edit/apply 的普通模型。",
        "status_no_models_found": "在提供的文本中没有找到模型名称。",
        "status_parsed_models": "已解析 {count} 个模型，开始检查...",
        "status_running_ollama_list": "正在运行 `ollama list`...",
        "status_loaded_ollama_list": "已加载 `ollama list` 输出。点击“检查模型”开始解析和检查。",
        "status_select_model_first": "请先检查模型，然后在表格中选择一个普通模型。",
        "status_selected_model_missing": "所选模型还没有检查后的元数据。",
        "status_no_ready_models": "没有可用于生成配置的已检查模型。",
        "status_generated_config": "已为 {count} 个模型生成 Continue 配置。当前默认模型：{model}。",
        "status_generate_before_copy": "请先生成配置，再复制。",
        "status_copied": "配置已复制到剪贴板。",
        "status_generate_before_write": "请先生成配置，再写入文件。",
        "status_write_failed": "写入配置失败：{error}",
        "status_written_with_backup": "已写入配置到 {path}，并创建备份 {backup}",
        "status_written": "已写入配置到 {path}",
        "ollama_not_found": "在 PATH 中找不到 `ollama`。",
        "ollama_failed": "运行 `ollama {args}` 失败：{error}",
        "ollama_timeout": "`ollama {args}` 在 {timeout} 秒后超时。",
        "ollama_command_failed": "`ollama {args}` 失败：{error}",
        "unknown_error": "未知错误。",
        "error_prefix": "错误：{err}",
    },
}


def detect_language() -> str:
    try:
        system_locale = locale.getlocale()[0] or os.getenv("LANG", "")
    except Exception:
        system_locale = None
    if not system_locale:
        return "en"
    normalized = system_locale.lower()
    if normalized.startswith("de"):
        return "de"
    if normalized.startswith("zh"):
        return "zh"
    return "en"


def ensure_continue_dir() -> Path:
    CONTINUE_SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
    return CONTINUE_SETTINGS_DIR


def load_saved_language() -> str | None:
    try:
        ensure_continue_dir()
        if not LANGUAGE_CONFIG_PATH.exists():
            return None
        data = json.loads(LANGUAGE_CONFIG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None

    language = data.get("language")
    if language in TRANSLATIONS:
        return language
    return None


def save_language(language: str) -> None:
    ensure_continue_dir()
    LANGUAGE_CONFIG_PATH.write_text(
        json.dumps({"language": language}, indent=2),
        encoding="utf-8",
    )


@dataclass
class ModelInfo:
    name: str
    source_kind: str = "local"
    architecture: str = ""
    parameters: str = ""
    context_length: str = ""
    embedding_length: str = ""
    quantization: str = ""
    capabilities: set[str] = field(default_factory=set)
    inspection_status: str = STATUS_PENDING
    inspection_error: str = ""

    @property
    def is_embedding_only(self) -> bool:
        return "embedding" in self.capabilities and "completion" not in self.capabilities

    @property
    def continue_roles(self) -> list[str]:
        if self.is_embedding_only:
            return ["embed"]
        return ["chat", "edit", "apply"]

    @property
    def continue_capabilities(self) -> list[str]:
        items: list[str] = []
        if "tools" in self.capabilities:
            items.append("tool_use")
        if "vision" in self.capabilities:
            items.append("image_input")
        return items


def yaml_string(value: str) -> str:
    return json.dumps(value)


def display_model_name(model_name: str) -> str:
    return f"ollama local {model_name}"


def parse_sort_number(value: str) -> int:
    digits = "".join(char for char in value if char.isdigit())
    return int(digits) if digits else -1


def parse_ollama_models(output: str) -> list[str]:
    models: list[str] = []
    seen: set[str] = set()

    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        upper_line = line.upper()
        if upper_line.startswith("NAME ") or upper_line == "NAME":
            continue

        model_name = line.split()[0]
        if model_name not in seen:
            seen.add(model_name)
            models.append(model_name)

    return models


def detect_source_kind(model_name: str) -> str:
    return "cloud" if ":cloud" in model_name.lower() else "local"


def generate_continue_config(models: list[ModelInfo], selected_model_name: str) -> str:
    ordered_models = sorted(models, key=lambda model: (model.name != selected_model_name, model.name.lower()))

    lines = [
        f"name: {yaml_string(TRANSLATIONS['en']['config_name'])}",
        "version: 1.0.0",
        "schema: v1",
        "models:",
    ]

    for model in ordered_models:
        lines.extend(
            [
                f"  - name: {yaml_string(display_model_name(model.name))}",
                f"    provider: {yaml_string('ollama')}",
                f"    model: {yaml_string(model.name)}",
                "    roles:",
            ]
        )
        for role in model.continue_roles:
            lines.append(f"      - {role}")
        if not model.is_embedding_only:
            lines.append("      - autocomplete")
        if model.continue_capabilities:
            lines.append("    capabilities:")
            for capability in model.continue_capabilities:
                lines.append(f"      - {capability}")
        if model.context_length and not model.is_embedding_only:
            lines.append("    defaultCompletionOptions:")
            lines.append(f"      contextLength: {model.context_length}")
        lines.append("")

    lines.extend(
        [
            f"defaultModel: {yaml_string(display_model_name(selected_model_name))}",
            "",
            "context:",
            "  - provider: code",
            "  - provider: docs",
            "  - provider: diff",
            "  - provider: terminal",
            "  - provider: problems",
            "  - provider: folder",
            "  - provider: codebase",
        ]
    )
    return "\n".join(lines)


def parse_ollama_show(output: str, model_name: str) -> ModelInfo:
    info = ModelInfo(name=model_name, source_kind=detect_source_kind(model_name))
    current_section = ""

    for raw_line in output.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue

        indent = len(raw_line) - len(raw_line.lstrip())
        if indent <= 2:
            current_section = stripped.lower()
            continue

        if current_section == "model":
            parts = stripped.rsplit(maxsplit=1)
            if len(parts) != 2:
                continue
            key, value = parts
            normalized_key = key.replace(" ", "_").lower()
            if normalized_key == "architecture":
                info.architecture = value
            elif normalized_key == "parameters":
                info.parameters = value
            elif normalized_key == "context_length":
                info.context_length = value
            elif normalized_key == "embedding_length":
                info.embedding_length = value
            elif normalized_key == "quantization":
                info.quantization = value
        elif current_section == "capabilities":
            info.capabilities.add(stripped.lower())

    return info


async def run_ollama_command(*args: str, timeout: float = 15, translate=None) -> tuple[str | None, str | None]:
    translate = translate or (lambda key, **kwargs: TRANSLATIONS["en"][key].format(**kwargs))
    try:
        process = await asyncio.create_subprocess_exec(
            "ollama",
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
    except FileNotFoundError:
        return None, translate("ollama_not_found")
    except OSError as exc:
        return None, translate("ollama_failed", args=" ".join(args), error=exc)

    try:
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        process.kill()
        await process.communicate()
        return None, translate("ollama_timeout", args=" ".join(args), timeout=int(timeout))

    if process.returncode != 0:
        stderr_text = stderr.decode().strip() or translate("unknown_error")
        return None, translate("ollama_command_failed", args=" ".join(args), error=stderr_text)

    return stdout.decode(), None


def backup_and_write_config(config_text: str) -> tuple[Path, Path | None]:
    config_path = CONTINUE_CONFIG_PATH
    ensure_continue_dir()
    backup_path: Path | None = None

    if config_path.exists():
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_path = config_path.with_name(f"config.yaml.backup-{timestamp}")
        shutil.copy2(config_path, backup_path)

    config_path.write_text(config_text, encoding="utf-8")
    return config_path, backup_path


def main(page: ft.Page) -> None:
    current_language = load_saved_language() or detect_language()
    last_status_key = ""
    last_status_kwargs: dict[str, object] = {}
    last_status_error = False
    last_step1_progress_key = ""
    last_step1_progress_kwargs: dict[str, object] = {}
    last_progress_key = ""
    last_progress_kwargs: dict[str, object] = {}

    def t(key: str, **kwargs: object) -> str:
        template = TRANSLATIONS.get(current_language, TRANSLATIONS["en"]).get(key, TRANSLATIONS["en"].get(key, key))
        return template.format(**kwargs)

    page.title = t("app_title")
    page.window.width = 1100
    page.window.height = 900
    page.padding = 24
    page.scroll = ft.ScrollMode.AUTO
    page.theme_mode = ft.ThemeMode.LIGHT

    clipboard = ft.Clipboard()
    page.services.append(clipboard)
    parsed_model_names: list[str] = []
    model_details: dict[str, ModelInfo] = {}
    inspected_model_names: list[str] = []
    selected_model_name: str | None = None
    sort_specs: list[tuple[str, bool]] = []
    default_column_order = [
        "default",
        "name",
        "source",
        "type",
        "status",
        "architecture",
        "parameters",
        "context",
        "embedding",
        "quantization",
        "roles",
        "capabilities",
    ]
    column_order = list(default_column_order)
    busy = False
    step1_expanded = True
    step2_expanded = False
    step3_expanded = False

    intro_text = ft.Text(selectable=True)
    app_title_text = ft.Text(size=28, weight=ft.FontWeight.BOLD)
    status_text = ft.Text("", selectable=True)
    step1_progress_text = ft.Text("")
    step1_progress_bar = ft.ProgressBar(width=500, visible=False, value=0)
    progress_text = ft.Text("")
    progress_bar = ft.ProgressBar(width=500, visible=False, value=0)
    monospace_style = ft.TextStyle(font_family="Menlo")
    step1_title = ft.Text(size=18, weight=ft.FontWeight.BOLD)
    step2_title = ft.Text(size=18, weight=ft.FontWeight.BOLD)
    step3_title = ft.Text(size=18, weight=ft.FontWeight.BOLD)
    inspected_models_label = ft.Text(size=12, color=ft.Colors.ON_SURFACE_VARIANT)
    sort_state_text = ft.Text(size=12, color=ft.Colors.BLUE_GREY_700)
    sort_hint_text = ft.Text(size=12, color=ft.Colors.BLUE_GREY_500)
    column_order_label = ft.Text(size=12, color=ft.Colors.BLUE_GREY_700)
    column_order_hint_text = ft.Text(size=12, color=ft.Colors.BLUE_GREY_500)
    sorting_frame_label = ft.Text(size=12, color=ft.Colors.ON_SURFACE_VARIANT)
    column_order_frame_label = ft.Text(size=12, color=ft.Colors.ON_SURFACE_VARIANT)
    language_label = ft.Text(weight=ft.FontWeight.W_500)

    def translate_status_code(status: str) -> str:
        mapping = {
            STATUS_PENDING: "status_pending",
            STATUS_INSPECTING: "status_inspecting",
            STATUS_READY: "status_ready",
            STATUS_ERROR: "status_error",
        }
        return t(mapping.get(status, "status_pending"))

    def column_label_key(column_name: str) -> str:
        mapping = {
            "default": "col_default",
            "name": "col_name",
            "source": "col_source",
            "type": "col_type",
            "status": "col_status",
            "architecture": "col_architecture",
            "parameters": "col_parameters",
            "context": "col_context",
            "embedding": "col_embedding",
            "quantization": "col_quantization",
            "roles": "col_roles",
            "capabilities": "col_continue_capabilities",
        }
        return mapping[column_name]

    def column_label_text(column_name: str) -> str:
        base = t(column_label_key(column_name))
        for index, (sorted_column, ascending) in enumerate(sort_specs, start=1):
            if sorted_column == column_name:
                arrow = "↑" if ascending else "↓"
                return f"{base} {index}{arrow}"
        return base

    def reset_sort(_: Any = None) -> None:
        sort_specs.clear()
        refresh_table()
        refresh_config_actions()

    def cycle_sort(column_name: str) -> None:
        for index, (sorted_column, ascending) in enumerate(sort_specs):
            if sorted_column != column_name:
                continue
            if ascending:
                sort_specs[index] = (column_name, False)
            else:
                sort_specs.pop(index)
            refresh_table()
            refresh_config_actions()
            return

        sort_specs.append((column_name, True))
        refresh_table()
        refresh_config_actions()

    def build_table_columns() -> list[ft.DataColumn]:
        def sort_handler(column_name: str):
            def handler(_: Any) -> None:
                cycle_sort(column_name)

            return handler

        return [
            ft.DataColumn(
                label=ft.Text(column_label_text(column_name)),
                numeric=column_name in {"parameters", "context", "embedding"},
                on_sort=sort_handler(column_name),
            )
            for column_name in column_order
        ]

    input_field = ft.TextField(
        label=t("input_label"),
        multiline=True,
        min_lines=10,
        max_lines=16,
        expand=True,
        text_style=monospace_style,
        hint_style=monospace_style,
        hint_text=t("input_hint"),
    )

    models_table = ft.DataTable(
        columns=build_table_columns(),
        rows=[],
        sort_column_index=0,
        sort_ascending=True,
        bgcolor=ft.Colors.WHITE,
        heading_row_color=ft.Colors.BLUE_GREY_50,
        heading_row_height=52,
        heading_text_style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_900),
        data_row_min_height=44,
        column_spacing=24,
        horizontal_lines=ft.BorderSide(1, ft.Colors.BLUE_GREY_100),
    )
    column_order_list = ft.ReorderableListView(
        horizontal=True,
        build_controls_on_demand=False,
        show_default_drag_handles=False,
        height=52,
        spacing=8,
    )

    config_output = ft.TextField(
        label=t("output_label"),
        multiline=True,
        min_lines=14,
        max_lines=20,
        read_only=True,
        expand=True,
        text_style=monospace_style,
    )

    step1_body = ft.Column(controls=[], spacing=12)
    step2_body = ft.Column(controls=[], spacing=12)
    step3_body = ft.Column(controls=[], spacing=12)
    step1_indicator_icon = ft.Icon(ft.Icons.KEYBOARD_ARROW_DOWN)
    step2_indicator_icon = ft.Icon(ft.Icons.KEYBOARD_ARROW_RIGHT)
    step3_indicator_icon = ft.Icon(ft.Icons.KEYBOARD_ARROW_RIGHT)
    step1_indicator_text = ft.Text(size=12, color=ft.Colors.BLUE_700)
    step2_indicator_text = ft.Text(size=12, color=ft.Colors.AMBER_800)
    step3_indicator_text = ft.Text(size=12, color=ft.Colors.GREEN_800)

    def set_status(key: str, *, is_error: bool = False, **kwargs: object) -> None:
        nonlocal last_status_key, last_status_kwargs, last_status_error
        last_status_key = key
        last_status_kwargs = kwargs
        last_status_error = is_error
        status_text.value = t(key, **kwargs)
        status_text.color = ft.Colors.RED_700 if is_error else ft.Colors.GREEN_700
        page.update()

    def set_progress(key: str = "", **kwargs: object) -> None:
        nonlocal last_progress_key, last_progress_kwargs
        last_progress_key = key
        last_progress_kwargs = kwargs
        progress_text.value = t(key, **kwargs) if key else ""
        page.update()

    def set_step1_progress(key: str = "", *, visible: bool = False, value: float | None = None, **kwargs: object) -> None:
        nonlocal last_step1_progress_key, last_step1_progress_kwargs
        last_step1_progress_key = key
        last_step1_progress_kwargs = kwargs
        step1_progress_text.value = t(key, **kwargs) if key else ""
        step1_progress_bar.visible = visible
        if value is not None:
            step1_progress_bar.value = value
        page.update()

    def apply_translations() -> None:
        page.title = t("app_title")
        app_title_text.value = t("app_title")
        intro_text.value = t("intro")
        input_field.label = t("input_label")
        input_field.hint_text = t("input_hint")
        config_output.label = t("output_label")
        run_button.content = t("run_ollama_list")
        inspect_button.content = t("inspect_models")
        generate_button.content = t("generate_config")
        copy_button.content = t("copy_config")
        write_button.content = t("write_config")
        reset_sort_button.content = t("sort_reset")
        reset_column_order_button.content = t("order_reset")
        inspected_models_label.value = t("inspected_models")
        column_order_label.value = t("column_order")
        column_order_hint_text.value = ""
        sorting_frame_label.value = t("sorting_title")
        column_order_frame_label.value = t("column_order_title")
        sort_hint_text.value = ""
        language_label.value = t("language")
        language_menu.items = [
            ft.PopupMenuItem(t("language_en"), checked=current_language == "en", on_click=lambda _: set_language("en")),
            ft.PopupMenuItem(t("language_de"), checked=current_language == "de", on_click=lambda _: set_language("de")),
            ft.PopupMenuItem(t("language_zh"), checked=current_language == "zh", on_click=lambda _: set_language("zh")),
        ]
        if last_step1_progress_key:
            step1_progress_text.value = t(last_step1_progress_key, **last_step1_progress_kwargs)
        if last_progress_key:
            progress_text.value = t(last_progress_key, **last_progress_kwargs)
        if last_status_key:
            status_text.value = t(last_status_key, **last_status_kwargs)
            status_text.color = ft.Colors.RED_700 if last_status_error else ft.Colors.GREEN_700
        refresh_sections()
        refresh_table()
        refresh_config_actions()
        page.update()

    def refresh_sections() -> None:
        step1_body.visible = step1_expanded
        step2_body.visible = step2_expanded
        step3_body.visible = step3_expanded
        step1_indicator_text.value = t("collapse") if step1_expanded else t("expand")
        step2_indicator_text.value = t("collapse") if step2_expanded else t("expand")
        step3_indicator_text.value = t("collapse") if step3_expanded else t("expand")
        step1_indicator_icon.icon = ft.Icons.KEYBOARD_ARROW_DOWN if step1_expanded else ft.Icons.KEYBOARD_ARROW_RIGHT
        step2_indicator_icon.icon = ft.Icons.KEYBOARD_ARROW_DOWN if step2_expanded else ft.Icons.KEYBOARD_ARROW_RIGHT
        step3_indicator_icon.icon = ft.Icons.KEYBOARD_ARROW_DOWN if step3_expanded else ft.Icons.KEYBOARD_ARROW_RIGHT
        step1_indicator_icon.color = ft.Colors.BLUE_700
        step2_indicator_icon.color = ft.Colors.AMBER_800
        step3_indicator_icon.color = ft.Colors.GREEN_800
        step1_title.value = t("step1")
        step2_title.value = t("step2")
        step3_title.value = t("step3")
        page.update()

    def source_label(model: ModelInfo) -> str:
        return t("source_cloud") if model.source_kind == "cloud" else t("source_local")

    def status_sort_rank(model: ModelInfo) -> int:
        order = {
            STATUS_PENDING: 0,
            STATUS_INSPECTING: 1,
            STATUS_READY: 2,
            STATUS_ERROR: 3,
        }
        return order.get(model.inspection_status, -1)

    def update_sort_state_text() -> None:
        if not sort_specs:
            sort_state_text.value = t("sort_state_none")
            return

        parts: list[str] = []
        for index, (column_name, ascending) in enumerate(sort_specs, start=1):
            arrow = "↑" if ascending else "↓"
            parts.append(f"{index}. {t(column_label_key(column_name))} {arrow}")
        sort_state_text.value = t("sort_state_prefix", value=" | ".join(parts))

    def refresh_column_order_list() -> None:
        column_order_list.controls = [
            ft.ReorderableDragHandle(
                key=column_name,
                mouse_cursor=ft.MouseCursor.GRAB,
                content=ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text(t(column_label_key(column_name)), size=13, weight=ft.FontWeight.W_500),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    bgcolor=ft.Colors.BLUE_GREY_50,
                    border=ft.Border.all(1, ft.Colors.BLUE_GREY_200),
                    border_radius=8,
                    height=40,
                    padding=ft.Padding.symmetric(horizontal=12),
                ),
            )
            for column_name in column_order
        ]

    def set_busy_state(is_busy: bool, message: str = "") -> None:
        nonlocal busy
        busy = is_busy
        progress_bar.visible = is_busy
        progress_text.value = message
        run_button.disabled = is_busy
        inspect_button.disabled = is_busy
        generate_button.disabled = is_busy or not bool(selected_model_name)
        copy_button.disabled = is_busy or not bool(config_output.value)
        write_button.disabled = is_busy or not bool(config_output.value)
        page.update()

    def table_value(model: ModelInfo, column_name: str) -> str:
        if column_name == "default":
            return "1" if model.name == selected_model_name else "0"
        if column_name == "name":
            return model.name
        if column_name == "source":
            return source_label(model)
        if column_name == "type":
            return t("type_embedding_only") if model.is_embedding_only else t("type_normal")
        if column_name == "status":
            return translate_status_code(model.inspection_status)
        if column_name == "architecture":
            return model.architecture
        if column_name == "parameters":
            return model.parameters
        if column_name == "context":
            return model.context_length
        if column_name == "embedding":
            return model.embedding_length
        if column_name == "quantization":
            return model.quantization
        if column_name == "roles":
            return ", ".join(model.continue_roles)
        if column_name == "capabilities":
            return ", ".join(model.continue_capabilities)
        return ""

    def table_sort_key(model: ModelInfo, column_name: str):
        if column_name == "default":
            return 1 if model.name == selected_model_name else 0
        if column_name == "status":
            return status_sort_rank(model)
        if column_name == "context":
            return parse_sort_number(model.context_length)
        if column_name == "embedding":
            return parse_sort_number(model.embedding_length)
        return table_value(model, column_name).lower()

    def refresh_table() -> None:
        sorted_models = [model_details[name] for name in inspected_model_names if name in model_details]
        if sort_specs:
            for column_name, ascending in reversed(sort_specs):
                sorted_models.sort(
                    key=lambda model, current_column=column_name: table_sort_key(model, current_column),
                    reverse=not ascending,
                )

        def checkbox_handler(model_name: str):
            def handler(event: Any) -> None:
                nonlocal selected_model_name
                checked = bool(event.control.value)
                selected_model = model_details.get(model_name)
                if selected_model is None or selected_model.is_embedding_only:
                    selected_model_name = None
                    refresh_table()
                    refresh_config_actions()
                    set_status("status_embedding_default_error", is_error=True)
                    return

                selected_model_name = model_name if checked else None
                refresh_table()
                refresh_config_actions()
                if selected_model_name:
                    set_status("status_selected_default", model=selected_model_name)
                else:
                    set_status("status_cleared_default")

            return handler

        models_table.columns = build_table_columns()
        models_table.rows = [
            ft.DataRow(
                cells=[
                    (
                        ft.DataCell(
                            ft.Checkbox(
                                value=model.name == selected_model_name,
                                disabled=model.is_embedding_only or busy or model.inspection_status != STATUS_READY,
                                on_change=checkbox_handler(model.name),
                                tooltip=t("tooltip_select_default") if not model.is_embedding_only else t("tooltip_embedding_default"),
                            )
                        )
                        if column_name == "default"
                        else ft.DataCell(ft.Text(model.name))
                        if column_name == "name"
                        else ft.DataCell(ft.Text(source_label(model)))
                        if column_name == "source"
                        else ft.DataCell(ft.Text(t("type_embedding_only") if model.is_embedding_only else t("type_normal")))
                        if column_name == "type"
                        else ft.DataCell(ft.Text(translate_status_code(model.inspection_status) if not model.inspection_error else t("error_prefix", err=model.inspection_error)))
                        if column_name == "status"
                        else ft.DataCell(ft.Text(model.architecture or "-"))
                        if column_name == "architecture"
                        else ft.DataCell(ft.Text(model.parameters or "-"))
                        if column_name == "parameters"
                        else ft.DataCell(ft.Text(model.context_length or "-"))
                        if column_name == "context"
                        else ft.DataCell(ft.Text(model.embedding_length or "-"))
                        if column_name == "embedding"
                        else ft.DataCell(ft.Text(model.quantization or "-"))
                        if column_name == "quantization"
                        else ft.DataCell(ft.Text(", ".join(model.continue_roles)))
                        if column_name == "roles"
                        else ft.DataCell(ft.Text(", ".join(model.continue_capabilities) or "-"))
                    )
                    for column_name in column_order
                ]
            )
            for model in sorted_models
        ]
        models_table.sort_column_index = None
        update_sort_state_text()
        refresh_column_order_list()
        page.update()

    def refresh_config_actions() -> None:
        inspect_button.disabled = busy
        generate_button.disabled = busy or not bool(selected_model_name)
        copy_button.disabled = busy or not bool(config_output.value)
        write_button.disabled = busy or not bool(config_output.value)
        reset_sort_button.disabled = not bool(sort_specs)
        reset_column_order_button.disabled = column_order == default_column_order
        page.update()

    async def enrich_models(model_names: list[str]) -> None:
        nonlocal selected_model_name, step1_expanded, step2_expanded, step3_expanded
        selected_model_name = None
        progress_bar.value = 0
        step1_expanded = False
        step2_expanded = True
        step3_expanded = False
        refresh_sections()
        set_progress("status_inspecting_models", count=len(model_names))
        set_busy_state(True, progress_text.value)

        for index, model_name in enumerate(model_names, start=1):
            current_model = model_details[model_name]
            current_model.inspection_status = STATUS_INSPECTING
            current_model.inspection_error = ""
            set_progress("status_loading_model", index=index, count=len(model_names), model=model_name)
            progress_bar.value = (index - 1) / len(model_names)
            refresh_table()

            output, error = await run_ollama_command("show", model_name, timeout=20, translate=t)
            if error:
                current_model.inspection_status = STATUS_ERROR
                current_model.inspection_error = error
                config_output.value = ""
                refresh_table()
                set_busy_state(False)
                refresh_config_actions()
                set_status("error_prefix", is_error=True, err=error)
                return

            parsed_model = parse_ollama_show(output or "", model_name)
            parsed_model.inspection_status = STATUS_READY
            model_details[model_name] = parsed_model
            progress_bar.value = index / len(model_names)
            refresh_table()

        set_busy_state(False)
        set_progress()
        config_output.value = ""
        refresh_table()
        refresh_config_actions()

        normal_models = [info.name for info in model_details.values() if not info.is_embedding_only]
        if normal_models:
            embedding_only_count = len(model_names) - len(normal_models)
            suffix = t("status_filtered_embeddings", count=embedding_only_count) if embedding_only_count else ""
            set_status("status_loaded_metadata", count=len(model_names), suffix=suffix)
            return

        set_status("status_no_normal_models", is_error=True)

    def prepare_models_from_input() -> list[str]:
        nonlocal selected_model_name, step1_expanded, step2_expanded, step3_expanded
        models = parse_ollama_models(input_field.value or "")
        if not models:
            parsed_model_names.clear()
            model_details.clear()
            inspected_model_names.clear()
            selected_model_name = None
            config_output.value = ""
            refresh_table()
            refresh_config_actions()
            set_status("status_no_models_found", is_error=True)
            return []

        parsed_model_names[:] = models
        model_details.clear()
        inspected_model_names[:] = models
        selected_model_name = None
        config_output.value = ""
        step1_expanded = False
        step2_expanded = True
        step3_expanded = False
        for model_name in models:
            model_details[model_name] = ModelInfo(
                name=model_name,
                source_kind=detect_source_kind(model_name),
                inspection_status=STATUS_PENDING,
            )
        refresh_table()
        refresh_config_actions()
        refresh_sections()
        set_status("status_parsed_models", count=len(models))
        return models

    async def handle_run_ollama(_: Any) -> None:
        set_progress()
        progress_bar.visible = False
        set_step1_progress("status_running_ollama_list", visible=True)
        set_busy_state(True, "")
        output, error = await run_ollama_command("list", translate=t)
        if error:
            set_busy_state(False)
            set_step1_progress()
            set_status("error_prefix", is_error=True, err=error)
            return

        input_field.value = output or ""
        set_busy_state(False)
        set_step1_progress()
        page.update()
        set_status("status_loaded_ollama_list")

    def handle_inspect(_: Any) -> None:
        models = prepare_models_from_input()
        if not models:
            return

        page.run_task(enrich_models, models)

    def handle_generate(_: Any) -> None:
        nonlocal step1_expanded, step2_expanded, step3_expanded
        if not selected_model_name:
            set_status("status_select_model_first", is_error=True)
            return

        selected = model_details.get(selected_model_name)
        if selected is None:
            set_status("status_selected_model_missing", is_error=True)
            return

        ready_models = [model_details[name] for name in inspected_model_names if name in model_details and model_details[name].inspection_status == STATUS_READY]
        if not ready_models:
            set_status("status_no_ready_models", is_error=True)
            return

        config_output.value = generate_continue_config(ready_models, selected_model_name)
        step1_expanded = False
        step2_expanded = False
        step3_expanded = True
        refresh_sections()
        refresh_config_actions()
        set_status("status_generated_config", count=len(ready_models), model=selected.name)

    async def handle_copy() -> None:
        if not config_output.value:
            set_status("status_generate_before_copy", is_error=True)
            return

        await clipboard.set(config_output.value)
        set_status("status_copied")

    def handle_write(_: Any) -> None:
        if not config_output.value:
            set_status("status_generate_before_write", is_error=True)
            return

        try:
            output_path, backup_path = backup_and_write_config(config_output.value)
        except OSError as exc:
            set_status("status_write_failed", is_error=True, error=exc)
            return

        if backup_path:
            set_status("status_written_with_backup", path=output_path, backup=backup_path.name)
            return

        set_status("status_written", path=output_path)

    def set_language(lang: str) -> None:
        nonlocal current_language
        current_language = lang
        save_language(lang)
        apply_translations()

    def reset_column_order(_: Any = None) -> None:
        column_order[:] = list(default_column_order)
        refresh_table()
        refresh_config_actions()

    def handle_column_reorder(event: ft.OnReorderEvent) -> None:
        old_index = event.old_index
        new_index = event.new_index
        if old_index is None or new_index is None:
            return
        if old_index < new_index:
            new_index -= 1
        column = column_order.pop(old_index)
        column_order.insert(new_index, column)
        refresh_table()
        refresh_config_actions()

    run_button = ft.Button(t("run_ollama_list"), on_click=handle_run_ollama)
    inspect_button = ft.Button(t("inspect_models"), on_click=handle_inspect)
    generate_button = ft.FilledButton(t("generate_config"), on_click=handle_generate, disabled=True)
    def handle_copy_click(_: Any) -> None:
        _copy_task = page.run_task(handle_copy)

    copy_button = ft.Button(t("copy_config"), on_click=handle_copy_click, disabled=True)
    write_button = ft.FilledButton(t("write_config"), on_click=handle_write, disabled=True)
    reset_sort_button = ft.Button(t("sort_reset"), on_click=reset_sort, disabled=True)
    reset_column_order_button = ft.Button(t("order_reset"), on_click=reset_column_order, disabled=True)
    language_menu = ft.PopupMenuButton(
        icon=ft.Icons.LANGUAGE,
        items=[
            ft.PopupMenuItem(t("language_en"), checked=current_language == "en", on_click=lambda _: set_language("en")),
            ft.PopupMenuItem(t("language_de"), checked=current_language == "de", on_click=lambda _: set_language("de")),
            ft.PopupMenuItem(t("language_zh"), checked=current_language == "zh", on_click=lambda _: set_language("zh")),
        ],
    )
    column_order_list.on_reorder = handle_column_reorder

    def toggle_step1(_: Any) -> None:
        nonlocal step1_expanded
        step1_expanded = not step1_expanded
        refresh_sections()

    def toggle_step2(_: Any) -> None:
        nonlocal step2_expanded
        step2_expanded = not step2_expanded
        refresh_sections()

    def toggle_step3(_: Any) -> None:
        nonlocal step3_expanded
        step3_expanded = not step3_expanded
        refresh_sections()

    step1_body.controls = [
        ft.Row(
            controls=[
                run_button,
                inspect_button,
            ],
            wrap=True,
        ),
        step1_progress_text,
        step1_progress_bar,
        input_field,
    ]
    step2_body.controls = [
        progress_text,
        progress_bar,
        ft.Stack(
            controls=[
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Container(content=column_order_list, expand=True),
                                    reset_column_order_button,
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                        ],
                        spacing=0,
                    ),
                    padding=ft.Padding.only(left=12, right=12, top=18, bottom=10),
                    border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
                    border_radius=10,
                    bgcolor=ft.Colors.WHITE,
                    margin=ft.Margin.only(top=6),
                ),
                ft.Container(
                    content=column_order_frame_label,
                    left=12,
                    top=0,
                    bgcolor=ft.Colors.AMBER_50,
                    padding=ft.Padding.symmetric(horizontal=6),
                ),
            ]
        ),
        ft.Stack(
            controls=[
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Column(
                                controls=[sort_state_text],
                                spacing=2,
                                expand=True,
                            ),
                            reset_sort_button,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.Padding.only(left=12, right=12, top=18, bottom=10),
                    border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
                    border_radius=10,
                    bgcolor=ft.Colors.WHITE,
                    margin=ft.Margin.only(top=6),
                ),
                ft.Container(
                    content=sorting_frame_label,
                    left=12,
                    top=0,
                    bgcolor=ft.Colors.AMBER_50,
                    padding=ft.Padding.symmetric(horizontal=6),
                ),
            ]
        ),
        ft.Stack(
            controls=[
                ft.Container(
                    content=ft.Row(controls=[models_table], scroll=ft.ScrollMode.AUTO),
                    padding=ft.Padding.only(left=12, right=12, top=24, bottom=12),
                    border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
                    border_radius=10,
                    bgcolor=ft.Colors.WHITE,
                    margin=ft.Margin.only(top=6),
                ),
                ft.Container(
                    content=inspected_models_label,
                    left=12,
                    top=0,
                    bgcolor=ft.Colors.AMBER_50,
                    padding=ft.Padding.symmetric(horizontal=6),
                ),
            ]
        ),
        ft.Row(
            controls=[
                generate_button,
            ],
            wrap=True,
        ),
    ]
    step3_body.controls = [
        ft.Row(
            controls=[
                copy_button,
                write_button,
            ],
            wrap=True,
        ),
        config_output,
    ]

    page.add(
        ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        app_title_text,
                        ft.Row(
                            controls=[language_label, language_menu],
                            spacing=6,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                intro_text,
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Container(
                                content=ft.Row(
                                    controls=[
                                        step1_title,
                                        ft.Row(
                                            controls=[step1_indicator_text, step1_indicator_icon],
                                            spacing=4,
                                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                ),
                                on_click=toggle_step1,
                                ink=True,
                                border_radius=8,
                                padding=ft.Padding.symmetric(vertical=4, horizontal=2),
                            ),
                            step1_body,
                        ],
                        spacing=12,
                    ),
                    padding=16,
                    border=ft.Border.all(1, ft.Colors.BLUE_200),
                    border_radius=12,
                    bgcolor=ft.Colors.BLUE_50,
                ),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Container(
                                content=ft.Row(
                                    controls=[
                                        step2_title,
                                        ft.Row(
                                            controls=[step2_indicator_text, step2_indicator_icon],
                                            spacing=4,
                                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                ),
                                on_click=toggle_step2,
                                ink=True,
                                border_radius=8,
                                padding=ft.Padding.symmetric(vertical=4, horizontal=2),
                            ),
                            step2_body,
                        ],
                        spacing=12,
                    ),
                    padding=16,
                    border=ft.Border.all(1, ft.Colors.AMBER_300),
                    border_radius=12,
                    bgcolor=ft.Colors.AMBER_50,
                ),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Container(
                                content=ft.Row(
                                    controls=[
                                        step3_title,
                                        ft.Row(
                                            controls=[step3_indicator_text, step3_indicator_icon],
                                            spacing=4,
                                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                ),
                                on_click=toggle_step3,
                                ink=True,
                                border_radius=8,
                                padding=ft.Padding.symmetric(vertical=4, horizontal=2),
                            ),
                            step3_body,
                        ],
                        spacing=12,
                    ),
                    padding=16,
                    border=ft.Border.all(1, ft.Colors.GREEN_300),
                    border_radius=12,
                    bgcolor=ft.Colors.GREEN_50,
                ),
                status_text,
            ],
            tight=False,
            spacing=16,
        )
    )

    apply_translations()


if __name__ == "__main__":
    ft.run(main)
