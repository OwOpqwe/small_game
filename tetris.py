import streamlit as st

st.set_page_config(layout="centered")
st.title("Tetris in Streamlit 🎮")

# Instructions
st.markdown("""
**Instructions:**  
- **Keyboard (desktop):**  
  - Left: `A` | Right: `D` | Soft Drop: `S` | Rotate: `W`  
  - Pause/Resume: `Space` | Restart: `R`  
- **Mobile (phone/tablet):**  
  - Use the on-screen buttons on the **sides** of the game.  

**Difficulty levels:**  
- Easy → slow blocks  
- Normal → medium speed  
- Hard → faster  
- Demon → very fast  
- Impossible → extremely fast (almost instant!)  

**Goal:** Clear lines to earn points. The game ends if blocks reach the top.
""")

# Difficulty selector
difficulty = st.selectbox("Choose Difficulty", ["Easy", "Normal", "Hard", "Demon", "Impossible"], index=1)

# Drop intervals in milliseconds
difficulty_speeds = {
    "Easy": 1000,
    "Normal": 600,
    "Hard": 300,
    "Demon": 100,
    "Impossible": 0.001  # Almost instant
}
drop_speed = difficulty_speeds[difficulty]

# Full HTML + JS code with SIDE controls
html_code = f"""
<style>
  body {{ background: #111; color: #fff; font-family: monospace; text-align: center; }}

  #game-wrapper {{
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 15px;
    margin-top: 10px;
  }}

  canvas {{
    background: #222;
    display: block;
    width: 240px;
    height: 400px;
  }}

  button {{
    margin: 6px;
    padding: 16px 20px;
    border: none;
    border-radius: 10px;
    font-size: 22px;
    cursor: pointer;
    font-weight: bold;
    color: white;
    min-width: 60px;
    min-height: 50px;
  }}
  button:active {{ transform: scale(0.9); }}

  #pauseBtn, #restartBtn {{ background: #c0392b; }} /* red */
  #btn-left, #btn-right {{ background: #2980b9; }}   /* blue */
  #btn-drop {{ background: #27ae60; }}   /* green */
  #btn-rotate {{ background: #f1c40f; color: black; }} /* yellow */

  #controls-left, #controls-right {{
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
  }}

  #scoreBoard {{ font-size: 20px; margin-bottom: 5px; }}
  #gameOver {{ display: none; color: red; font-size: 24px; margin-top: 10px; font-weight: bold; }}
</style>

<div id="scoreBoard">Score: 0 | Lines: 0</div>

<div id="game-wrapper">
  <!-- Left controls -->
  <div id="controls-left">
    <button id="btn-left" onclick="playerMove(-1)">⬅</button>
    <button id="btn-drop" onclick="playerDrop()">⬇</button>
    <button id="btn-right" onclick="playerMove(1)">➡</button>
  </div>

  <!-- Game canvas -->
  <canvas id="tetris" width="240" height="400"></canvas>

  <!-- Right controls -->
  <div id="controls-right">
    <button id="btn-rotate" onclick="playerRotate(1)">⟳</button>
    <button id="pauseBtn">⏯</button>
    <button id="restartBtn">🔄</button>
  </div>
</div>

<div id="gameOver">YOU LOSE 😵</div>

<script>
const canvas = document.getElementById('tetris');
const context = canvas.getContext('2d');
context.scale(20,20);

let paused = false;
let gameOver = false;
let score = 0;
let lines = 0;

function updateScore() {{
    document.getElementById("scoreBoard").innerText = `Score: ${{score}} | Lines: ${{lines}}`;
}}

function togglePause() {{
    if (gameOver) return;
    paused = !paused;
    document.getElementById("pauseBtn").innerText = paused ? "▶" : "⏯";
}}

function restartGame() {{
    arena.forEach(row => row.fill(0));
    resetPlayer();
    gameOver = false;
    paused = false;
    score = 0;
    lines = 0;
    updateScore();
    document.getElementById("gameOver").style.display = "none";
    document.getElementById("pauseBtn").innerText = "⏯";
}}

document.getElementById("pauseBtn").addEventListener("click", togglePause);
document.getElementById("restartBtn").addEventListener("click", restartGame);

function arenaSweep() {{
    let rowCount = 1;
    outer: for (let y = arena.length -1; y > 0; --y) {{
        for (let x = 0; x < arena[y].length; ++x) {{
            if (arena[y][x] === 0) continue outer;
        }}
        const row = arena.splice(y,1)[0].fill(0);
        arena.unshift(row);
        ++y;
        score += rowCount*10;
        lines += 1;
        rowCount *= 2;
    }}
    updateScore();
}}

function collide(arena, player) {{
    const [m, o] = [player.matrix, player.pos];
    for (let y = 0; y < m.length; ++y) {{
        for (let x = 0; x < m[y].length; ++x) {{
            if (m[y][x] !== 0 &&
                (arena[y + o.y] &&
                 arena[y + o.y][x + o.x]) !== 0) {{
                return true;
            }}
        }}
    }}
    return false;
}}

function createMatrix(w,h) {{
    const matrix = [];
    while(h--) matrix.push(new Array(w).fill(0));
    return matrix;
}}

function createPiece(type) {{
    if (type === 'T') return [[0,7,0],[7,7,7],[0,0,0]];
    if (type === 'O') return [[2,2],[2,2]];
    if (type === 'L') return [[0,0,3],[3,3,3],[0,0,0]];
    if (type === 'J') return [[4,0,0],[4,4,4],[0,0,0]];
    if (type === 'I') return [[0,0,0,0],[1,1,1,1],[0,0,0,0],[0,0,0,0]];
    if (type === 'S') return [[0,5,5],[5,5,0],[0,0,0]];
    if (type === 'Z') return [[6,6,0],[0,6,6],[0,0,0]];
}}

function drawMatrix(matrix, offset) {{
    matrix.forEach((row,y) => {{
        row.forEach((value,x) => {{
            if (value !== 0) {{
                context.fillStyle = colors[value];
                context.fillRect(x + offset.x, y + offset.y, 1,1);
            }}
        }});
    }});
}}

function draw() {{
    context.fillStyle = '#222';
    context.fillRect(0,0,canvas.width,canvas.height);

    // Draw grid
    context.strokeStyle = '#444';
    for (let x = 0; x <= 12; x++) {{
        context.beginPath();
        context.moveTo(x,0);
        context.lineTo(x,20);
        context.stroke();
    }}
    for (let y = 0; y <= 20; y++) {{
        context.beginPath();
        context.moveTo(0,y);
        context.lineTo(12,y);
        context.stroke();
    }}

    drawMatrix(arena,{{x:0,y:0}});
    drawMatrix(player.matrix,player.pos);

    if (gameOver) {{
        context.fillStyle = "rgba(0,0,0,0.6)";
        context.fillRect(0,0,canvas.width,canvas.height);
    }}
}}

function merge(arena, player) {{
    player.matrix.forEach((row,y) => {{
        row.forEach((value,x) => {{
            if (value !== 0) {{
                arena[y + player.pos.y][x + player.pos.x] = value;
            }}
        }});
    }});
}}

function playerDrop() {{
    player.pos.y++;
    if (collide(arena,player)) {{
        player.pos.y--;
        merge(arena,player);
        resetPlayer();
        arenaSweep();
    }}
    dropCounter = 0;
}}

function playerMove(dir) {{
    player.pos.x += dir;
    if (collide(arena,player)) {{
        player.pos.x -= dir;
    }}
}}

function playerRotate(dir) {{
    const pos = player.pos.x;
    let offset = 1;
    rotate(player.matrix,dir);
    while (collide(arena,player)) {{
        player.pos.x += offset;
        offset = -(offset + (offset > 0 ? 1:-1));
        if (offset > player.matrix[0].length) {{
            rotate(player.matrix,-dir);
            player.pos.x = pos;
            return;
        }}
    }}
}}

function rotate(matrix, dir) {{
    for (let y=0; y<matrix.length; ++y) {{
        for (let x=0; x<y; ++x) {{
            [matrix[x][y],matrix[y][x]] = [matrix[y][x],matrix[x][y]];
        }}
    }}
    if (dir > 0) matrix.forEach(row => row.reverse());
    else matrix.reverse();
}}

function resetPlayer() {{
    const pieces = 'ILJOTSZ';
    player.matrix = createPiece(pieces[pieces.length * Math.random() |0]);
    player.pos.y = 0;
    player.pos.x = (arena[0].length / 2 |0) - (player.matrix[0].length/2 |0);
    if (collide(arena,player)) {{
        gameOver = true;
        paused = true;
        document.getElementById("gameOver").style.display = "block";
    }}
}}

let dropCounter = 0;
let dropInterval = {drop_speed};
let lastTime = 0;

function update(time=0) {{
    const deltaTime = time - lastTime;
    lastTime = time;
    if (!paused && !gameOver) {{
        dropCounter += deltaTime;
        if (dropCounter > dropInterval) {{
            playerDrop();
        }}
    }}
    draw();
    requestAnimationFrame(update);
}}

document.addEventListener('keydown', event => {{
    if (event.code === 'Space') {{
        togglePause();
        event.preventDefault();
        return;
    }}
    if (event.key === 'r' || event.key === 'R') {{
        restartGame();
        return;
    }}
    if (paused || gameOver) return;
    if (event.key === 'a' || event.key === 'A') playerMove(-1);
    else if (event.key === 'd' || event.key === 'D') playerMove(1);
    else if (event.key === 's' || event.key === 'S') playerDrop();
    else if (event.key === 'w' || event.key === 'W') playerRotate(1);
}});

const arena = createMatrix(12,20);
const colors = [
    null,
    '#00FFFF', '#FFFF00', '#FF8C00', '#0000FF',
    '#00FF00', '#FF0000', '#800080'
];
const player = {{ pos: {{x:0,y:0}}, matrix: null }};
resetPlayer();
update();
</script>
"""

st.components.v1.html(html_code, height=600)
 
