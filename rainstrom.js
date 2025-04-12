window.onload = function () {
  const canvas = document.createElement('canvas');
  canvas.id = 'rain';
  document.body.appendChild(canvas);

  const ctx = canvas.getContext('2d');
  let width = canvas.width = window.innerWidth;
  let height = canvas.height = window.innerHeight;

  const raindrops = Array.from({ length: 400 }, () => ({
    x: Math.random() * width,
    y: Math.random() * height,
    length: Math.random() * 20 + 10,
    velocityY: Math.random() * 4 + 4
  }));

  function drawRain() {
    ctx.clearRect(0, 0, width, height);
    ctx.strokeStyle = 'rgba(173,216,230,0.3)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    for (let drop of raindrops) {
      ctx.moveTo(drop.x, drop.y);
      ctx.lineTo(drop.x, drop.y + drop.length);
    }
    ctx.stroke();
    moveRain();
  }

  function moveRain() {
    for (let drop of raindrops) {
      drop.y += drop.velocityY;
      if (drop.y > height) {
        drop.y = -drop.length;
        drop.x = Math.random() * width;
      }
    }
  }

  function loop() {
    drawRain();
    requestAnimationFrame(loop);
  }

  loop();

  window.onresize = () => {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
  };
};
