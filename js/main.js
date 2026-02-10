// Estado global do jogo
let unlockedDigits = ["_", "_", "_", "_", "_"]; 
const finalCode = ["3", "7", "9", "5", "4"]; // Ordem das fases definida no projeto

// Função para abrir o modal de questão
function openQuestion(phaseIndex) {
    const q = window.QUESTIONS[phaseIndex];
    if (!q) return;

    // Resetar feedback anterior
    const feedback = document.getElementById('qFeedback');
    feedback.innerText = "";
    
    document.getElementById('qBadge').innerText = q.id;
    document.getElementById('qPrompt').innerText = q.prompt;
    document.getElementById('qImg').src = `assets/images/${q.image}`;
    
    const optionsDiv = document.getElementById('qOptions');
    optionsDiv.innerHTML = '';
    
    q.options.forEach((opt, index) => {
        const btn = document.createElement('button');
        btn.className = 'btn-opt';
        btn.innerText = opt;
        btn.onclick = () => checkAnswer(index, q, phaseIndex);
        optionsDiv.appendChild(btn);
    });
    
    document.getElementById('qModal').classList.remove('hidden');
}

// Validação da resposta e liberação do dígito correspondente
function checkAnswer(selectedIndex, question, index) {
    const selectedLetter = String.fromCharCode(65 + selectedIndex); 
    const feedback = document.getElementById('qFeedback');
    
    if (selectedLetter === question.answer) {
        feedback.innerText = "✅ " + question.explain;
        feedback.className = "feedback success";
        
        // Libera o dígito específico daquela fase na posição correta
        if (question.main) {
            unlockedDigits[index] = finalCode[index];
            updateHUD();
        }
    } else {
        feedback.innerText = "❌ Tente novamente! Revise os conceitos anatômicos.";
        feedback.className = "feedback error";
    }
}

// Atualiza o HUD com o progresso visual do código
function updateHUD() {
    const hud = document.getElementById('hud');
    hud.innerText = `Código de Escape: ${unlockedDigits.join(" ")}`;
}

// Lógica do Teclado da Porta (Integrado ao kModal)
let currentInput = "";
function pressKey(num) {
    const display = document.getElementById('kDisplay');
    
    if (currentInput.length < 5) {
        currentInput += num;
        display.innerText = currentInput.padEnd(5, "_");
    }
    
    if (currentInput.length === 5) {
        if (currentInput === finalCode.join("")) {
            display.style.color = "#2ecc71";
            display.innerText = "OPEN";
            setTimeout(() => {
                alert("🎉 Missão Cumprida! Você dominou o sistema cardiorrespiratório.");
                location.reload();
            }, 500);
        } else {
            display.style.color = "#e74c3c";
            display.innerText = "ERROR";
            currentInput = "";
            setTimeout(() => {
                display.style.color = "#fff";
                display.innerText = "_____";
            }, 1000);
        }
    }
}

// Fechar Modais
document.getElementById('qClose').onclick = () => document.getElementById('qModal').classList.add('hidden');
document.getElementById('kClose').onclick = () => document.getElementById('kModal').classList.add('hidden');
