import os
import requests

USERNAME = os.getenv("GITHUB_REPOSITORY_OWNER", "ksbn")
TOKEN = os.getenv("GITHUB_TOKEN")

# 1. Fetch real contribution data from GitHub GraphQL API
query = """
query($user: String!) {
  user(login: $user) {
    contributionsCollection {
      contributionCalendar {
        weeks {
          contributionDays {
            contributionCount
            date
          }
        }
      }
    }
  }
}
"""

res = requests.post(
    "https://api.github.com/graphql",
    json={"query": query, "variables": {"user": USERNAME}},
    headers={"Authorization": f"bearer {TOKEN}"}
).json()

weeks = res["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]

# 2. Define Snow & Ice Color Palette
def get_snow_color(count):
    if count == 0: return "#ebedf0"  # Snow Base
    if count < 3:  return "#b6e3f4"  # Light Ice
    if count < 6:  return "#6bc5e8"  # Mid Powder
    if count < 9:  return "#2ca0d2"  # Deep Slope
    return "#007bb6"                 # Glacier Blue

# 3. Build Grid & Compute Slalom Coordinates
grid_rects = []
path_points = []

for x, week in enumerate(weeks):
    for y, day in enumerate(week["contributionDays"]):
        color = get_snow_color(day["contributionCount"])
        px = x * 13 + 15
        py = y * 13 + 15
        grid_rects.append(f'<rect x="{px}" y="{py}" width="10" height="10" rx="2" fill="{color}" />')
        
        # Track active contribution squares for the slalom trail
        if day["contributionCount"] > 0:
            path_points.append((px, py))

# Fallback path if contribution history is sparse
if len(path_points) < 2:
    path_points = [(15, 15), (200, 40), (400, 15), (600, 70), (700, 15)]

# 4. Generate CSS Keyframes for Box-by-Box Movement
keyframes_css = []
total_points = len(path_points)

for i, (cx, cy) in enumerate(path_points):
    pct = round((i / max(total_points - 1, 1)) * 100, 2)
    keyframes_css.append(f"  {pct}% {{ transform: translate({cx}px, {cy}px); }}")

keyframes_str = "\n".join(keyframes_css)

# 5. Native Vector Rider Sprite (Snowboarder Girl)
# Drawn using native SVG shapes (Head, Helmet, Goggles, Ponytail, Jacket, Board)
vector_rider_sprite = """
<g id="snowboarder-girl">
  <!-- Snowboard -->
  <rect x="-3" y="9" width="16" height="3" rx="1.5" fill="#007bb6" transform="rotate(-12)" />
  <!-- Legs / Pants -->
  <rect x="2" y="5" width="3" height="5" fill="#1b394a" />
  <rect x="6" y="5" width="3" height="5" fill="#1b394a" />
  <!-- Jacket -->
  <rect x="1" y="1" width="9" height="5" rx="1" fill="#3c83aa" />
  <!-- Helmet & Head -->
  <circle cx="5.5" cy="-1.5" r="3.5" fill="#6bc5e8" />
  <!-- Pink Goggles -->
  <rect x="4" y="-2.5" width="4" height="1.5" rx="0.5" fill="#ff4b82" />
  <!-- Ponytail -->
  <path d="M 2.5 -1.5 Q 0 -1 0 2 Q 1 3 2 1 Z" fill="#e6a15c" />
</g>
"""

# 6. Assemble Final SVG File
svg_output = f"""<svg width="720" height="120" viewBox="0 0 720 120" xmlns="http://www.w3.org/2000/svg">
  <style>
    .slalom-runner {{
      animation: slalomStep 15s steps(1, end) infinite alternate;
    }}
    @keyframes slalomStep {{
{keyframes_str}
    }}
  </style>
  <g>
    <!-- Contribution Grid -->
    {''.join(grid_rects)}
    
    <!-- Vector Snowboarder Girl -->
    <g class="slalom-runner">
      {vector_rider_sprite}
    </g>
  </g>
</svg>"""

os.makedirs("dist", exist_ok=True)
with open("dist/github-snowboard-slalom.svg", "w") as f:
    f.write(svg_output)
