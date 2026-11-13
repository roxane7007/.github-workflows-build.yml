import flet as ft
import json
import os

def main(page: ft.Page):
    # --- 画面全体の設定（iOS風クリーンデザイン） ---
    page.title = "マイToDoリスト"
    page.window_width = 480
    page.window_height = 750
    page.scroll = ft.ScrollMode.AUTO
    page.bgcolor = "#F2F2F7"
    page.padding = 20

    default_categories = ["やることリスト", "買うものリスト", "行きたいところ"]

    # --- Android・Mac両対応の安全な保存先決定処理 ---
    def get_data_file_path():
        # まずFletが提供するアプリ専用データ領域を確認
        app_data_dir = os.environ.get("FLET_APP_STORAGE_DATA")
        if app_data_dir and os.path.exists(app_data_dir):
            return os.path.join(app_data_dir, "my_todo_data.json")
        # 次にホームディレクトリ（Mac用）を試す
        home_dir = os.path.expanduser("~")
        if home_dir and home_dir != "/" and os.access(home_dir, os.W_OK):
            return os.path.join(home_dir, "my_todo_data.json")
        # どちらも使えない場合は現在の作業フォルダに保存
        return "my_todo_data.json"

    data_file = get_data_file_path()

    def load_tasks():
        if os.path.exists(data_file):
            try:
                with open(data_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def save_tasks():
        try:
            with open(data_file, "w", encoding="utf-8") as f:
                json.dump(tasks, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存エラー: {e}")

    tasks = load_tasks()

    saved_categories = list(default_categories)
    for t in tasks:
        if t["category"] not in saved_categories:
            saved_categories.append(t["category"])

    # --- 入力エリアのパーツ ---
    new_task = ft.TextField(
        hint_text="新しいタスクを入力...",
        expand=True,
        bgcolor="#FFFFFF",
        border_radius=12,
        border_color="#E5E5EA",
        text_size=16,
        content_padding=14
    )

    category_dropdown = ft.Dropdown(
        options=[ft.dropdown.Option(c) for c in saved_categories] + [ft.dropdown.Option("＋新しい種類を追加...")],
        value="やることリスト",
        width=200,
        bgcolor="#FFFFFF",
        border_radius=12,
        border_color="#E5E5EA",
        text_size=15
    )

    new_category_input = ft.TextField(
        hint_text="新しい種類を入力",
        visible=False,
        expand=True,
        bgcolor="#FFFFFF",
        border_radius=12,
        border_color="#E5E5EA",
        text_size=15,
        content_padding=12
    )

    tasks_view = ft.Column(spacing=12)
    completed_view = ft.Column(spacing=10)

    def update_ui():
        tasks_view.controls.clear()
        completed_view.controls.clear()

        current_categories = list(default_categories)
        for t in tasks:
            if t["category"] not in current_categories:
                current_categories.append(t["category"])

        # 【未完了リスト】
        for cat in current_categories:
            cat_tasks = [t for t in tasks if t["category"] == cat and not t["completed"]]
            if len(cat_tasks) > 0:
                card_items = [
                    ft.Text(cat, weight=ft.FontWeight.BOLD, size=18, color="#1C1C1E"),
                    ft.Divider(height=10, color="#E5E5EA")
                ]
                for task in cat_tasks:
                    card_items.append(create_task_row(task))

                tasks_view.controls.append(
                    ft.Container(
                        content=ft.Column(card_items, spacing=6),
                        bgcolor="#FFFFFF",
                        padding=16,
                        border_radius=16,
                        border=ft.Border.all(1, "#E5E5EA")
                    )
                )

        # 【完了リスト】
        completed_tasks = [t for t in tasks if t["completed"]]
        if len(completed_tasks) > 0:
            completed_items = [
                ft.Text("✅ 完了リスト", weight=ft.FontWeight.BOLD, size=17, color="#8E8E93"),
                ft.Divider(height=10, color="#E5E5EA")
            ]
            for task in completed_tasks:
                completed_items.append(create_completed_row(task))

            completed_view.controls.append(
                ft.Container(
                    content=ft.Column(completed_items, spacing=6),
                    bgcolor="#FFFFFF",
                    padding=16,
                    border_radius=16,
                    border=ft.Border.all(1, "#E5E5EA"),
                    margin=ft.Margin.only(top=10)
                )
            )

        page.update()

    def delete_task(task):
        tasks.remove(task)
        save_tasks()
        update_ui()

    def create_task_row(task):
        def checkbox_changed(e):
            task["completed"] = e.control.value
            save_tasks()
            update_ui()

        def delete_clicked(e):
            delete_task(task)

        return ft.Row([
            ft.Checkbox(
                label=task["name"],
                value=task["completed"],
                on_change=checkbox_changed,
                expand=True,
                label_style=ft.TextStyle(size=16, color="#1C1C1E")
            ),
            ft.TextButton(
                content="削除",
                on_click=delete_clicked,
                style=ft.ButtonStyle(color="#FF3B30")
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    def create_completed_row(task):
        def checkbox_changed(e):
            task["completed"] = e.control.value
            save_tasks()
            update_ui()

        def delete_clicked(e):
            delete_task(task)

        badge = ft.Container(
            content=ft.Text(task["category"], size=12, color="#636366"),
            bgcolor="#F2F2F7",
            padding=ft.Padding.symmetric(horizontal=8, vertical=3),
            border_radius=8
        )
        return ft.Row([
            ft.Checkbox(value=True, on_change=checkbox_changed),
            ft.Text(
                task["name"],
                size=15,
                style=ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH, color="#8E8E93"),
                expand=True
            ),
            badge,
            ft.TextButton(
                content="削除",
                on_click=delete_clicked,
                style=ft.ButtonStyle(color="#FF3B30")
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    def dropdown_changed(e):
        if category_dropdown.value == "＋新しい種類を追加...":
            new_category_input.visible = True
        else:
            new_category_input.visible = False
            new_category_input.value = ""
        page.update()

    category_dropdown.on_change = dropdown_changed

    def add_clicked(e):
        if new_task.value == "":
            return
        selected_cat = category_dropdown.value

        if selected_cat == "＋新しい種類を追加...":
            if new_category_input.value == "":
                return
            selected_cat = new_category_input.value
            if selected_cat not in [opt.key for opt in category_dropdown.options]:
                category_dropdown.options.insert(-1, ft.dropdown.Option(selected_cat))
            category_dropdown.value = selected_cat
            new_category_input.visible = False
            new_category_input.value = ""

        tasks.append({"name": new_task.value, "category": selected_cat, "completed": False})
        save_tasks()
        new_task.value = ""
        update_ui()

    # --- 塗りつぶしの丸い「追加」ボタン ---
    add_button = ft.Button(
        content=ft.Text("追加", size=16, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
        on_click=add_clicked,
        bgcolor="#007AFF",
        height=50,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=25)
        )
    )

    # --- 画面へのパーツ配置 ---
    page.add(
        ft.Text("📝 マイToDoリスト", size=28, weight=ft.FontWeight.BOLD, color="#1C1C1E"),
        ft.Container(height=6),
        ft.Row([category_dropdown, new_category_input], spacing=10),
        ft.Row([new_task, add_button], spacing=10),
        ft.Container(height=10),
        tasks_view,
        completed_view
    )
    update_ui()

ft.run(main)
