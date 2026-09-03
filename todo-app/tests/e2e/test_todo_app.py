"""End-to-end tests for the todo app UI via Playwright."""
import re

from playwright.sync_api import Page, expect


# ---- Helpers ----
def add_todo(page: Page, title: str, description: str = "", priority: str = "medium"):
    page.fill("#todo-title", title)
    if description:
        page.fill("#todo-description", description)
    page.select_option("#todo-priority", priority)
    page.click("#add-btn")


def todo_count(page: Page) -> int:
    return page.locator(".todo-item").count()


# ---- Smoke ----
def test_page_loads(page: Page):
    expect(page).to_have_title("Todo App")
    expect(page.locator("h1")).to_have_text("Todo App")


def test_empty_state_shown(page: Page):
    expect(page.locator("#empty-state")).to_be_visible()
    expect(page.locator("#empty-state .empty-text")).to_have_text(
        "No todos yet. Add one above!"
    )


# ---- Create flow ----
def test_add_todo(page: Page):
    add_todo(page, "Buy groceries")
    expect(page.locator(".todo-item")).to_have_count(1)
    expect(page.locator(".todo-item .todo-title")).to_have_text("Buy groceries")
    expect(page.locator("#empty-state")).to_be_hidden()


def test_add_todo_with_description_and_priority(page: Page):
    add_todo(page, "Finish report", description="Q3 summary", priority="high")
    expect(page.locator(".todo-item .todo-title")).to_have_text("Finish report")
    expect(page.locator(".todo-item .todo-desc")).to_have_text("Q3 summary")
    expect(page.locator(".priority-badge")).to_have_text("high")
    expect(page.locator(".priority-badge")).to_have_class(re.compile("priority-high"))


def test_add_multiple_todos(page: Page):
    add_todo(page, "Task 1")
    add_todo(page, "Task 2")
    add_todo(page, "Task 3")
    expect(page.locator(".todo-item")).to_have_count(3)


def test_empty_title_prevented(page: Page):
    page.fill("#todo-title", "")
    page.click("#add-btn")
    expect(page.locator(".todo-item")).to_have_count(0)
    expect(page.locator("#empty-state")).to_be_visible()


# ---- Toggle / complete ----
def test_toggle_todo_marks_complete(page: Page):
    add_todo(page, "Toggle me")
    expect(page.locator(".todo-item")).not_to_have_class(re.compile("completed"))
    page.check(".todo-checkbox")
    expect(page.locator(".todo-item")).to_have_class(re.compile("completed"))
    expect(page.locator(".todo-title")).to_have_css("text-decoration-line", re.compile("line-through"))


def test_toggle_todo_back_to_active(page: Page):
    add_todo(page, "Toggle twice")
    page.check(".todo-checkbox")
    page.uncheck(".todo-checkbox")
    expect(page.locator(".todo-item")).not_to_have_class(re.compile("completed"))


# ---- Edit flow ----
def test_edit_todo(page: Page):
    add_todo(page, "Old title")
    page.click(".icon-btn[title='Edit']")
    expect(page.locator(".edit-input").first).to_be_visible()
    page.fill(".edit-input", "New title")
    page.click(".btn-sm:not(.btn-danger)")
    expect(page.locator(".todo-title")).to_have_text("New title")


def test_edit_todo_cancel(page: Page):
    add_todo(page, "Keep me")
    page.click(".icon-btn[title='Edit']")
    page.fill(".edit-input", "Changed")
    page.click("text=Cancel")
    expect(page.locator(".todo-title")).to_have_text("Keep me")


def test_edit_priority(page: Page):
    add_todo(page, "Low task", priority="low")
    expect(page.locator(".priority-badge")).to_have_text("low")
    page.click(".icon-btn[title='Edit']")
    page.select_option(".edit-input + textarea + select", "high")
    page.click(".btn-sm:not(.btn-danger)")
    expect(page.locator(".priority-badge")).to_have_text("high")


# ---- Delete flow ----
def test_delete_todo(page: Page):
    add_todo(page, "Delete me")
    page.click(".icon-btn[title='Delete']")
    expect(page.locator(".todo-item")).to_have_count(0)
    expect(page.locator("#empty-state")).to_be_visible()


def test_delete_one_of_many(page: Page):
    add_todo(page, "Keep")
    add_todo(page, "Delete")
    page.locator(".todo-item", has_text="Delete").locator(".icon-btn[title='Delete']").click()
    expect(page.locator(".todo-item")).to_have_count(1)
    expect(page.locator(".todo-title")).to_have_text("Keep")


# ---- Filters ----
def test_filter_active(page: Page):
    add_todo(page, "Active task")
    add_todo(page, "Done task")
    page.check(".todo-checkbox")
    page.click("button[data-filter='active']")
    expect(page.locator(".todo-item")).to_have_count(1)
    expect(page.locator(".todo-title")).to_have_text("Active task")


def test_filter_completed(page: Page):
    add_todo(page, "Active task")
    add_todo(page, "Done task")
    page.locator(".todo-item", has_text="Done task").locator(".todo-checkbox").check()
    page.click("button[data-filter='completed']")
    expect(page.locator(".todo-item")).to_have_count(1)
    expect(page.locator(".todo-title")).to_have_text("Done task")


def test_filter_all(page: Page):
    add_todo(page, "Active task")
    add_todo(page, "Done task")
    page.locator(".todo-item", has_text="Done task").locator(".todo-checkbox").check()
    page.click("button[data-filter='all']")
    expect(page.locator(".todo-item")).to_have_count(2)


# ---- Priority filter ----
def test_priority_filter(page: Page):
    add_todo(page, "Low", priority="low")
    add_todo(page, "High", priority="high")
    page.click("button[data-priority-filter='high']")
    expect(page.locator(".todo-item")).to_have_count(1)
    expect(page.locator(".todo-title")).to_have_text("High")


# ---- Search ----
def test_search(page: Page):
    add_todo(page, "Buy apples")
    add_todo(page, "Walk dog")
    page.fill("#search", "apple")
    expect(page.locator(".todo-item")).to_have_count(1)
    expect(page.locator(".todo-title")).to_have_text("Buy apples")


def test_search_clears(page: Page):
    add_todo(page, "Buy apples")
    add_todo(page, "Walk dog")
    page.fill("#search", "apple")
    expect(page.locator(".todo-item")).to_have_count(1)
    page.fill("#search", "")
    expect(page.locator(".todo-item")).to_have_count(2)


# ---- Clear completed ----
def test_clear_completed(page: Page):
    add_todo(page, "Active")
    add_todo(page, "Done 1")
    add_todo(page, "Done 2")
    page.locator(".todo-item", has_text="Done 1").locator(".todo-checkbox").check()
    page.locator(".todo-item", has_text="Done 2").locator(".todo-checkbox").check()
    page.click("#clear-completed")
    expect(page.locator(".todo-item")).to_have_count(1)
    expect(page.locator(".todo-title")).to_have_text("Active")


# ---- Stats ----
def test_stats_display(page: Page):
    add_todo(page, "Task A", priority="high")
    add_todo(page, "Task B", priority="low")
    expect(page.locator("#stat-total")).to_have_text("2")
    expect(page.locator("#stat-active")).to_have_text("2")
    expect(page.locator("#stat-completed")).to_have_text("0")
    expect(page.locator("#stat-high")).to_have_text("1")
    page.locator(".todo-item", has_text="Task A").locator(".todo-checkbox").check()
    expect(page.locator("#stat-completed")).to_have_text("1")
    expect(page.locator("#stat-active")).to_have_text("1")


# ---- Toast ----
def test_toast_on_add(page: Page):
    add_todo(page, "Toast test")
    expect(page.locator("#toast")).to_contain_text("Todo added!")
    expect(page.locator("#toast")).to_have_class(re.compile("show"))


def test_toast_on_delete(page: Page):
    add_todo(page, "Delete toast")
    page.click(".icon-btn[title='Delete']")
    expect(page.locator("#toast")).to_contain_text("Todo deleted")


# ---- Persistence ----
def test_persistence_across_reload(page: Page):
    add_todo(page, "Persist me")
    page.reload()
    expect(page.locator(".todo-item")).to_have_count(1)
    expect(page.locator(".todo-title")).to_have_text("Persist me")
