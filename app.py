import streamlit as st
import streamlit.components.v1 as components

# Standard Systems Setup
st.set_page_config(page_title="Math Snake", layout="wide", initial_sidebar_state="collapsed")

with st.sidebar:
    st.title("System Menu")
    if st.button("Home"): st.session_state.logging_active = False
    if st.button("Workout"): st.session_state.logging_active = True
    if st.session_state.get('logging_active', False):
        st.warning("Workout active: Creation locked.")
    else:
        if st.button("Create New Exercise"): st.info("Opening Creator...")

# The Game Logic & Mobile-First CSS
game_html = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        * { box-sizing: border-box; }
        body { 
            margin: 0; padding: 0; 
            background: #94af10; 
            font-family: 'Courier New', monospace;
            height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: hidden; /* Prevent body scroll */
        }
        #header-ui {
            background: #849d0f; padding: 5px; 
            display: flex; justify-content: space-around; align-items: center;
            border-bottom: 2px solid #000; flex-shrink: 0;
            height: 40px;
        }
        #canvas-container {
            width: 100%;
            display: flex;
            justify-content: center;
            background: #000;
            flex-shrink: 0;
        }
        canvas { 
            background: #94af10; 
            width: 100%; 
            max-width: 360px; /* Slightly smaller for better fit */
            height: auto;
            image-rendering: pixelated;
        }
        #controls {
            flex-grow: 1;
            display: flex;
            justify-content: center;
            align-items: flex-start; /* REQ-31: Pull buttons to top of container */
            background: #94af10;
            padding-top: 10px; /* Minimal gap from canvas */
        }
        .dpad {
            display: grid;
            grid-template-columns: repeat(3, 28vw);
            grid-template-rows: repeat(2, 28vw);
            gap: 8px;
        }
        .btn {
            background: #222; color: #94af10; 
            border: 2px solid #000; border-radius: 10px;
            display: flex; align-items: center; justify-content: center; 
            font-size: 24px; user-select: none;
            box-shadow: 0 4px #000;
        }
        .btn:active { background: #444; transform: translateY(2px); box-shadow: 0 2px #000; }
        
        /* Special style for the Slow toggle in center (REQ-32) */
        .slow-btn { font-size: 14px; font-weight: bold; background: #444; }
        .slow-active { background: #000; color: #fff; border-color: #fff; }

        #up { grid-column: 2; }
        #left { grid-column: 1; grid-row: 2; }
        #slow-toggle { grid-column: 2; grid-row: 2; } /* Center spot */
        #right { grid-column: 3; grid-row: 2; }
        #down { grid-column: 2; grid-row: 3; } /* Moved down to allow center button */
    </style>
</head>
<body>
    <div id="header-ui">
        <b>SCORE:<span id="score">0</span></b>
        <div id="logic" style="font-size:16px">?</div>
        <div id="status-label" style="font-size:10px">FAST</div>
    </div>
    
    <div id="canvas-container">
        <canvas id="c" width="400" height="400"></canvas>
    </div>

    <div id="controls">
        <div class="dpad">
            <div class="btn" id="up" ontouchstart="move(0,-1)">▲</div>
            <div class="btn" id="left" ontouchstart="move(-1,0)">◀</div>
            <div class="btn slow-btn" id="slow-toggle" ontouchstart="tglSlow()">SLOW</div>
            <div class="btn" id="right" ontouchstart="move(1,0)">▶</div>
            <div class="btn" id="down" ontouchstart="move(0,1)">▼</div>
        </div>
    </div>

<script>
    const canvas = document.getElementById('c'), ctx = canvas.getContext('2d');
    const logicEl = document.getElementById('logic'), scoreEl = document.getElementById('score');
    const statusEl = document.getElementById('status-label');
    const slowBtn = document.getElementById('slow-toggle');

    let p = {x:10, y:10, dx:0, dy:0, s:'>', v:10}, body = [], food = [], score = 0, slow = false, bite = false;

    function spawn() {
        food = [];
        for(let i=0; i<3; i++) food.push({x:Math.floor(Math.random()*18+1), y:Math.floor(Math.random()*18+1), v:Math.floor(Math.random()*50)});
    }

    function tglSlow() {
        slow = !slow;
        statusEl.innerText = slow ? "SLOW" : "FAST";
        slowBtn.classList.toggle('slow-active');
        p.dx = 0; p.dy = 0; // Stop movement on toggle
    }

    window.move = (x, y) => {
        if((p.dx===-x && x!==0) || (p.dy===-y && y!==0)) return;
        p.dx=x; p.dy=y; if(slow) update();
    };

    function update() {
        if(p.dx===0 && p.dy===0) return;
        body.unshift({x:p.x, y:p.y, v:p.v});
        if(body.length > score + 1) body.pop();
        p.x+=p.dx; p.y+=p.dy;
        if(p.x<0) p.x=19; if(p.x>19) p.x=0;
        if(p.y<0) p.y=19; if(p.y>19) p.y=0;
        body.forEach(b => { if(b.x===p.x && b.y===p.y) reset(); });
        food.forEach((f,i) => {
            if(f.x===p.x && f.y===p.y) {
                let ok = (p.dx===-1||p.dy===-1) ? (p.s==='>'?f.v>p.v:f.v<p.v) : (p.s==='>'?p.v>f.v:p.v<f.v);
                if(ok) {
                    bite=true; setTimeout(()=>bite=false,300);
                    p.v=f.v; score++; scoreEl.innerText=score;
                    p.s=Math.random()>0.5?'>':'<';
                    food.splice(i,1); spawn();
                } else { reset(); }
            }
        });
        logicEl.innerText = (p.dx===-1||p.dy===-1) ? `? ${p.s} ${p.v}` : `${p.v} ${p.s} ?`;
    }

    function reset() { 
        alert("Oops! Game Reset.");
        p={x:10,y:10,dx:0,dy:0,s:'>',v:10}; body=[]; score=0; scoreEl.innerText='0'; spawn(); 
    }

    function draw() {
        ctx.fillStyle='#94af10'; ctx.fillRect(0,0,400,400);
        ctx.fillStyle='#849d0f';
        for(let i=0;i<20;i++) for(let j=0;j<20;j++) ctx.fillRect(i*20+9,j*20+9,2,2);
        ctx.fillStyle='#000'; ctx.font='bold 16px monospace';
        food.forEach(f=>ctx.fillText(f.v, f.x*20+2, f.y*20+15));
        ctx.font='12px monospace';
        body.forEach(b=>ctx.fillText(b.v, b.x*20+4, b.y*20+14));
        ctx.font='bold 22px monospace';
        ctx.fillText(bite?(p.s==='>'?'Ë':'Ё'):p.s, p.x*20, p.y*20+18);
    }

    spawn();
    setInterval(() => { if(!slow) update(); draw(); }, 220);
</script>
</body>
</html>
"""

# Reduced height to 750 to prevent excess scrolling, scrolling=True as a fallback.
components.html(game_html, height=750, scrolling=True)