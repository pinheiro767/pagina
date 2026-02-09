const hud = document.getElementById("hud");

const config = {
  type: Phaser.AUTO,
  parent: "game",
  width: 800,
  height: 500,
  backgroundColor: "#0b1224",
  scale: {
    mode: Phaser.Scale.FIT,
    autoCenter: Phaser.Scale.CENTER_BOTH
  },
  scene: {
    preload,
    create
  }
};

new Phaser.Game(config);

function preload() {
  console.log("Phaser carregado");
}

function create() {
  hud.textContent = "Jogo iniciado";

  this.add.text(200, 200, "CardioResp Escape", {
    fontSize: "28px",
    color: "#ffffff"
  });

  this.add.circle(400, 300, 20, 0x4fc3f7);
}
