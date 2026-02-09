const HUD = document.getElementById("hud");

// mobile buttons state
const mobile = { up:false, down:false, left:false, right:false, interact:false };
function bindBtn(id, key){
  const el = document.getElementById(id);
  const on = () => mobile[key] = true;
  const off = () => mobile[key] = false;
  el.addEventListener("pointerdown", on);
  el.addEventListener("pointerup", off);
  el.addEventListener("pointercancel", off);
  el.addEventListener("pointerleave", off);
}
bindBtn("up","up"); bindBtn("down","down"); bindBtn("left","left"); bindBtn("right","right");

document.getElementById("interact").addEventListener("pointerdown", ()=> mobile.interact = true);
document.getElementById("interact").addEventListener("pointerup", ()=> mobile.interact = false);

// modals
const qModal = document.getElementById("qModal");
const qBadge = document.getElementById("qBadge");
const qTitle = document.getElementById("qTitle");
const qPrompt = document.getElementById("qPrompt");
const qImg = document.getElementById("qImg");
const qOptions = document.getElementById("qOptions");
const qFeedback = document.getElementById("qFeedback");
document.getElementById("qClose").onclick = ()=> hideQ();

const kModal = document.getElementById("kModal");
const kDisplay = document.getElementById("kDisplay");
const kPad = document.getElementById("kPad");
const kHelp = document.getElementById("kHelp");
document.getElementById("kClose").onclick = ()=> hideK();

function showQ(){ qModal.classList.remove("hidden"); }
function hideQ(){ qModal.classList.add("hidden"); }
function showK(){ kModal.classList.remove("hidden"); }
function hideK(){ kModal.classList.add("hidden"); }

// escape code
const MAIN_CODE_DIGITS = ["7","3","9","1","4"];
const FINAL_CODE = MAIN_CODE_DIGITS.join("");

// terminal positions
const TERMINALS = [
  {q:0, x:220, y:190},
  {q:1, x:520, y:170},
  {q:2, x:820, y:220},
  {q:3, x:330, y:440},
  {q:4, x:760, y:470},
  // bônus
  {q:5, x:980, y:360},
  {q:6, x:110, y:510},
  {q:7, x:560, y:520},
];

const config = {
  type: Phaser.AUTO,
  parent: "game",
  width: 1100,
  height: 650,
  backgroundColor: "#070b14",
  scale: { mode: Phaser.Scale.FIT, autoCenter: Phaser.Scale.CENTER_BOTH },
  scene: { preload, create, update }
};

let player, cursors, keys;
let terminals = [];
let door, doorText;
let solved = new Set();
let score = 0, combo = 0, shields = 0, penalty = 0;
let digits = [];
let interactLock = false;
let keypadInput = "";

new Phaser.Game(config);

function preload(){
  for (const q of window.QUESTIONS){
    this.load.image(q.image, `assets/images/${q.image}`);
  }
}

function create(){
  // lab panel
  const g = this.add.graphics();
  g.fillStyle(0x0b1224, 1).fillRoundedRect(20, 80, 1060, 550, 18);
  g.lineStyle(2, 0x1f2d4a, 1).strokeRoundedRect(20, 80, 1060, 550, 18);

  player = this.add.circle(120, 325, 16, 0xa0dcff).setStrokeStyle(3, 0x142032);

  terminals = [];
  TERMINALS.forEach(t=>{
    const rect = this.add.rectangle(t.x, t.y, 56, 44, 0x3a4670).setStrokeStyle(2, 0xa0c8ff);
    rect.q = t.q;
    terminals.push(rect);
  });

  door = this.add.rectangle(1030, 325, 110, 180, 0x1c202e).setStrokeStyle(2, 0xa0c8ff);
  this.add.text(1000, 248, "PORTA", {fontFamily:"Arial", fontSize:"18px", color:"#eef2ff"});
  doorText = this.add.text(985, 280, "TRANCADA", {fontFamily:"Arial", fontSize:"14px", color:"#eef2ff"});

  cursors = this.input.keyboard.createCursorKeys();
  keys = this.input.keyboard.addKeys("W,A,S,D,E");
  this.input.keyboard.on("keydown-E", ()=> onInteract());
  this.input.keyboard.on("keydown-ESC", ()=> { hideQ(); hideK(); });

  buildKeypadUI();
  renderHUD();
}

function update(_, dtMs){
  const dt = dtMs/1000;
  const sp = 260;

  const left = keys.A.isDown || cursors.left.isDown || mobile.left;
  const right = keys.D.isDown || cursors.right.isDown || mobile.right;
  const up = keys.W.isDown || cursors.up.isDown || mobile.up;
  const down = keys.S.isDown || cursors.down.isDown || mobile.down;

  let vx = (right?1:0) - (left?1:0);
  let vy = (down?1:0) - (up?1:0);

  const n = Math.hypot(vx,vy) || 1;
  player.x = clamp(player.x + (vx/n)*sp*dt, 40, 1060);
  player.y = clamp(player.y + (vy/n)*sp*dt, 100, 610);

  // Interact mobile
  if (mobile.interact && !interactLock){
    interactLock = true;
    onInteract();
  }
  if (!mobile.interact) interactLock = false;

  const keysMain = countMainSolved();
  doorText.setText(keysMain >= 5 ? "PRONTA" : "TRANCADA");
  renderHUD();
}

function clamp(v,a,b){ return Math.max(a, Math.min(b,v)); }
function near(ax,ay,bx,by,dist=44){
  return Phaser.Math.Distance.Between(ax,ay,bx,by) <= dist;
}

function countMainSolved(){
  let c=0;
  for (let i=0;i<5;i++) if (solved.has(i)) c++;
  return c;
}

function onInteract(){
  if (!qModal.classList.contains("hidden") || !kModal.classList.contains("hidden")) return;

  // terminal?
  for (const t of terminals){
    if (near(player.x, player.y, t.x, t.y, 46)){
      if (solved.has(t.q)) return;
      openQuestion(t.q);
      return;
    }
  }

  // door?
  if (near(player.x, player.y, door.x, door.y, 90)){
    if (countMainSolved() < 5){
      toast("Porta trancada: resolva as 5 fases principais.");
      return;
    }
    openKeypad();
    return;
  }
}

function toast(msg){
  HUD.textContent = msg;
  setTimeout(renderHUD, 1400);
}

function renderHUD(){
  const t = Math.floor((performance.now()/1000) + penalty);
  const mm = String(Math.floor(t/60)).padStart(2,"0");
  const ss = String(t%60).padStart(2,"0");
  const keysMain = countMainSolved();
  HUD.textContent = `⏱️ ${mm}:${ss} • 🔑 ${keysMain}/5 • 🪙 ${score} • 🔥 ${combo} • 💠 ${shields} • 🔢 ${digits.join("")}`;
}

function openQuestion(qIndex){
  const q = window.QUESTIONS[qIndex];
  qBadge.textContent = q.main ? "🗝️ PRINCIPAL" : "🧩 BÔNUS";
  qTitle.textContent = q.id;
  qPrompt.textContent = q.prompt;
  qImg.src = `assets/images/${q.image}`;
  qFeedback.textContent = "";

  qOptions.innerHTML = "";
  q.options.forEach(opt=>{
    const btn = document.createElement("button");
    btn.className = "opt";
    btn.textContent = opt;
    btn.onclick = ()=> answerQuestion(qIndex, opt);
    qOptions.appendChild(btn);
  });

  showQ();
}

function answerQuestion(qIndex, opt){
  const q = window.QUESTIONS[qIndex];
  const picked = opt.split(")")[0].trim();

  if (picked === q.answer){
    qFeedback.textContent = `✅ Correto! +100 🪙  •  ${q.explain}`;
    score += 100;
    combo += 1;
    if (combo % 3 === 0) shields += 1;
    solved.add(qIndex);

    if (q.main && qIndex >= 0 && qIndex <= 4){
      const d = MAIN_CODE_DIGITS[qIndex];
      if (!digits.includes(d)) digits.push(d);
    }

    setTimeout(()=> hideQ(), 650);
  } else {
    combo = 0;
    if (shields > 0){
      shields -= 1;
      qFeedback.textContent = `❌ Erro… mas o escudo te salvou!`;
    } else {
      penalty += 10;
      qFeedback.textContent = `❌ Incorreto. +10s`;
    }
  }
}

function buildKeypadUI(){
  kPad.innerHTML = "";
  const buttons = ["1","2","3","4","5","6","7","8","9","⌫","0","⏎"];
  buttons.forEach(b=>{
    const el = document.createElement("button");
    el.className = "btn";
    el.textContent = b;
    el.onclick = ()=>{
      if (b === "⌫") keypadInput = keypadInput.slice(0,-1);
      else if (b === "⏎") submitKeypad();
      else if (/\d/.test(b) && keypadInput.length < 8) keypadInput += b;
      renderKeypad();
    };
    kPad.appendChild(el);
  });
}

function openKeypad(){
  keypadInput = "";
  renderKeypad();
  showK();
}

function renderKeypad(){
  kDisplay.textContent = keypadInput || "—";
  kHelp.textContent = `Dígitos coletados: ${digits.join("")} • Código final: ${FINAL_CODE.length} dígitos`;
}

function submitKeypad(){
  if (keypadInput === FINAL_CODE){
    hideK();
    toast("🎉 Você escapou! Parabéns!");
  } else {
    keypadInput = "";
    penalty += 10;
    toast("Código errado (+10s). Tente novamente.");
    renderKeypad();
  }
                       }
