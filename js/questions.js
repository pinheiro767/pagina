window.QUESTIONS = [
  {
    id: "Fase 1 — Mediastino",
    prompt: "O coração localiza-se predominantemente em qual compartimento do mediastino?",
    options: ["A) Mediastino superior","B) Mediastino anterior","C) Mediastino médio","D) Mediastino posterior","E) Cavidade pleural esquerda"],
    answer: "C",
    explain: "O coração fica no mediastino médio, dentro do pericárdio.",
    image: "q1_mediastino.png",
    main: true
  },
  {
    id: "Fase 2 — Irrigação coronariana",
    prompt: "A artéria interventricular anterior é ramo direto da:",
    options: ["A) Artéria coronária direita","B) Artéria coronária esquerda","C) Artéria circunflexa","D) Artéria torácica interna","E) Aorta descendente"],
    answer: "B",
    explain: "A interventricular anterior (LAD/DA) é ramo da coronária esquerda.",
    image: "q2_coronarias.png",
    main: true
  },
  {
    id: "Fase 3 — Hilo pulmonar",
    prompt: "No hilo pulmonar, a estrutura mais posterior em relação às demais é:",
    options: ["A) Artéria pulmonar","B) Veias pulmonares","C) Brônquio principal","D) Nervo frênico","E) Linfonodos"],
    answer: "C",
    explain: "No hilo, o brônquio principal tende a estar mais posterior.",
    image: "q3_hilo.png",
    main: true
  },
  {
    id: "Fase 4 — Valvas cardíacas",
    prompt: "A valva atrioventricular direita está localizada entre:",
    options: ["A) Átrio esquerdo e ventrículo esquerdo","B) Ventrículo esquerdo e aorta","C) Átrio direito e ventrículo direito","D) Átrio direito e veia cava superior","E) Ventrículo direito e tronco pulmonar"],
    answer: "C",
    explain: "AV direita = tricúspide (AD ↔ VD).",
    image: "q4_valvas.png",
    main: true
  },
  {
    id: "Fase 5 — Pleuras",
    prompt: "A pleura que reveste diretamente a superfície do pulmão e acompanha suas fissuras é denominada:",
    options: ["A) Pleura parietal costal","B) Pleura mediastinal","C) Pleura diafragmática","D) Pleura visceral","E) Endotélio pleural"],
    answer: "D",
    explain: "A pleura visceral está aderida ao pulmão e entra nas fissuras.",
    image: "q5_pleura.png",
    main: true
  },

  // BÔNUS (se quiser usar também)
  {
    id: "Bônus 1 — Árvore brônquica",
    prompt: "O brônquio principal direito é mais frequentemente associado a maior risco de aspiração porque é:",
    options: ["A) Mais longo, mais estreito e horizontal","B) Mais curto, mais largo e mais vertical","C) Mais curto, mais estreito e oblíquo","D) Mais longo, mais largo e vertical","E) Igual ao esquerdo em calibre e inclinação"],
    answer: "B",
    explain: "Direito = mais curto, mais largo e mais vertical.",
    image: "bonus1_bronquio_direito.png",
    main: false
  },
  {
    id: "Bônus 2 — Superfícies cardíacas",
    prompt: "A face esternocostal (anterior) do coração é formada predominantemente por:",
    options: ["A) Átrio esquerdo","B) Ventrículo esquerdo","C) Átrio direito","D) Ventrículo direito","E) Tronco pulmonar"],
    answer: "D",
    explain: "A face anterior do coração é predominantemente do ventrículo direito.",
    image: "bonus2_face_esternocostal.png",
    main: false
  },
  {
    id: "Bônus 3 — Nó AV (topografia)",
    prompt: "O nó atrioventricular localiza-se anatomicamente:",
    options: ["A) No teto do átrio direito, próximo à veia cava superior","B) No septo interatrial, próximo ao óstio do seio coronário","C) Na parede livre do ventrículo direito","D) No sulco interventricular anterior","E) No ápice cardíaco"],
    answer: "B",
    explain: "Nó AV: septo interatrial, próximo ao óstio do seio coronário.",
    image: "bonus3_no_av.png",
    main: false
  }
];
