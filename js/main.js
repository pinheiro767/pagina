// Estado global do jogo
let solvedQuestions = 0;
let unlockedDigits = [];
const finalCode = ["3", "7", "9", "5", "4"]; // Ordem das fases

// Função para abrir o modal de questão
function openQuestion(phaseIndex) {
    const q = window.QUESTIONS[phaseIndex];
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

// Validação da resposta e liberação do dígito
function checkAnswer(selectedIndex, question, index) {
    const selectedLetter = String.fromCharCode(65 + selectedIndex); // 0=A, 1=B...
    const feedback = document.getElementById('qFeedback');
    
    if (selectedLetter === question.answer) {
        feedback.innerText = "✅ " + question.explain;
        feedback.style.color = "#2ecc71";
        
        if (question.main && !unlockedDigits.includes(finalCode[index])) {
            unlockedDigits.push(finalCode[index]);
            updateHUD();
        }
    } else {
        feedback.innerText = "❌ Tente novamente! Analise a anatomia na imagem.";
        feedback.style.color = "#e74c3c";
    }
}

// Atualiza o HUD com o código que o aluno vai descobrindo
function updateHUD() {
    const hud = document.getElementById('hud');
    hud.innerText = `Dígitos encontrados: ${unlockedDigits.join(" ")}`;
}

// Lógica do Teclado da Porta
let currentInput = "";
function pressKey(num) {
    if (currentInput.length < 5) {
        currentInput += num;
        document.getElementById('kDisplay').innerText = currentInput.padEnd(5, "_");
    }
    
    if (currentInput === finalCode.join("")) {
        alert("🎉 Parabéns! Você dominou o sistema cardiorrespiratório e escapou!");
        location.reload(); 
    } else if (currentInput.length === 5) {
        currentInput = ""; // Reseta se errar
        document.getElementById('kDisplay').innerText = "ERRO";
        setTimeout(() => document.getElementById('kDisplay').innerText = "_____", 1000);
    }
}
