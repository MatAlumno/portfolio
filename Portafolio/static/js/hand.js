const hand = document.getElementById("hand-cursor");

let mouse = { x: window.innerWidth / 2, y: window.innerHeight / 2 };
let handPos = { x: mouse.x, y: mouse.y };

window.addEventListener("mousemove", e => {
    mouse.x = e.clientX;
    mouse.y = e.clientY;
});

// Smoothness
const smooth = 0.1;

// Offset 
const offsetX = 30;
const offsetY = -30;

// Ajusta este valor según tu imagen
const angleOffset = 180;  

function animateHand() {

    handPos.x += (mouse.x + offsetX  - handPos.x) * smooth;
    handPos.y += (mouse.y + offsetY - handPos.y) * smooth;

    const dx = mouse.x - handPos.x;
    const dy = mouse.y + offsetY - handPos.y;
    const angle = Math.atan2(dy, dx) * 180 / Math.PI;

    hand.style.transform = `
        translate(${handPos.x}px, ${handPos.y}px)
        rotate(${angle + angleOffset}deg)
    `;

    requestAnimationFrame(animateHand);
}

animateHand();
