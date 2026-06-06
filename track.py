from flask import Flask, request, render_template_string, session, redirect
import requests
import re
import traceback

app = Flask(__name__)
app.secret_key = "cyberpulse-tracker-session-key-2024"

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>CYBERPULSE TRACKER v3.7</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@600;900&display=swap');

*{margin:0;padding:0;box-sizing:border-box;}
::selection{background:#00ff41;color:#0a0a0f;}

html,body{
width:100%;
min-height:100%;
overflow-x:hidden;
background:#0a0a0f;
color:#c0ffc0;
font-family:'Share Tech Mono',monospace;
position:relative;
}

/* ===== MATRIX RAIN CANVAS ===== */
#matrix-canvas{
position:fixed;
top:0;left:0;
width:100%;height:100%;
z-index:0;
pointer-events:none;
opacity:0.25;
}

/* ===== CRT SCANLINES ===== */
body::after{
content:"";
position:fixed;
top:0;left:0;
width:100%;height:100%;
background:repeating-linear-gradient(
0deg,
rgba(0,0,0,0.15) 0px,
rgba(0,0,0,0.15) 1px,
transparent 1px,
transparent 3px
);
pointer-events:none;
z-index:999;
}

/* ===== VIGNETTE ===== */
body::before{
content:"";
position:fixed;
top:0;left:0;
width:100%;height:100%;
background:radial-gradient(ellipse at center,transparent 50%,rgba(0,0,0,0.7) 100%);
pointer-events:none;
z-index:998;
}

/* ===== GRID OVERLAY ===== */
.grid-overlay{
position:fixed;
top:0;left:0;
width:100%;height:100%;
background-image:
linear-gradient(rgba(0,255,65,0.03) 1px,transparent 1px),
linear-gradient(90deg,rgba(0,255,65,0.03) 1px,transparent 1px);
background-size:40px 40px;
pointer-events:none;
z-index:1;
}

/* ===== TERMINAL CONTAINER ===== */
.terminal{
position:relative;
z-index:10;
max-width:920px;
margin:20px auto;
padding:0 15px;
}

/* ===== TERMINAL WINDOW ===== */
.window{
background:rgba(8,12,16,0.92);
border:1px solid #00ff4133;
border-radius:6px;
box-shadow:
0 0 30px rgba(0,255,65,0.08),
inset 0 0 60px rgba(0,255,65,0.03);
margin-bottom:20px;
backdrop-filter:blur(4px);
position:relative;
overflow:hidden;
}

.window::before{
content:"";
position:absolute;
top:0;left:0;
width:100%;height:1px;
background:linear-gradient(90deg,transparent,#00ff41,transparent);
opacity:0.5;
}

/* ===== TITLE BAR ===== */
.title-bar{
display:flex;
align-items:center;
padding:10px 16px;
background:rgba(0,255,65,0.04);
border-bottom:1px solid #00ff4118;
gap:12px;
user-select:none;
}

.title-dots{display:flex;gap:6px;}
.title-dot{
width:10px;height:10px;
border-radius:50%;
border:1px solid rgba(255,255,255,0.06);
}
.title-dot.r{background:#ff0040;}
.title-dot.y{background:#ffb000;}
.title-dot.g{background:#00ff41;}

.title-text{
font-family:'Orbitron',monospace;
font-size:11px;
color:#00ff4166;
letter-spacing:3px;
text-transform:uppercase;
flex:1;
text-align:center;
}

/* ===== TERMINAL BODY ===== */
.term-body{
padding:20px;
}

/* ===== ASCII HEADER ===== */
.ascii-art{
font-size:7px;
line-height:1.1;
color:#00ff41;
text-align:center;
margin-bottom:18px;
opacity:0.7;
letter-spacing:0;
white-space:pre;
overflow:hidden;
}

/* ===== PROMPT LINE ===== */
.prompt{
display:flex;
align-items:center;
gap:8px;
margin-bottom:12px;
font-size:13px;
color:#00ff4199;
}

.prompt-symbol{color:#00ff41;font-weight:bold;}
.prompt-path{color:#00ff4188;}
.prompt-cursor{
display:inline-block;
width:8px;height:14px;
background:#00ff41;
animation:blink 0.9s step-end infinite;
}

@keyframes blink{
0%,100%{opacity:1;}
50%{opacity:0;}
}

/* ===== INPUT AREA ===== */
.input-area{
display:flex;
align-items:center;
gap:8px;
background:rgba(0,255,65,0.03);
border:1px solid #00ff4122;
border-radius:4px;
padding:4px 12px;
transition:0.3s;
}

.input-area:focus-within{
border-color:#00ff4177;
box-shadow:0 0 20px rgba(0,255,65,0.1);
}

.input-area .prompt-symbol{font-size:16px;}

.term-input{
flex:1;
background:none;
border:none;
outline:none;
color:#00ff41;
font-family:'Share Tech Mono',monospace;
font-size:15px;
letter-spacing:1px;
caret-color:#00ff41;
}

.term-input::placeholder{
color:#00ff4133;
font-size:13px;
letter-spacing:2px;
}

.term-btn{
background:none;
border:1px solid #00ff4144;
color:#00ff41;
padding:8px 18px;
font-family:'Share Tech Mono',monospace;
font-size:13px;
cursor:pointer;
border-radius:4px;
transition:0.3s;
letter-spacing:2px;
text-transform:uppercase;
}

.term-btn:hover{
background:#00ff4111;
border-color:#00ff41;
box-shadow:0 0 25px rgba(0,255,65,0.2);
text-shadow:0 0 10px #00ff41;
}

/* ===== LOADING ANIMATION ===== */
.loading{
display:none;
align-items:center;
gap:10px;
padding:10px 0;
font-size:13px;
color:#00ff4188;
}

.loading.active{display:flex;}

.loading-dots{display:flex;gap:4px;}
.loading-dot{
width:6px;height:6px;
background:#00ff41;
border-radius:50%;
animation:dotPulse 1.4s ease-in-out infinite;
}
.loading-dot:nth-child(2){animation-delay:0.2s;}
.loading-dot:nth-child(3){animation-delay:0.4s;}

@keyframes dotPulse{
0%,80%,100%{opacity:0.2;transform:scale(0.8);}
40%{opacity:1;transform:scale(1.2);}
}

/* ===== SEPARATOR ===== */
.sep{
display:flex;
align-items:center;
gap:10px;
margin:14px 0;
color:#00ff4133;
font-size:12px;
}
.sep-line{flex:1;height:1px;background:linear-gradient(90deg,transparent,#00ff4166,transparent);}

/* ===== DATA OUTPUT ===== */
.output{display:none;}

.output.active{display:block;}

.data-card{
background:rgba(0,255,65,0.02);
border:1px solid #00ff4122;
border-radius:4px;
padding:14px;
margin-bottom:12px;
position:relative;
overflow:hidden;
}

.data-card::before{
content:"";
position:absolute;
top:0;left:0;
width:3px;height:100%;
background:#00ff41;
opacity:0.4;
}

.data-card-header{
font-family:'Orbitron',monospace;
font-size:10px;
color:#00ff4166;
letter-spacing:2px;
margin-bottom:10px;
}

.data-row{
display:flex;
padding:4px 0;
border-bottom:1px solid #00ff4108;
font-size:13px;
line-height:1.6;
}

.data-row:last-child{border-bottom:none;}

.data-key{
color:#00ff4199;
min-width:100px;
flex-shrink:0;
}

.data-key .arrow{color:#00ff4166;margin-left:4px;}

.data-val{
color:#c0ffc0;
word-break:break-word;
opacity:0;
animation:typeIn 0.3s ease forwards;
}

.data-row:nth-child(1) .data-val{animation-delay:0.05s;}
.data-row:nth-child(2) .data-val{animation-delay:0.15s;}
.data-row:nth-child(3) .data-val{animation-delay:0.25s;}
.data-row:nth-child(4) .data-val{animation-delay:0.35s;}
.data-row:nth-child(5) .data-val{animation-delay:0.45s;}
.data-row:nth-child(6) .data-val{animation-delay:0.55s;}
.data-row:nth-child(7) .data-val{animation-delay:0.65s;}

@keyframes typeIn{
from{opacity:0;transform:translateX(-8px);filter:blur(4px);}
to{opacity:1;transform:translateX(0);filter:blur(0);}
}

.data-val.aadhaar{
color:#ff0040;
text-shadow:0 0 10px rgba(255,0,64,0.4);
font-weight:bold;
letter-spacing:2px;
}

.data-val.highlight{
color:#00ff41;
text-shadow:0 0 8px rgba(0,255,65,0.5);
}

/* ===== MAP ===== */
.map-wrap{
margin-top:12px;
border:1px solid #00ff4122;
border-radius:4px;
overflow:hidden;
position:relative;
}

#map{
height:260px;
z-index:1;
}

.map-overlay{
position:absolute;
top:8px;left:8px;
z-index:1000;
font-family:'Orbitron',monospace;
font-size:9px;
color:#00ff4166;
letter-spacing:1px;
background:rgba(0,0,0,0.7);
padding:4px 10px;
border-radius:2px;
border:1px solid #00ff4118;
pointer-events:none;
}

#distance{
text-align:center;
padding:10px;
font-family:'Orbitron',monospace;
font-size:13px;
color:#00ff41;
letter-spacing:1px;
}

/* ===== DATA + REPORT ROW ===== */
.data-report-row{
display:flex;
gap:14px;
margin-top:12px;
}

.data-report-col{
flex:1;
min-width:0;
}

.data-report-col.data-col{
max-width:480px;
flex:1.2;
}

.data-report-col.report-col{
flex:2;
}

@media(max-width:960px){
.data-report-row{flex-direction:column;}
.data-report-col.data-col{max-width:none;}
}

/* ===== REPORT TOGGLE BUTTON ===== */
.report-toggle-btn{
width:100%;
background:none;
border:1px solid #ff004044;
color:#ff0040;
padding:12px 16px;
font-family:'Share Tech Mono',monospace;
font-size:13px;
cursor:pointer;
border-radius:4px;
transition:0.3s;
letter-spacing:2px;
text-transform:uppercase;
text-align:center;
}

.report-toggle-btn:hover{
background:#ff004011;
border-color:#ff0040;
box-shadow:0 0 25px rgba(255,0,64,0.2);
text-shadow:0 0 10px #ff0040;
}

.report-toggle-btn.active{
border-color:#00ff41;
color:#00ff41;
background:rgba(0,255,65,0.04);
}

/* ===== REPORT SECTION ===== */
.report-wrap{
margin-top:12px;
border:1px solid #ff004044;
border-radius:4px;
overflow:hidden;
position:relative;
background:rgba(255,0,64,0.03);
}

.report-wrap::before{
content:"";
position:absolute;
top:0;left:0;
width:100%;height:2px;
background:linear-gradient(90deg,transparent,#ff0040,transparent);
animation:reportScan 2s ease-in-out infinite;
}

@keyframes reportScan{
0%,100%{opacity:0.3;}
50%{opacity:1;}
}

.report-header{
display:flex;
align-items:center;
gap:10px;
padding:10px 14px;
background:rgba(255,0,64,0.06);
border-bottom:1px solid #ff004022;
font-family:'Orbitron',monospace;
font-size:11px;
color:#ff0040;
letter-spacing:2px;
}

.report-icon{
font-size:16px;
animation:pulse 1.5s ease-in-out infinite;
}

@keyframes pulse{
0%,100%{opacity:0.6;transform:scale(1);}
50%{opacity:1;transform:scale(1.1);}
}

.report-body{padding:14px;}

.report-desc{
font-size:11px;
color:#ff004088;
line-height:1.6;
margin-bottom:12px;
padding:8px 10px;
border-left:2px solid #ff004044;
background:rgba(255,0,64,0.04);
}

.report-textarea{
width:100%;
min-height:220px;
background:rgba(0,0,0,0.5);
border:1px solid #ff004022;
border-radius:3px;
color:#ff8080;
font-family:'Share Tech Mono',monospace;
font-size:12px;
line-height:1.7;
padding:12px;
resize:vertical;
outline:none;
transition:0.3s;
}

.report-textarea:focus{
border-color:#ff004066;
box-shadow:0 0 15px rgba(255,0,64,0.1);
}

.report-actions{
display:flex;
gap:8px;
margin-top:10px;
flex-wrap:wrap;
}

.report-btn{
flex:1;
min-width:120px;
background:none;
border:1px solid #ff004044;
color:#ff0040;
padding:10px 16px;
font-family:'Share Tech Mono',monospace;
font-size:12px;
cursor:pointer;
border-radius:3px;
transition:0.3s;
letter-spacing:1px;
text-transform:uppercase;
text-align:center;
}

.report-btn:hover{
background:#ff004011;
border-color:#ff0040;
box-shadow:0 0 20px rgba(255,0,64,0.15);
text-shadow:0 0 8px #ff0040;
}

.report-btn.copied{
border-color:#00ff41;
color:#00ff41;
}

.report-links{
margin-top:12px;
padding:10px 12px;
background:rgba(0,0,0,0.3);
border:1px solid #ff004015;
border-radius:3px;
}

.report-links-title{
font-family:'Orbitron',monospace;
font-size:9px;
color:#ff004066;
letter-spacing:2px;
margin-bottom:8px;
}

.report-link-grid{
display:grid;
grid-template-columns:1fr 1fr;
gap:6px;
}

.report-link{
display:flex;
align-items:center;
gap:6px;
padding:6px 10px;
background:rgba(255,0,64,0.04);
border:1px solid #ff004015;
border-radius:2px;
color:#ff8080;
font-size:11px;
text-decoration:none;
transition:0.3s;
font-family:'Share Tech Mono',monospace;
}

.report-link:hover{
background:#ff004011;
border-color:#ff004033;
color:#ff0040;
}

.link-arrow{color:#ff004033;font-family:monospace;}

@media(max-width:600px){
.report-link-grid{grid-template-columns:1fr;}
.report-btn{min-width:100%;}
}

/* ===== STATUS BAR ===== */
.status-bar{
display:flex;
justify-content:space-between;
padding:8px 16px;
background:rgba(0,255,65,0.03);
border-top:1px solid #00ff4118;
font-size:10px;
color:#00ff4144;
font-family:'Orbitron',monospace;
letter-spacing:1px;
}

.status-bar .blink{
display:inline-block;
width:6px;height:6px;
background:#00ff41;
border-radius:50%;
margin-right:6px;
animation:blink 1s step-end infinite;
vertical-align:middle;
}

/* ===== GLITCH TEXT ===== */
.glitch{
font-family:'Orbitron',monospace;
font-size:13px;
font-weight:900;
color:#00ff41;
letter-spacing:4px;
text-transform:uppercase;
position:relative;
display:inline-block;
}

.glitch::before,.glitch::after{
content:attr(data-text);
position:absolute;
top:0;left:0;
width:100%;height:100%;
opacity:0;
}

.glitch:hover::before{
opacity:0.7;
color:#ff0040;
z-index:-1;
animation:glitch1 0.3s ease;
}

.glitch:hover::after{
opacity:0.7;
color:#0ff;
z-index:-2;
animation:glitch2 0.3s ease;
}

@keyframes glitch1{
0%{transform:translate(0);}
20%{transform:translate(-2px,2px);}
40%{transform:translate(2px,-1px);}
60%{transform:translate(-1px,3px);}
80%{transform:translate(1px,-2px);}
100%{transform:translate(0);}
}

@keyframes glitch2{
0%{transform:translate(0);}
20%{transform:translate(2px,-2px);}
40%{transform:translate(-2px,1px);}
60%{transform:translate(1px,-3px);}
80%{transform:translate(-1px,2px);}
100%{transform:translate(0);}
}

/* ===== FOOTER ===== */
.term-footer{
text-align:center;
padding:10px;
font-size:10px;
color:#00ff4133;
font-family:'Orbitron',monospace;
letter-spacing:2px;
}

/* ===== RESPONSIVE ===== */
@media(max-width:600px){
.terminal{margin:10px auto;padding:0 8px;}
.term-body{padding:12px;}
.ascii-art{font-size:5px;}
.data-key{min-width:70px;font-size:12px;}
.data-val{font-size:12px;}
.title-text{font-size:9px;}
}
</style>
</head>
<body>

<canvas id="matrix-canvas"></canvas>
<div class="grid-overlay"></div>

<div class="terminal">

<div class="window">
<div class="title-bar">
<div class="title-dots">
<div class="title-dot r"></div>
<div class="title-dot y"></div>
<div class="title-dot g"></div>
</div>
<div class="title-text">CYBERPULSE_TRACKER // v3.7.1</div>
<div class="title-dots">
<div style="color:#00ff4133;font-size:9px;">&#x25B2;</div>
</div>
</div>

<div class="term-body">

<div class="ascii-art">
   _____ ____  _____  ______  _    _ _____   _____  ____  _  __
  / ____/ __ \\|  __ \\|  ____| |  | |  __ \\ / ____|/ __ \\| |/ /
 | |   | |  | | |__) | |__    |  | | |__) | |   | |  | | ' /
 | |   | |  | |  _  /|  __|   |  | |  _  /| |   | |  | |  &lt;
 | |___| |__| | | \\ \\| |____  |__| | | \\ \\| |___| |__| | . \\
  \\_____\\____/|_|  \\_\\______|\\____/|_|  \\_\\\\_____|\\____/|_|\\_\\\\
</div>

<form method="POST" id="track-form">
<div class="prompt">
<span class="prompt-symbol">></span>
<span class="prompt-path">/home/cyberpulse/tracker</span>
</div>

<div class="input-area">
<span class="prompt-symbol">#</span>
<input class="term-input" type="text" name="number" placeholder="ENTER_TARGET_NUMBER" required>
<button class="term-btn" type="submit">[ EXEC ]</button>
</div>
</form>

<div class="loading" id="loading">
<span>INITIALIZING QUERY</span>
<div class="loading-dots">
<div class="loading-dot"></div>
<div class="loading-dot"></div>
<div class="loading-dot"></div>
</div>
</div>

{% if data %}
<div class="data-report-row">

<div class="data-report-col data-col">
<div class="sep"><span class="sep-line"></span><span>DECRYPTED PAYLOAD</span><span class="sep-line"></span></div>

<div class="output active" id="output">
{% for entry in data %}
<div class="data-card">
<div class="data-card-header">
<span class="glitch" data-text="RECORD_{{loop.index}}">RECORD_{{loop.index}}</span>
<span style="float:right;color:#00ff4133;font-size:10px;">0x{{'%04x' % loop.index}}</span>
</div>

<div class="data-row">
<span class="data-key">NAME <span class="arrow">~</span></span>
<span class="data-val highlight">{{entry.name or "N/A"}}</span>
</div>

{% if entry.father_name %}
<div class="data-row">
<span class="data-key">FATHER <span class="arrow">~</span></span>
<span class="data-val">{{entry.father_name}}</span>
</div>
{% endif %}

<div class="data-row">
<span class="data-key">MOBILE <span class="arrow">~</span></span>
<span class="data-val highlight">{{entry.mobile or "N/A"}}</span>
</div>

{% if entry.address %}
<div class="data-row">
<span class="data-key">ADDRESS <span class="arrow">~</span></span>
<span class="data-val" {% if loop.first %}id="addr"{% endif %}>{{entry.address}}</span>
</div>
{% endif %}

{% if entry.circle %}
<div class="data-row">
<span class="data-key">CIRCLE <span class="arrow">~</span></span>
<span class="data-val">{{entry.circle}}</span>
</div>
{% endif %}

{% if entry.alternate %}
<div class="data-row">
<span class="data-key">ALT_NUM <span class="arrow">~</span></span>
<span class="data-val">{{entry.alternate}}</span>
</div>
{% endif %}

{% if entry.aadhaar %}
<div class="data-row">
<span class="data-key">AADHAAR <span class="arrow">~</span></span>
<span class="data-val aadhaar">{{entry.aadhaar}}</span>
</div>
{% endif %}
</div>
{% endfor %}
</div>

<div style="margin-top:10px;">
<button class="report-toggle-btn" id="report-toggle" type="button">[ &#x26A0; REPORT THIS LEAK ]</button>
</div>

</div>

<div class="data-report-col report-col" id="report-col" style="display:none;">
<div class="report-wrap" id="report-section">
<div class="report-header">
<span class="report-icon">&#x26A0;</span>
<span>BREACH REPORT // NOTIFY AUTHORITIES</span>
</div>
<div class="report-body">
<div class="report-desc">
The data above was retrieved from an unauthorized API selling leaked Aadhaar and telecom records. 
Report this breach to the appropriate authorities using the template below.
</div>
<textarea class="report-textarea" id="report-body" readonly>=== DATA BREACH REPORT ===

To whom it may concern,

I am reporting a serious violation of data privacy laws. 
My personal information is being distributed and sold through an
unauthorized API without my consent.

=== MY LEAKED DATA ===

Name: {{data[0].name}}
Phone: {{data[0].mobile}}
Address: {{data[0].address}}
{% if data[0].aadhaar %}Aadhaar: {{data[0].aadhaar}}{% endif %}
{% if data[0].father_name %}Father Name: {{data[0].father_name}}{% endif %}
Telecom Circle: {{data[0].circle}}

=== SOURCE DETAILS ===

API Endpoint: https://exploitsindia.site/track/live.php
Domain Registrar: Unknown (exploitsindia.site)
Seller Contact: @Cyb3rS0ldier (Telegram)
Service Type: Paid API returning name, address, father name, 
             alternate numbers, and full Aadhaar numbers 
             for any Indian mobile number

=== VIOLATIONS ===

1. Aadhaar Act 2016 — Section 28, 29 (unauthorized disclosure of Aadhaar)
2. IT Act 2000 — Section 43A (data breach), Section 66E (privacy violation)
3. Digital Personal Data Protection Act 2023 — unauthorized processing of personal data

=== REQUESTED ACTION ===

Please investigate this service and its operator, and 
take immediate action to:
- Take down the API endpoint
- Block the domain exploitsindia.site
- Initiate legal proceedings against the operator
- Investigate the source of the data leak

Thank you.
---
Generated via Cyberpulse Tracker</textarea>

<div class="report-actions">
<button class="report-btn" id="copy-btn">[ COPY TO CLIPBOARD ]</button>
<button class="report-btn" id="mail-btn">[ OPEN IN EMAIL ]</button>
</div>

<div class="report-links">
<div class="report-links-title">// REPORT PORTALS</div>
<div class="report-link-grid">
<a class="report-link" href="https://cybercrime.gov.in/Webform/Crime_AuthoLogin.aspx" target="_blank" rel="noopener">
<span class="link-arrow">&gt;</span> File Complaint (Cybercrime) <span style="margin-left:auto;color:#ff004033;">&#x2197;</span>
</a>
<a class="report-link" href="https://abuse.cloudflare.com" target="_blank" rel="noopener">
<span class="link-arrow">&gt;</span> Cloudflare Abuse <span style="margin-left:auto;color:#ff004033;">&#x2197;</span>
</a>
</div>
</div>
</div>
</div>
</div>
</div>

<div class="map-wrap">
<div class="map-overlay">[ GEOLOCALIZATION ]</div>
<div id="map"></div>
<div id="distance"></div>
</div>
{% endif %}

</div>

<div class="status-bar">
<span><span class="blink"></span>SYS.ONLINE</span>
<span>NODES: 8</span>
<span>SEC: TLS_1.3</span>
<span>00:00:00</span>
</div>

</div>

<div class="term-footer">[ CYBERPULSE TRACKER // UNAUTHORIZED ACCESS IS PUNISHABLE BY LAW ]</div>

</div>

{% if data %}
<script>
// ---- MATRIX RAIN ----
const c = document.getElementById('matrix-canvas');
const ctx = c.getContext('2d');
let W, H, cols, drops;

function resizeMatrix(){
W = c.width = window.innerWidth;
H = c.height = window.innerHeight;
cols = Math.floor(W / 14);
drops = Array(cols).fill(1);
}
resizeMatrix();
window.addEventListener('resize', resizeMatrix);

const chars = 'アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン0123456789ABCDEF<>/{}[]|&^%$#@!';

function drawMatrix(){
ctx.fillStyle = 'rgba(10,10,15,0.05)';
ctx.fillRect(0,0,W,H);
ctx.font = '14px monospace';
for(let i=0;i<drops.length;i++){
const char = chars[Math.floor(Math.random()*chars.length)];
ctx.fillStyle = Math.random()>0.98?'#c0ffc0':'#00ff41';
ctx.fillText(char,i*14,drops[i]*14);
drops[i]++;
if(drops[i]*14>H||Math.random()>0.95)drops[i]=0;
}
}
setInterval(drawMatrix,50);

// ---- MAP ----
const map = L.map('map').setView([20.59,78.96],5);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{
attribution:''
}).addTo(map);

const addrEl = document.getElementById('addr');
if(addrEl){
const address = addrEl.innerText.trim();
const distEl = document.getElementById('distance');

async function geocode(query){
const r=await fetch('https://nominatim.openstreetmap.org/search?format=json&q='+encodeURIComponent(query)+'&countrycodes=in&limit=1');
const d=await r.json();
return d.length>0?d[0]:null;
}

async function locateTarget(){
const full = await geocode(address);
if(full) return full;

const pin = address.match(/\\b\\d{6}\\b/);
if(pin){const r=await geocode(pin[0]);if(r)return r;}

const parts = address.split(/[,\\s]+/).filter(Boolean);
if(parts.length>3){
const fallback = parts.slice(-3).join(' ');
const r = await geocode(fallback);
if(r) return r;
}
return null;
}

navigator.geolocation.getCurrentPosition(function(pos){
const userLat = pos.coords.latitude;
const userLng = pos.coords.longitude;
const userMarker = L.marker([userLat,userLng]).addTo(map);
userMarker.bindPopup('<span style="color:#00ff41;font-family:monospace;">◉ YOU</span>');
L.circle([userLat,userLng],{radius:pos.coords.accuracy||100,color:'#00ff4144',fillColor:'#00ff41',fillOpacity:0.05}).addTo(map);

locateTarget().then(target=>{
if(target){
const lat=parseFloat(target.lat),lon=parseFloat(target.lon);
const tgt = L.marker([lat,lon]).addTo(map);
tgt.bindPopup('<span style="color:#ff0040;font-family:monospace;">◉ TARGET</span>');
L.circle([lat,lon],{radius:500,color:'#ff004044',fillColor:'#ff0040',fillOpacity:0.05,dashArray:'4,4'}).addTo(map);
L.polyline([[userLat,userLng],[lat,lon]],{
color:'#00ff41',weight:2,opacity:0.6,dashArray:'8,8'
}).addTo(map);
map.fitBounds([[userLat,userLng],[lat,lon]],{padding:[40,40]});

const R=6371;
const dLat=(lat-userLat)*Math.PI/180;
const dLon=(lon-userLng)*Math.PI/180;
const a=Math.sin(dLat/2)**2+Math.cos(userLat*Math.PI/180)*Math.cos(lat*Math.PI/180)*Math.sin(dLon/2)**2;
const km=R*2*Math.atan2(Math.sqrt(a),Math.sqrt(1-a));
if(distEl)distEl.innerHTML='DISTANCE: '+km.toFixed(2)+' KM | ACCURACY: ±'+(pos.coords.accuracy||'?')+'m';
} else {
if(distEl)distEl.innerHTML='⚠ COULD NOT GEOCODE ADDRESS — TRY MANUAL SEARCH';
map.setView([userLat,userLng],12);
L.marker([userLat,userLng]).addTo(map).bindPopup('YOU');
}
});
}, function(err){
distEl.innerHTML='⚠ LOCATION ERROR: '+err.message;
},{enableHighAccuracy:true,timeout:10000});
}

// ---- TOGGLE REPORT ----
const toggleBtn = document.getElementById('report-toggle');
const reportCol = document.getElementById('report-col');

if(toggleBtn && reportCol){
toggleBtn.addEventListener('click',function(){
const hidden = reportCol.style.display === 'none';
reportCol.style.display = hidden ? 'block' : 'none';
toggleBtn.textContent = hidden ? '[ &#x26A0; HIDE REPORT ]' : '[ &#x26A0; REPORT THIS LEAK ]';
toggleBtn.classList.toggle('active',hidden);
});
}

// ---- REPORT ----
const reportBody = document.getElementById('report-body');
const copyBtn = document.getElementById('copy-btn');
const mailBtn = document.getElementById('mail-btn');

if(copyBtn){
copyBtn.addEventListener('click',function(){
if(!reportBody)return;
reportBody.select();
reportBody.setSelectionRange(0,reportBody.value.length);
navigator.clipboard.writeText(reportBody.value).then(function(){
copyBtn.textContent = '[ COPIED ]';
copyBtn.classList.add('copied');
setTimeout(function(){
copyBtn.textContent = '[ COPY TO CLIPBOARD ]';
copyBtn.classList.remove('copied');
},2000);
}).catch(function(){
document.execCommand('copy');
copyBtn.textContent = '[ COPIED ]';
setTimeout(function(){
copyBtn.textContent = '[ COPY TO CLIPBOARD ]';
},2000);
});
});
}

if(mailBtn){
mailBtn.addEventListener('click',function(){
if(!reportBody)return;
const subject = encodeURIComponent('Data Breach Report - ' + '{{data[0].name}}');
const body = encodeURIComponent(reportBody.value);
window.location.href = 'mailto:?subject=' + subject + '&body=' + body;
});
}
</script>
{% endif %}

<script>
// ---- FORM LOADING ----
document.getElementById('track-form').addEventListener('submit',function(){
document.getElementById('loading').classList.add('active');
});

// ---- CLOCK ----
function updateClock(){
const d=new Date();
const h=String(d.getHours()).padStart(2,'0');
const m=String(d.getMinutes()).padStart(2,'0');
const s=String(d.getSeconds()).padStart(2,'0');
const el=document.querySelector('.status-bar span:last-child');
if(el)el.textContent=h+':'+m+':'+s;
}
setInterval(updateClock,1000);
updateClock();
</script>

</body>
</html>
"""

# ===== FULL DATA PARSER =====
def parse_section(text):
    def get(pattern):
        m = re.search(pattern, text)
        return m.group(1).strip() if m else ""
    return {
        "name": get(r"Name[:\-]?\s*(.*)"),
        "father_name": get(r"Father Name[:\-]?\s*(.*)"),
        "mobile": get(r"Mobile[:\-]?\s*(.*)"),
        "address": get(r"Address[:\-]?\s*(.*)"),
        "circle": get(r"Circle[:\-]?\s*(.*)"),
        "alternate": get(r"Alternate[:\-]?\s*(.*)"),
        "aadhaar": get(r"Aadhaar[:\-]?\s*(.*)"),
    }

def fetch_data(number):
    try:
        url = f"https://exploitsindia.site/track/live.php?term={number}"
        r = requests.get(url, timeout=10)
        r.encoding = "utf-8"
        res = r.text
        print("="*60)
        print("RAW API RESPONSE:")
        print(res)
        print("="*60)

        parts = re.split(r"Additional Result:", res)
        results = []

        for i, part in enumerate(parts):
            parsed = parse_section(part)
            if parsed["name"]:
                results.append(parsed)

        return results if results else None

    except Exception as e:
        print(f"ERROR in fetch_data: {e}")
        traceback.print_exc()
        return None

@app.route("/", methods=["GET","POST"])
def home():
    if request.method == "POST":
        number = request.form.get("number")
        data = fetch_data(number)
        session["tracker_data"] = data
        return redirect("/")

    data = session.pop("tracker_data", None)
    return render_template_string(HTML, data=data)
if __name__ == "__main__":
    print("""
          
██╗  ██╗██████╗ ██╗███████╗██╗  ██╗
██║ ██╔╝██╔══██╗██║██╔════╝██║  ██║
█████╔╝ ██████╔╝██║███████╗███████║
██╔═██╗ ██╔══██╗██║╚════██║██╔══██║
██║  ██╗██║  ██║██║███████║██║  ██║
╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚══════╝╚═╝  ╚═╝
          
━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ DEVELOPER BY KRISH ⚡
━━━━━━━━━━━━━━━━━━━━━━━━━━

SERVER STARTING...
""")
    
    app.run(host="0.0.0.0", port=5000)