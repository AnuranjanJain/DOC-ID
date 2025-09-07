
// Wait for DOM to fully load before initializing
document.addEventListener('DOMContentLoaded', function() {
    // Apply delay to each letter in loading animation
    const letters = document.querySelectorAll('.loading-text span');
    letters.forEach((letter, index) => {
        letter.style.animationDelay = `${index * 0.1}s`;
    });
    // Loading animation - show content after matrix has been visible
    setTimeout(function() {
        const loadingElement = document.getElementById('loading');
        if (loadingElement) {
            loadingElement.style.opacity = 0;
            setTimeout(function() {
                loadingElement.style.display = 'none';
                document.getElementById('mainContent').style.display = 'block';
            }, 700);
        }
    }, 500);
    // Initialize Matrix animation
    initializeMatrix();
});

function initializeMatrix() {
    var canvas = document.getElementById('canvas'),
        ctx = canvas.getContext('2d'),
        canvas2 = document.getElementById('canvas2'),
        ctx2 = canvas2.getContext('2d'),
        // full screen dimensions
        cw = window.innerWidth,
        ch = window.innerHeight,
        // Japanese katakana characters for authentic Matrix look
        katakana = "abcdefghijklmnopqrstuvwxyz",
        latin = "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        nums = "0123456789",
        // Combine all character sets
        chars = katakana + latin + nums,
        charArr = chars.split(''),
        maxCharCount = 100,
        fallingCharArr = [],
        fontSize = 16, // Larger font size for better visibility
        maxColums = cw/(fontSize),
        glowIntensity = 0.3; // Reduced glow intensity for subtlety

    // Set canvas dimensions
    canvas.width = canvas2.width = cw;
    canvas.height = canvas2.height = ch;

    // Fill background with solid dark color first
    ctx.fillStyle = "rgba(0, 0, 0, 0.97)"; // Darker initial background
    ctx.fillRect(0, 0, cw, ch);

    // Handle window resize
    window.addEventListener('resize', function() {
        cw = window.innerWidth;
        ch = window.innerHeight;
        canvas.width = canvas2.width = cw;
        canvas.height = canvas2.height = ch;
        maxColums = cw/(fontSize);
        // Reset falling characters
        fallingCharArr = [];
        for(var i = 0; i < maxColums; i++) {
            fallingCharArr.push(new Point(i*fontSize, randomFloat(-500, 0)));
        }
        // Fill background with solid dark color after resize
        ctx.fillStyle = "rgba(0, 0, 0, 0.97)";
        ctx.fillRect(0, 0, cw, ch);
    });

    function randomInt(min, max) {
        return Math.floor(Math.random() * (max - min) + min);
    }

    function randomFloat(min, max) {
        return Math.random() * (max - min) + min;
    }

    function Point(x, y) {
        this.x = x;
        this.y = y;
        this.stackHeight = randomInt(3, 20); // Reduced stack height for subtlety
        this.speed = randomFloat(0.5, 2); // Slower speed for subtle movement
        this.countdown = this.stackHeight; // Countdown for the bright head character
        // Only 5% chance of being a bright column (reduced from 10%)
        this.isBright = Math.random() < 0.05;
        this.opacity = randomFloat(0.3, 0.7); // Reduced opacity range
    }

    Point.prototype.draw = function(ctx) {
        // Get new random character
        this.value = charArr[randomInt(0, charArr.length-1)];
        // Create a stack effect where only the first character is brightest
        var isHead = this.countdown <= 0;
        var headPos = Math.floor(this.y / fontSize) * fontSize;
        // Iterate through the stack positions
        for(var i = 0; i <= this.stackHeight; i++) {
            var posY = this.y - (i * fontSize);
            var char = charArr[randomInt(0, charArr.length-1)];
            var alpha;
            // If this is the head character
            if (i === 0) {
                // Bright head character (but dimmer than before)
                ctx2.shadowColor = "#00ff00";
                ctx2.shadowBlur = 5; // Reduced blur for subtlety
                ctx2.fillStyle = this.isBright ? "rgba(180, 255, 180, 0.7)" : "rgba(120, 255, 120, 0.6)";
                alpha = 0.7; // Reduced from 0.9
            } else {
                // Trail characters get progressively dimmer
                var dimming = 1 - (i / this.stackHeight);
                alpha = dimming * 0.5 * this.opacity; // Reduced overall opacity
                if (this.isBright) {
                    ctx2.shadowColor = "#00ff00";
                    ctx2.shadowBlur = 3; // Reduced blur
                    ctx2.fillStyle = `rgba(100, 255, 100, ${alpha})`;
                } else {
                    ctx2.shadowBlur = 0;
                    ctx2.fillStyle = `rgba(40, 180, 40, ${alpha})`;
                }
            }
            if (posY < ch && posY > 0) {
                ctx2.font = fontSize + "px monospace";
                ctx2.fillText(char, this.x, posY);
            }
        }
        // Update position
        this.y += this.speed;
        // Reset when reaching bottom
        if (this.y - (this.stackHeight * fontSize) > ch) {
            this.y = randomFloat(-200, 0);
            this.speed = randomFloat(0.5, 2); // Slower speed range
            this.stackHeight = randomInt(3, 20); // Reduced stack height
            this.isBright = Math.random() < 0.05;
        }
    }

    // Create falling characters
    for(var i = 0; i < maxColums; i++) {
        fallingCharArr.push(new Point(i*fontSize, randomFloat(-500, 0)));
    }

    // Start animation immediately
    var update = function() {
        // Darker semi-transparent black for trail effect
        ctx.fillStyle = "rgba(0, 0, 0, 0.08)"; // Increased opacity for darker trails
        ctx.fillRect(0, 0, cw, ch);
        // Clear second canvas for glowing effect
        ctx2.clearRect(0, 0, cw, ch);
        // Update all falling characters
        var i = fallingCharArr.length;
        while (i--) {
            fallingCharArr[i].draw(ctx2);
        }
        requestAnimationFrame(update);
    }
    // Start matrix animation immediately
    update();
}
