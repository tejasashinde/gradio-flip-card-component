# Flip Card Custom Component

A simple interactive memory card game in [Gradio 6](https://www.gradio.app/), built using the `gr.HTML` subclassing pattern.
Flip cards, find matching emoji pairs, and complete the game when all pairs are matched.

## Features

- Built with `gr.HTML`
- Smooth 3D flip animation
- Match and wrong-pair feedback
- Preset and custom emoji input
- Auto grid sizing up to 4×4
- Game history output

## Quick Start

```bash
pip install -r requirements.txt
python app.py
```

Then open `http://127.0.0.1:7860` in your browser.

## How It Works

The component extends `gr.HTML` using Gradio 6's custom HTML component pattern:

```python
class FlipCard(gr.HTML):
    def __init__(self, **kwargs):
        super().__init__(
            html_template=HTML_TEMPLATE,
            css_template=CSS_TEMPLATE,
            js_on_load=JS_ON_LOAD,
            **kwargs,
        )
```

The game logic runs in the browser using JavaScript, while Gradio receives the final winning message through `props.value`.

## Usage

```python
import gradio as gr
from flip_card import DEFAULT_EMOJIS, PRESETS, FlipCard, update_flip_card


def on_win(result: str | None, history: list[str] | None):
    if not result:
        return "", "", history or []

    history = (history or []) + [result]

    history_text = "\n".join(
        f"{i}. {item}"
        for i, item in enumerate(reversed(history[-10:]), start=1)
    )

    return result, history_text, history

def change_preset(name: str):
    emojis = PRESETS.get(name, DEFAULT_EMOJIS).copy()

    return (
        update_flip_card(emojis=emojis),
        emojis,
        ",".join(emojis),
        "",
    )

def parse_emojis(text: str | None):
    emojis = [item.strip() for item in (text or "").split(",") if item.strip()]
    emojis = list(dict.fromkeys(emojis))

    return emojis[:8] if len(emojis) >= 2 else DEFAULT_EMOJIS.copy()

def apply_custom(text: str | None):
    emojis = parse_emojis(text)

    return update_flip_card(emojis=emojis), emojis, ""

def new_game(emojis: list[str] | None):
    return update_flip_card(emojis=emojis or DEFAULT_EMOJIS.copy()), ""

with gr.Blocks() as demo:
    game = FlipCard()

    result = gr.Textbox(label="Result", interactive=False)
    history_box = gr.Textbox(label="Game History", lines=6, interactive=False)

    preset = gr.Dropdown(
        label="Preset",
        choices=list(PRESETS.keys()),
        value="Fruits",
    )
    custom = gr.Textbox(
        label="Custom Emojis",
        value="🍎,🍍",
        placeholder="Example: 🐶,🐱,🦊,🐼",
    )

    apply_btn = gr.Button("Apply Custom Emojis")
    new_btn = gr.Button("New Shuffled Game")
    current_emojis = gr.State(DEFAULT_EMOJIS.copy())
    history = gr.State([])

    game.change(
        fn=on_win,
        inputs=[game, history],
        outputs=[result, history_box, history],
    )
    preset.change(
        fn=change_preset,
        inputs=preset,
        outputs=[game, current_emojis, custom, result],
    )
    apply_btn.click(
        fn=apply_custom,
        inputs=custom,
        outputs=[game, current_emojis, result],
    )
    new_btn.click(
        fn=new_game,
        inputs=current_emojis,
        outputs=[game, result],
    )

demo.launch()
```

See the [Gradio Custom HTML Components Guide](https://www.gradio.app/guides/custom-HTML-components) for more details.

## LICENSE

**Apache License 2.0**. See the [LICENSE](LICENSE) file for details.
