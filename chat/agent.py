import json
import os

from google import genai

from .tools import TOOL_DECLARATIONS, TOOL_FUNCTIONS

MODEL = "gemini-3.5-flash-lite"

SYSTEM_PROMPT = """You are an inventory assistant for a small warehouse.

You help the user check and update stock and prices by calling the tools available to you.

Rules:
- Always use a tool to answer questions about stock or price. Never guess or rely on memory.
- For a total cost or VAT question, call calculate_total with the requested quantity and VAT percentage. Use its returned numbers in your answer; do not invent a price or currency.
- If a calculated quote is not in stock, mention that plainly. A quote must not reduce stock.
- If a tool returns an error, explain the problem to the user in plain language.
- Before deleting an item entirely, make sure that is what the user meant.
- Keep your answers short and factual.
- Do not answer any question unrelated to the inventory task.
"""

MAX_STEPS = 5

def run_agent(user_message, previous_interaction_id=None, verbose=False):
    """Send a message to the agent and run tools until it produces an answer."""

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "Add your GEMINI_API_KEY to inventory/.env, then restart the server to use the AI chat.", None
    client = genai.Client(api_key=api_key)

    interaction = client.interactions.create(
        model=MODEL,
        input=user_message,
        tools=TOOL_DECLARATIONS,
        system_instruction=SYSTEM_PROMPT,
        previous_interaction_id=previous_interaction_id,
    )

    for _ in range(MAX_STEPS):
        calls = [s for s in interaction.steps if s.type == "function_call"]

        if not calls:
            return interaction.output_text, interaction.id

        results = []
        for call in calls:
            function = TOOL_FUNCTIONS[call.name]
            output = function(**call.arguments)

            if verbose:
                print(f"  -> {call.name}({call.arguments}) = {output}")

            results.append({
                "type": "function_result",
                "name": call.name,
                "call_id": call.id,
                "result": [{"type": "text", "text": json.dumps(output)}],
            })

        interaction = client.interactions.create(
            model=MODEL,
            input=results,
            tools=TOOL_DECLARATIONS,
            system_instruction=SYSTEM_PROMPT,
            previous_interaction_id=interaction.id,
        )

    return "I got stuck working on that. Please try rephrasing.", interaction.id
