import gradio as gr
import json
import random
import time
from typing import Any


# =========================================================
# DEFAULT DATA
# =========================================================

DEFAULT_EMOJIS: list[str] = ["🍎", "🍍"]

PRESETS: dict[str, list[str]] = {
    "Fruits": ["🍎", "🍍"],
    "Animals": ["🐶", "🐱", "🦊"],
    "Space": ["🌙", "⭐", "🚀", "🪐"],
    "Food": ["🍕", "🍔", "🍩", "🍟"],
    "Nature": ["🌸", "🌳", "🍄", "🌻", "🌊", "🍁"],
    "Challenge": ["🐶", "🐱", "🦊", "🐼", "🐸", "🐵", "🦁", "🐯"],
}


def create_cards(emojis: list[str]) -> list[str]:
    """Create a shuffled list of paired emoji cards."""
    cards = emojis * 2
    random.shuffle(cards)
    return cards


def new_game_id() -> str:
    """Create a unique game id so the frontend knows when to reset state."""
    return str(time.time_ns())


def compute_grid_cols(card_count: int) -> int:
    """
    Compute the number of grid columns based on total card count.

    4 cards    -> 2 columns
    6-8 cards  -> 3 columns
    10-16 cards -> 4 columns
    """
    if card_count <= 4:
        return 2

    if card_count <= 8:
        return 3

    return 4


# =========================================================
# HTML TEMPLATE
# =========================================================

HTML_TEMPLATE = """
<div class="memory-container" data-game-id="${game_id || '0'}">

    <div class="memory-header">
        <div class="memory-title">🎴 Flip Card Match</div>
        <div class="memory-subtitle">Find all matching pairs</div>
    </div>

    <div class="memory-stats">
        <div class="stat-pill">
            <span class="stat-label">Moves</span>
            <strong id="moves-count">0</strong>
        </div>

        <div class="stat-pill">
            <span class="stat-label">Matches</span>
            <strong id="matches-count">0</strong>
        </div>
    </div>

    <div
        class="memory-grid"
        id="memory-grid"
        style="--grid-cols: ${grid_cols || 2};"
    >
        ${(() => {
            let cards = [];

            try {
                cards = JSON.parse(cards_json || '[]');
            } catch (error) {
                cards = [];
            }

            let html = '';

            cards.forEach((card, i) => {
                html += `
                    <div class="memory-card" data-index="${i}" tabindex="0" role="button" aria-label="Memory card">
                        <div class="memory-inner">
                            <div class="memory-front">?</div>
                            <div class="memory-back">${card}</div>
                        </div>
                    </div>
                `;
            });

            return html;
        })()}
    </div>

    <div class="game-status ${value ? 'show' : ''}" id="game-status-area">
        <div class="status-text">
            ${value || 'Find all matching pairs!'}
        </div>
    </div>

    <button class="reset-button" id="reset-btn" type="button">
        🔄 RESET GAME
    </button>

</div>
"""


# =========================================================
# CSS TEMPLATE
# =========================================================

CSS_TEMPLATE = """
.memory-container {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 32px;
    background:
        radial-gradient(circle at top left, rgba(129, 140, 248, 0.28), transparent 35%),
        radial-gradient(circle at bottom right, rgba(244, 114, 182, 0.22), transparent 35%),
        linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    border-radius: 28px;
    position: relative;
    overflow: hidden;
    min-height: 560px;
    box-sizing: border-box;
}

.memory-container::before {
    content: "";
    position: absolute;
    inset: 0;
    background-image:
        radial-gradient(circle, rgba(255,255,255,0.13) 1px, transparent 1px);
    background-size: 28px 28px;
    opacity: 0.22;
    pointer-events: none;
}

.memory-header,
.memory-stats,
.memory-grid,
.game-status,
.reset-button {
    position: relative;
    z-index: 1;
}

.memory-header {
    text-align: center;
    margin-bottom: 18px;
}

.memory-title {
    font-size: 30px;
    font-weight: 900;
    color: #ffffff;
    letter-spacing: -0.04em;
}

.memory-subtitle {
    margin-top: 4px;
    font-size: 15px;
    color: rgba(255,255,255,0.7);
    font-weight: 600;
}

.memory-stats {
    display: flex;
    gap: 12px;
    margin-bottom: 22px;
}

.stat-pill {
    min-width: 96px;
    padding: 10px 14px;
    border-radius: 999px;
    background: rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.13);
    color: white;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    box-shadow: 0 8px 22px rgba(0,0,0,0.18);
}

.stat-label {
    font-size: 13px;
    color: rgba(255,255,255,0.72);
    font-weight: 700;
}

.stat-pill strong {
    font-size: 17px;
    color: #fef3c7;
}

.memory-grid {
    display: grid;
    grid-template-columns: repeat(var(--grid-cols, 2), 130px);
    gap: 16px;
    justify-content: center;
    max-width: 100%;
}

.memory-card {
    width: 130px;
    height: 130px;
    perspective: 1000px;
    cursor: pointer;
    position: relative;
    outline: none;
}

.memory-card:focus-visible .memory-inner {
    box-shadow: 0 0 0 4px rgba(250, 204, 21, 0.65);
    border-radius: 22px;
}

.memory-inner {
    position: relative;
    width: 100%;
    height: 100%;
    transition: transform 0.65s cubic-bezier(0.2, 0.8, 0.2, 1);
    transform-style: preserve-3d;
    will-change: transform;
}

.memory-card.flipped .memory-inner {
    transform: rotateY(180deg);
}

.memory-front,
.memory-back {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    border-radius: 22px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 48px;
    line-height: 1;
    box-shadow: 0 14px 32px rgba(0,0,0,0.35);
    backface-visibility: hidden;
    -webkit-backface-visibility: hidden;
    transform-style: preserve-3d;
    -webkit-transform-style: preserve-3d;
    user-select: none;
}

.memory-front {
    background:
        radial-gradient(circle at 30% 20%, rgba(255,255,255,0.34), transparent 26%),
        linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    color: white;
    transform: rotateY(0deg);
    border: 2px solid rgba(255,255,255,0.18);
}

.memory-back {
    background:
        radial-gradient(circle at 30% 20%, rgba(255,255,255,0.92), transparent 30%),
        linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
    color: #111827;
    transform: rotateY(180deg);
    border: 2px solid rgba(15, 23, 42, 0.08);
}

.memory-card:hover:not(.flipped):not(.matched):not(.game-won) .memory-inner {
    transform: translateY(-4px) scale(1.025);
}

.memory-card.matched {
    pointer-events: none;
}

.memory-card.matched .memory-inner {
    animation: matchedPulse 0.9s ease-in-out infinite;
}

.memory-card.matched .memory-back {
    background:
        radial-gradient(circle at 30% 20%, rgba(255,255,255,0.82), transparent 30%),
        linear-gradient(135deg, #bbf7d0 0%, #86efac 100%);
    border-color: rgba(34,197,94,0.55);
}

.memory-card.wrong .memory-inner {
    animation: wrongShake 0.38s ease-in-out;
}

.memory-container.game-complete .memory-card {
    pointer-events: none;
}

.memory-container.game-complete .memory-card.matched .memory-inner {
    animation: finalWinPulse 1.2s ease-in-out infinite;
}

@keyframes matchedPulse {
    0% {
        transform: rotateY(180deg) scale(1);
    }
    50% {
        transform: rotateY(180deg) scale(1.045);
    }
    100% {
        transform: rotateY(180deg) scale(1);
    }
}

@keyframes finalWinPulse {
    0% {
        transform: rotateY(180deg) scale(1);
    }
    50% {
        transform: rotateY(180deg) scale(1.035);
    }
    100% {
        transform: rotateY(180deg) scale(1);
    }
}

@keyframes wrongShake {
    0% {
        transform: rotateY(180deg) translateX(0);
    }
    25% {
        transform: rotateY(180deg) translateX(-8px);
    }
    50% {
        transform: rotateY(180deg) translateX(8px);
    }
    75% {
        transform: rotateY(180deg) translateX(-5px);
    }
    100% {
        transform: rotateY(180deg) translateX(0);
    }
}

.game-status {
    margin-top: 28px;
    padding: 16px 28px;
    background: rgba(255,255,255,0.08);
    border-radius: 16px;
    border: 1px solid rgba(255,255,255,0.1);
    color: white;
    transition: all 0.4s ease;
    min-width: 280px;
}

.game-status.show {
    background: rgba(34,197,94,0.15);
    border-color: rgba(34,197,94,0.35);
    box-shadow: 0 14px 36px rgba(34,197,94,0.12);
}

.status-text {
    font-size: 20px;
    font-weight: 800;
    text-align: center;
}

.reset-button {
    margin-top: 24px;
    padding: 16px 44px;
    font-size: 18px;
    font-weight: 800;
    color: white;
    background: linear-gradient(135deg, #ef4444 0%, #f97316 100%);
    border: none;
    border-radius: 999px;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 10px 30px rgba(239,68,68,0.35);
    letter-spacing: 0.04em;
}

.reset-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 14px 36px rgba(239,68,68,0.45);
}

.reset-button:active {
    transform: translateY(0);
}

@media (max-width: 720px) {
    .memory-container {
        padding: 24px 14px;
        min-height: 500px;
    }

    .memory-title {
        font-size: 24px;
    }

    .memory-grid {
        grid-template-columns: repeat(min(var(--grid-cols, 2), 3), 105px);
        gap: 12px;
    }

    .memory-card {
        width: 105px;
        height: 105px;
    }

    .memory-front,
    .memory-back {
        font-size: 38px;
        border-radius: 18px;
    }

    .status-text {
        font-size: 16px;
    }

    .game-status {
        min-width: 240px;
        padding: 14px 18px;
    }

    .reset-button {
        padding: 13px 30px;
        font-size: 15px;
    }
}

@media (max-width: 420px) {
    .memory-grid {
        grid-template-columns: repeat(2, 105px);
    }
}
"""


# =========================================================
# JS ON LOAD
# =========================================================

JS_ON_LOAD = """
let flipped = [];
let matched = [];
let moves = 0;
let isLocked = false;
let isComplete = false;
let cards = [];
let activeCardsJson = null;
let activeGameId = null;
let winEmitTimer = null;

const FLIP_ANIMATION_MS = 700;

function getRoot() {
    return element.querySelector('.memory-container');
}

function getGrid() {
    return element.querySelector('#memory-grid');
}

function getStatusEl() {
    return element.querySelector('#game-status-area');
}

function getMovesCountEl() {
    return element.querySelector('#moves-count');
}

function getMatchesCountEl() {
    return element.querySelector('#matches-count');
}

function readCardsFromProps() {
    try {
        return JSON.parse(props.cards_json || '[]');
    } catch (error) {
        return [];
    }
}

function updateStats() {
    const movesCountEl = getMovesCountEl();
    const matchesCountEl = getMatchesCountEl();

    if (movesCountEl) {
        movesCountEl.textContent = String(moves);
    }

    if (matchesCountEl) {
        matchesCountEl.textContent = String(Math.floor(matched.length / 2));
    }
}

function updateStatus(message, show) {
    const statusEl = getStatusEl();

    if (!statusEl) return;

    statusEl.innerHTML = '<div class="status-text">' + message + '</div>';

    if (show) {
        statusEl.classList.add('show');
    } else {
        statusEl.classList.remove('show');
    }
}

function getCard(index) {
    const grid = getGrid();
    if (!grid) return null;

    return grid.querySelector('[data-index="' + index + '"]');
}

function clearCardState(card) {
    if (!card) return;

    card.classList.remove('flipped');
    card.classList.remove('matched');
    card.classList.remove('wrong');
}

function clearAllCards() {
    const grid = getGrid();
    if (!grid) return;

    const allCards = grid.querySelectorAll('.memory-card');

    allCards.forEach(function(card) {
        clearCardState(card);
    });
}

function resetLocalState() {
    if (winEmitTimer) {
        clearTimeout(winEmitTimer);
        winEmitTimer = null;
    }

    flipped = [];
    matched = [];
    moves = 0;
    isLocked = false;
    isComplete = false;

    const root = getRoot();
    if (root) {
        root.classList.remove('game-complete');
    }

    clearAllCards();
    updateStats();
    updateStatus('Find all matching pairs!', false);
}

function syncFromPropsIfNeeded() {
    const nextCardsJson = props.cards_json || '[]';
    const nextGameId = props.game_id || '0';

    if (activeCardsJson !== nextCardsJson || activeGameId !== nextGameId) {
        activeCardsJson = nextCardsJson;
        activeGameId = nextGameId;
        cards = readCardsFromProps();
        resetLocalState();
    }
}

function resetGame() {
    syncFromPropsIfNeeded();
    resetLocalState();
}

function flipBack(cardA, cardB) {
    setTimeout(function() {
        if (cardA) {
            cardA.classList.remove('flipped');
            cardA.classList.remove('wrong');
        }

        if (cardB) {
            cardB.classList.remove('flipped');
            cardB.classList.remove('wrong');
        }

        flipped = [];
        isLocked = false;
    }, 900);
}

function emitWinAfterFinalFlip(winMessage) {
    if (winEmitTimer) {
        clearTimeout(winEmitTimer);
    }

    winEmitTimer = setTimeout(function() {
        props.value = winMessage;
        winEmitTimer = null;
    }, FLIP_ANIMATION_MS + 120);
}

function handleMatch(firstIndex, secondIndex, firstCard, secondCard) {
    matched.push(firstIndex, secondIndex);
    flipped = [];

    if (firstCard) {
        firstCard.classList.add('matched');
    }

    if (secondCard) {
        secondCard.classList.add('matched');
    }

    updateStats();

    if (matched.length === cards.length) {
        isComplete = true;
        isLocked = true;

        const root = getRoot();
        if (root) {
            root.classList.add('game-complete');
        }

        const winMessage = '🎉 You won in ' + moves + ' moves!';
        updateStatus(winMessage, true);

        emitWinAfterFinalFlip(winMessage);
        return;
    }

    updateStatus('✅ Match Found!', true);
    isLocked = false;
}

function handleNoMatch(firstCard, secondCard) {
    updateStatus('❌ No Match!', true);

    if (firstCard) {
        firstCard.classList.add('wrong');
    }

    if (secondCard) {
        secondCard.classList.add('wrong');
    }

    flipBack(firstCard, secondCard);
}

function handleCardClick(card) {
    syncFromPropsIfNeeded();

    if (!card) return;
    if (isLocked) return;
    if (isComplete) return;

    const index = Number(card.dataset.index);

    if (!Number.isInteger(index)) return;
    if (matched.includes(index)) return;
    if (flipped.includes(index)) return;

    card.classList.add('flipped');
    flipped.push(index);

    if (flipped.length === 1) {
        updateStatus('Keep going!', true);
        return;
    }

    isLocked = true;
    moves += 1;
    updateStats();

    const firstIndex = flipped[0];
    const secondIndex = flipped[1];

    const firstCard = getCard(firstIndex);
    const secondCard = getCard(secondIndex);

    const firstValue = cards[firstIndex];
    const secondValue = cards[secondIndex];

    if (firstValue === secondValue) {
        handleMatch(firstIndex, secondIndex, firstCard, secondCard);
    } else {
        handleNoMatch(firstCard, secondCard);
    }
}

element.addEventListener('click', function(event) {
    const resetClicked = event.target.closest('#reset-btn');

    if (resetClicked && element.contains(resetClicked)) {
        event.preventDefault();
        resetGame();
        return;
    }

    const card = event.target.closest('.memory-card');

    if (card && element.contains(card)) {
        handleCardClick(card);
    }
});

element.addEventListener('keydown', function(event) {
    if (event.key !== 'Enter' && event.key !== ' ') return;

    const card = event.target.closest('.memory-card');

    if (card && element.contains(card)) {
        event.preventDefault();
        handleCardClick(card);
    }
});

syncFromPropsIfNeeded();
"""


# =========================================================
# CUSTOM COMPONENT
# =========================================================

class FlipCard(gr.HTML):
    def __init__(
        self,
        value: str | None = None,
        emojis: list[str] | None = None,
        cards: list[str] | None = None,
        cards_json: str | None = None,
        grid_cols: int | None = None,
        game_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        if emojis is None:
            emojis = DEFAULT_EMOJIS

        if cards is None:
            cards = create_cards(emojis)

        if cards_json is None:
            cards_json = json.dumps(cards, ensure_ascii=False)

        if grid_cols is None:
            grid_cols = compute_grid_cols(len(cards))

        if game_id is None:
            game_id = new_game_id()

        super().__init__(
            value=value,
            cards_json=cards_json,
            grid_cols=grid_cols,
            game_id=game_id,
            html_template=HTML_TEMPLATE,
            css_template=CSS_TEMPLATE,
            js_on_load=JS_ON_LOAD,
            apply_default_css=False,
            container=False,
            padding=False,
            **kwargs,
        )

    def api_info(self) -> dict[str, str]:
        return {
            "type": "string",
            "description": "Winning message after completing the flip-card memory game.",
        }


# =========================================================
# UPDATE HELPER
# =========================================================

def update_flip_card(
    emojis: list[str] | None = None,
    cards: list[str] | None = None,
    value: str | None = None,
) -> gr.HTML:
    """Return a Gradio HTML update for the FlipCard component."""
    if emojis is not None:
        new_cards = create_cards(emojis)
        cards_json = json.dumps(new_cards, ensure_ascii=False)

        return gr.HTML(
            cards_json=cards_json,
            grid_cols=compute_grid_cols(len(new_cards)),
            value=value,
            game_id=new_game_id(),
        )

    if cards is not None:
        cards_json = json.dumps(cards, ensure_ascii=False)

        return gr.HTML(
            cards_json=cards_json,
            grid_cols=compute_grid_cols(len(cards)),
            value=value,
            game_id=new_game_id(),
        )

    if value is not None:
        return gr.HTML(value=value)

    return gr.HTML()