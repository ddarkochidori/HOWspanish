// ==========================================
// CONFIGURACIÓN DE AMOR
// ==========================================
// 1. FECHA DE INICIO: 13 de Enero de 2026
const fechaInicio = new Date(2026, 0, 13, 0, 0, 0); 
// 2. FECHA DEL ENCUENTRO: 20 de Julio de 2026
const fechaEncuentro = new Date(2026, 6, 20, 0, 0, 0); // Mes 6 es Julio (0-index)

// ==========================================
// NAVEGACIÓN
// ==========================================
function ver(seccionId) {
    document.querySelectorAll('section').forEach(s => {
        s.classList.remove('active');
        s.classList.add('hidden');
    });
    const seccion = document.getElementById(seccionId);
    seccion.classList.remove('hidden');
    seccion.classList.add('active');
    
    // Scroll suave arriba
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ==========================================
// DOBLE CONTADOR DE TIEMPO
// ==========================================
function actualizarRelojes() {
    const ahora = new Date();
    
    // RELOJ 1: Tiempo Juntos
    const diferencia = ahora - fechaInicio;
    const dias = Math.floor(diferencia / (1000 * 60 * 60 * 24));
    const horas = Math.floor((diferencia / (1000 * 60 * 60)) % 24);
    const minutos = Math.floor((diferencia / 1000 / 60) % 60);
    const segundos = Math.floor((diferencia / 1000) % 60);

    // Solo actualizar si la sección es visible para ahorrar recursos
    if(document.getElementById('dias')) {
        document.getElementById('dias').innerText = dias;
        document.getElementById('horas').innerText = horas.toString().padStart(2, '0');
        document.getElementById('minutos').innerText = minutos.toString().padStart(2, '0');
        document.getElementById('segundos').innerText = segundos.toString().padStart(2, '0');
    }

    // RELOJ 2: Cuenta regresiva Julio
    const diffJulio = fechaEncuentro - ahora;
    if (diffJulio > 0) {
        const dJ = Math.floor(diffJulio / (1000 * 60 * 60 * 24));
        const hJ = Math.floor((diffJulio / (1000 * 60 * 60)) % 24);
        const mJ = Math.floor((diffJulio / 1000 / 60) % 60);
        const sJ = Math.floor((diffJulio / 1000) % 60);
        
        const textoCuenta = `${dJ} Días, ${hJ}h ${mJ}m ${sJ}s`;
        if(document.getElementById('countdown-julio')) {
            document.getElementById('countdown-julio').innerText = textoCuenta;
        }
    } else {
        if(document.getElementById('countdown-julio')) {
            document.getElementById('countdown-julio').innerText = "¡HOY ES EL DÍA! ✈️❤️";
        }
    }
}
setInterval(actualizarRelojes, 1000);

// ==========================================
// ÁBRELA CUANDO... (HUMANIZADO SAMUEL)
// ==========================================
const mensajesOpenWhen = {
    'triste': {
        titulo: "Para mi niña triste 😢",
        msg: "Amor mío, odio saber que estás mal. Escúchame: Esto es solo un momento feo, no una vida fea. Eres la persona más fuerte que conozco, pero no tienes que ser fuerte siempre. Llora si quieres, pero luego lávate la carita, que esos ojos hermosos son para brillar. Te amo infinito y te abrazo a la distancia.",
        img: "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbnZ4bm14bm14bm14bm14bm14bm14bm14bm14bm14bm14bm14biZlcD12MV9zdGlja2Vyc19zZWFyY2gmY3Q9cw/XpgOZHuDfIkoM/giphy.gif"
    },
    'feliz': {
        titulo: "¡Esa sonrisa me da vida! 😄",
        msg: "¡Siiii! Verte feliz es mi meta diaria. Disfruta este momento, mi amor. Ojalá estuviera ahí para celebrar contigo y darte mil besos. Tu felicidad es mi felicidad, nunca lo olvides.",
        img: "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbnZ4bm14bm14bm14bm14bm14bm14bm14bm14bm14bm14bm14biZlcD12MV9zdGlja2Vyc19zZWFyY2gmY3Q9cw/TjGFDxbbZRYjw/giphy.gif"
    },
    'duda': {
        titulo: "¿Dudas? ¡Jamás! 😠❤️",
        msg: "Ey, quítate esas ideas de la cabeza. Eres tú. Solo tú. No hay nadie más en mi vida ni la habrá. Desde el 13 de enero mi corazón tiene tu nombre tatuado. Confía en lo que tenemos, porque yo confío ciegamente en ti.",
        img: "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbnZ4bm14bm14bm14bm14bm14bm14bm14bm14bm14bm14bm14biZlcD12MV9zdGlja2Vyc19zZWFyY2gmY3Q9cw/4N1wOi78ZGzIc/giphy.gif"
    },
    'miedo': {
        titulo: "Yo te protejo 🛡️",
        msg: "Aunque esté lejos, nadie te va a tocar. Eres mi mujer y te cuido desde aquí hasta el fin del mundo. Si tienes miedo, cierra los ojos e imagina que te tengo agarrada de la mano muy fuerte. Todo va a estar bien.",
        img: "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbnZ4bm14bm14bm14bm14bm14bm14bm14bm14bm14bm14bm14biZlcD12MV9zdGlja2Vyc19zZWFyY2gmY3Q9cw/10ExVl07U5zX56/giphy.gif"
    },
    'extrañar': {
        titulo: "Yo te extraño más... ✈️",
        msg: "Sé que duele la distancia, amor. A mí también me duele no poder abrazarte. Pero piensa en el 20 DE JULIO. Ese día valdrá la pena cada segundo de espera. Ya falta menos, resiste un poquito más por nosotros.",
        img: "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbnZ4bm14bm14bm14bm14bm14bm14bm14bm14bm14bm14bm14biZlcD12MV9zdGlja2Vyc19zZWFyY2gmY3Q9cw/C9x8gX02SnMIoAClXa/giphy.gif"
    },
    'celosa': {
        titulo: "¡Mi celosa hermosa! 😏",
        msg: "Me encanta que seas celosa, pero relájate. No tienes competencia. Las demás son invisibles para mí. Tú eres mi reina, mi diosa y mi todo. Que miren lo que quieran, que yo solo tengo ojos para mi Natalia.",
        img: "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbnZ4bm14bm14bm14bm14bm14bm14bm14bm14bm14bm14bm14biZlcD12MV9zdGlja2Vyc19zZWFyY2gmY3Q9cw/LpdlqTkgO2Lwwixwv7/giphy.gif"
    }
};

function abrirSobre(tipo) {
    const data = mensajesOpenWhen[tipo];
    document.getElementById('titulo-sobre').innerText = data.titulo;
    document.getElementById('mensaje-sobre').innerText = data.msg;
    document.getElementById('img-sobre').src = data.img;
    document.getElementById('modal-sobre').classList.remove('hidden');
}
function cerrarSobre() {
    document.getElementById('modal-sobre').classList.add('hidden');
}

// ==========================================
// JUEGOS DIVERTIDOS
// ==========================================
let besos = 0;
document.getElementById('clicker-btn').addEventListener('click', () => {
    besos++;
    document.getElementById('score').innerText = besos;
    
    // RANGOS DE AMOR DIVERTIDOS
    const rank = document.getElementById('rank-amor');
    if (besos > 10) rank.innerText = "Novia Cariñosa 🥰";
    if (besos > 30) rank.innerText = "Adicta a mis besos 💋";
    if (besos > 60) rank.innerText = "Loca por Samuel 🤪";
    if (besos > 100) rank.innerText = "¡YA CÁSATE CONMIGO! 💍";
    
    // Animación de corazón flotante al hacer click
    crearCorazonClick();
});

function girarRuleta() {
    const opciones = [
        "Ir al cine a ver Terror 🎬", 
        "Comer hamburguesas gigantes 🍔", 
        "Caminar de la mano por el parque 🌳", 
        "Darnos besitos infinitos 💋", 
        "Tomarnos 1000 fotos 📸", 
        "¡Hacer todo lo anterior! ⭐"
    ];
    const res = document.getElementById('ruleta-res');
    res.innerText = "Girando...";
    
    let vueltas = 0;
    const intervalo = setInterval(() => {
        res.innerText = opciones[Math.floor(Math.random() * opciones.length)];
        vueltas++;
        if(vueltas > 10) {
            clearInterval(intervalo);
        }
    }, 100);
}

// ==========================================
// 100 RAZONES (ALEATORIAS)
// ==========================================
const razones = [
    "Porque eres Natalia y eso basta.",
    "Por cómo me haces sentir a miles de km.",
    "Porque eres mi mujer, la única.",
    "Por tu voz que me da paz.",
    "Porque aguantas mis locuras.",
    "Porque eres la niña más linda del mundo.",
    "Porque me elegiste a mí.",
    "Porque el 20 de Julio será épico contigo.",
    "Porque me motivas a ser mejor.",
    "¡Porque simplemente te amo!"
];
function nuevaRazon() {
    document.getElementById('frase-razon').innerText = razones[Math.floor(Math.random() * razones.length)];
}

// ==========================================
// EFECTOS VISUALES
// ==========================================
function crearCorazonesFondo() {
    const container = document.getElementById('hearts-container');
    setInterval(() => {
        const heart = document.createElement('div');
        heart.innerHTML = '❤️';
        heart.className = 'floating-heart';
        heart.style.left = Math.random() * 100 + 'vw';
        heart.style.top = '100vh';
        heart.style.fontSize = (Math.random() * 20 + 10) + 'px';
        heart.style.animationDuration = (Math.random() * 3 + 3) + 's';
        
        container.appendChild(heart);
        setTimeout(() => heart.remove(), 6000);
    }, 800);
}
crearCorazonesFondo();

function crearCorazonClick() {
    // Efecto extra al hacer click en el botón de besos (opcional)
}
