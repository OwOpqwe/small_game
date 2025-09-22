import streamlit as st

st.set_page_config(layout="centered")
st.title("Tetris")

st.markdown("""
**Instructions:** 
- Move Left: `A` (or swipe/drag left)  
- Move Right: `D` (or swipe/drag right)  
- Soft Drop: `S` (or drag down)  
- Rotate: `W` (or **double-tap**)  
- Pause / Resume: `Space` (or button)  
- Restart: `R` (or button)  
""")

difficulty = st.selectbox("Choose Difficulty", ["Easy", "Normal", "Hard", "Demon", "Impossible"], index=1)

difficulty_speeds = {
    "Easy": 1000,
    "Normal": 600,
    "Hard": 300,
    "Demon": 100,
    "Impossible": 0.001
}
drop_speed = difficulty_speeds[difficulty]

html_code = f"""
<style>
  body {{ background: #111; color: #fff; font-family: monospace; text-align: center; }}
  canvas {{ background: #222; display: block; margin: 10px auto; touch-action: none; }}
  button {{
    margin: 6px;
    padding: 14px 20px;
    border: none;
    border-radius: 8px;
    font-size: 18px;
    cursor: pointer;
    background: #444;
    color: white;
  }}
  button:active {{ background: #777; }}
  #sideControls {{
    display: flex;
    justify-content: center;
    gap: 10px;
    margin-top: 10px;
  }}
  #gameOver {{ display: none; color: red; font-size: 24px; margin-top: 10px; font-weight: bold; }}
  #scoreBoard {{ font-size: 20px; margin-bottom: 5px; }}
</style>

<div id="scoreBoard">Score: 0 | Lines: 0</div>
<canvas id="tetris" width="240" height="400"></canvas>
<br>
<div>
  <button id="pauseBtn">⏯ Pause</button>
  <button id="restartBtn">🔄 Restart</button>
</div>
<div id="gameOver">YOU LOSE 😵</div>

<div id="sideControls">
  <button onclick="safeRotate(1)">⟳ Rotate</button>
  <button onclick="safeMove(-1)">⬅</button>
  <button onclick="safeDrop()">⬇</button>
  <button onclick="safeMove(1)">➡</button>
</div>

<script>
const canvas = document.getElementById('tetris');
const context = canvas.getContext('2d');
context.scale(20,20);

let paused = false;
let gameOver = false;
let score = 0;
let lines = 0;
let lastActionTime = 0;
let actionDelay = 120;
let lineClearCooldown = 0;

function canAct() {{
    return lineClearCooldown <= 0 && (Date.now() - lastActionTime > actionDelay);
}}
function recordAction() {{ lastActionTime = Date.now(); }}

function safeMove(dir) {{ if(canAct()){{ playerMove(dir); recordAction(); }} }}
function safeDrop() {{ if(canAct()){{ playerDrop(); recordAction(); }} }}
function safeRotate(dir) {{ if(canAct()){{ playerRotate(dir); recordAction(); }} }}

function updateScore() {{
    document.getElementById("scoreBoard").innerText = `Score: ${{score}} | Lines: ${{lines}}`;
}}

function togglePause() {{
    if(gameOver) return;
    paused = !paused;
    document.getElementById("pauseBtn").innerText = paused ? "▶ Resume" : "⏯ Pause";
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
    document.getElementById("pauseBtn").innerText = "⏯ Pause";
}}

document.getElementById("pauseBtn").addEventListener("click", togglePause);
document.getElementById("restartBtn").addEventListener("click", restartGame);

function arenaSweep() {{
    let rowCount = 1;
    let linesCleared = 0;
    outer: for(let y = arena.length-1; y>0; --y){{
        for(let x=0; x<arena[y].length; ++x){{
            if(arena[y][x] === 0) continue outer;
        }}
        const row = arena.splice(y,1)[0].fill(0);
        arena.unshift(row);
        ++y;
        score += rowCount*10;
        lines +=1;
        rowCount *=2;
        linesCleared++;
    }}
    updateScore();
    if(linesCleared>0){{
        lineClearCooldown = 300;
        setTimeout(()=>{{ lineClearCooldown=0; }}, lineClearCooldown);
    }}
}}

function collide(arena, player){{
    const [m,o]=[player.matrix, player.pos];
    for(let y=0;y<m.length;y++){{
        for(let x=0;x<m[y].length;x++){{
            if(m[y][x]!==0 && (arena[y+o.y] && arena[y+o.y][x+o.x])!==0) return true;
        }}
    }}
    return false;
}}

function createMatrix(w,h){{ const matrix=[]; while(h--) matrix.push(new Array(w).fill(0)); return matrix; }}
function createPiece(type){{
    if(type==='T') return [[0,7,0],[7,7,7],[0,0,0]];
    if(type==='O') return [[2,2],[2,2]];
    if(type==='L') return [[0,0,3],[3,3,3],[0,0,0]];
    if(type==='J') return [[4,0,0],[4,4,4],[0,0,0]];
    if(type==='I') return [[0,0,0,0],[1,1,1,1],[0,0,0,0],[0,0,0,0]];
    if(type==='S') return [[0,5,5],[5,5,0],[0,0,0]];
    if(type==='Z') return [[6,6,0],[0,6,6],[0,0,0]];
}}

function drawMatrix(matrix, offset){{
    matrix.forEach((row,y)=>{{
        row.forEach((value,x)=>{{
            if(value!==0){{
                context.fillStyle = colors[value];
                context.fillRect(x + offset.x, y + offset.y, 1, 1);
                context.strokeStyle = 'rgba(0,0,0,0.3)';
                context.lineWidth = 0.05;
                context.strokeRect(x + offset.x, y + offset.y, 1, 1);
            }}
        }});
    }});
}}

function draw(){{
    context.fillStyle='#222';
    context.fillRect(0,0,canvas.width,canvas.height);

    // Draw grid behind blocks
    context.strokeStyle='#555';
    context.lineWidth=0.08;
    for(let x=0;x<12;x++){{
        for(let y=0;y<20;y++){{
            context.strokeRect(x, y,1,1);
        }}
    }}

    drawMatrix(arena,{{x:0,y:0}});
    drawMatrix(player.matrix,player.pos);

    if(gameOver){{
        context.fillStyle="rgba(0,0,0,0.6)";
        context.fillRect(0,0,canvas.width,canvas.height);
    }}
}}

function merge(arena, player){{
    player.matrix.forEach((row,y)=>{{
        row.forEach((value,x)=>{{
            if(value!==0) arena[y+player.pos.y][x+player.pos.x] = value;
        }});
    }});
}}

function playerDrop(){{
    player.pos.y++;
    if(collide(arena,player)){{
        player.pos.y--;
        merge(arena,player);
        resetPlayer();
        arenaSweep();
    }}
    dropCounter=0;
}}

function playerMove(dir){{
    player.pos.x += dir;
    if(collide(arena,player)) player.pos.x -= dir;
}}

function rotate(matrix, dir){{
    for(let y=0;y<matrix.length;y++){{
        for(let x=0;x<y;x++){{
            [matrix[x][y],matrix[y][x]]=[matrix[y][x],matrix[x][y]];
        }}
    }}
    if(dir>0) matrix.forEach(row=>row.reverse());
    else matrix.reverse();
}}

function playerRotate(dir){{
    const pos=player.pos.x;
    let offset=1;
    rotate(player.matrix,dir);
    while(collide(arena,player)){{
        player.pos.x+=offset;
        offset=-(offset+(offset>0?1:-1));
        if(offset>player.matrix[0].length){{
            rotate(player.matrix,-dir);
            player.pos.x=pos;
            return;
        }}
    }}
}}

function resetPlayer(){{
    const pieces='ILJOTSZ';
    player.matrix=createPiece(pieces[pieces.length*Math.random()|0]);
    player.pos.y=0;
    player.pos.x=(arena[0].length/2|0)-(player.matrix[0].length/2|0);
    if(collide(arena,player)){{
        gameOver=true;
        paused=true;
        document.getElementById("gameOver").style.display="block";
    }}
}}

let dropCounter=0;
let dropInterval={drop_speed};
let lastTime=0;

function update(time=0){{
    const deltaTime=time-lastTime;
    lastTime=time;
    if(!paused && !gameOver){{
        dropCounter+=deltaTime;
        if(dropCounter>dropInterval) playerDrop();
    }}
    draw();
    requestAnimationFrame(update);
}}

document.addEventListener('keydown', event => {{
    if(event.code==='Space'){{ togglePause(); event.preventDefault(); return; }}
    if(event.key==='r'||event.key==='R'){{ restartGame(); return; }}
    if(paused || gameOver) return;
    if(event.key==='a'||event.key==='A') safeMove(-1);
    else if(event.key==='d'||event.key==='D') safeMove(1);
    else if(event.key==='s'||event.key==='S') safeDrop();
    else if(event.key==='w'||event.key==='W') safeRotate(1);
}});

// Mobile touch + double-tap
let isDragging=false, dragStartX=0, dragStartY=0, lastTapTime=0;
canvas.addEventListener('touchstart', e=>{{ 
    isDragging=true; 
    dragStartX=e.touches[0].clientX;
    dragStartY=e.touches[0].clientY;
}}, false);

canvas.addEventListener('touchmove', e=>{{
    if(!isDragging) return;
    const currentX=e.touches[0].clientX;
    const currentY=e.touches[0].clientY;
    const dx=currentX-dragStartX;
    const dy=currentY-dragStartY;
    if(Math.abs(dx)>20){{ safeMove(dx>0?1:-1); dragStartX=currentX; }}
    if(dy>20){{ safeDrop(); dragStartY=currentY; }}
}}, false);

canvas.addEventListener('touchend', e=>{{
    isDragging=false;
    let dx=e.changedTouches[0].clientX-dragStartX;
    let dy=e.changedTouches[0].clientY-dragStartY;
    if(Math.abs(dx)<10 && Math.abs(dy)<10){{
        let currentTime=Date.now();
        if(currentTime-lastTapTime<250){{ safeRotate(1); lastTapTime=0; }}
        else lastTapTime=currentTime;
    }}
}}, false);

const arena=createMatrix(12,20);
const colors=[null,'#00FFFF','#FFFF00','#FF8C00','#0000FF','#00FF00','#FF0000','#800080'];
const player={{pos:{{x:0,y:0}},matrix:null}};
resetPlayer();
update();
</script>
"""

st.components.v1.html(html_code, height=750)
