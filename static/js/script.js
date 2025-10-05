script_js = r'''// Character Forge interactions
document.addEventListener("DOMContentLoaded", function() {
  // Animate buttons
  const buttons = document.querySelectorAll(".choice-btn");
  buttons.forEach(btn => {
    btn.addEventListener("click", () => {
      btn.classList.add("pressed");
      setTimeout(() => btn.classList.remove("pressed"), 200);
    });
  });

  // Add smooth scroll on transitions
  document.querySelectorAll("form").forEach(f => {
    f.addEventListener("submit", () => window.scrollTo({ top: 0, behavior: "smooth" }));
  });
});
'''

with open(os.path.join(ROOT, "static", "js", "script.js"), "w", encoding="utf-8") as f:
    f.write(script_js)

# --- Placeholder portrait (SVG) ---
portrait_svg = r'''<svg xmlns="http://www.w3.org/2000/svg" width="480" height="640" viewBox="0 0 480 640">
<rect width="100%" height="100%" fill="#efe6d9"/>
<g transform="translate(40,40)">
  <rect width="400" height="560" rx="12" fill="#fffaf0" stroke="#e1d6c4" />
  <text x="200" y="300" font-family="Cinzel, serif" font-size="28" text-anchor="middle" fill="#7a3b1b">Portrait</text>
  <text x="200" y="340" font-family="EB Garamond, serif" font-size="14" text-anchor="middle" fill="#6b5a4a">Replace with race_class art</text>
</g>
</svg>'''

with open(os.path.join(ROOT, "static", "img", "portrait_placeholder.png"), "wb") as f:
    f.write(portrait_svg.encode("utf-8"))