from src.common.llm import chat_json
from src.common.browser import browser_page

print("1) Probando LLM...")
data, model = chat_json("Reply only JSON", 'Return {"ok": true}')
print("   OK ->", data, "| modelo real:", model)

print("2) Probando navegador...")
with browser_page() as page:
    page.goto("https://books.toscrape.com")
    print("   OK ->", page.title())