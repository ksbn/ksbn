import os
import requests

USERNAME = os.getenv("GITHUB_REPOSITORY_OWNER", "ksbn")
TOKEN = os.getenv("GITHUB_TOKEN")

query = """
query($user: String!) {
  user(login: $user) {
    contributionsCollection {
      contributionCalendar {
        weeks {
          contributionDays {
            contributionCount
          }
        }
      }
    }
  }
}
"""

try:
    res = requests.post(
        "https://api.github.com/graphql",
        json={"query": query, "variables": {"user": USERNAME}},
        headers={"Authorization": f"bearer {TOKEN}"}
    ).json()

    weeks = res["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
except Exception as e:
    print(f"API Error or invalid response: {e}")
    weeks = []

def get_snow_color(count):
    if count == 0: return "#ebedf0"
    if count < 3:  return "#b6e3f4"
    if count < 6:  return "#6bc5e8"
    if count < 9:  return "#2ca0d2"
    return "#007bb6"

grid_rects = []
path_points = []

if weeks:
    for x, week in enumerate(weeks):
        for y, day in enumerate(week["contributionDays"]):
            count = day.get("contributionCount", 0)
            color = get_snow_color(count)
            px = x * 13 + 15
            py = y * 13 + 15
            grid_rects.append(f'<rect x="{px}" y="{py}" width="10" height="10" rx="2" fill="{color}" />')
            
            if count > 0:
                path_points.append((px, py))

if len(path_points) < 2:
    path_points = [(15, 15), (200, 40), (400, 15), (600, 70), (700, 15)]

keyframes_css = []
total_points = len(path_points)

for i, (cx, cy) in enumerate(path_points):
    pct = round((i / max(total_points - 1, 1)) * 100, 2)
    keyframes_css.append(f"  {pct}% {{ transform: translate({cx}px, {cy}px); }}")

keyframes_str = "\n".join(keyframes_css)

vector_rider_sprite = """
<g id="snowboarder-girl">
  <rect x="-3" y="9" width="16" height="3" rx="1.5" fill="#007bb6" transform="rotate(-12)" />
  <rect x="2" y="5" width="3" height="5" fill="#1b394a" />
  <rect x="6" y="5" width="3" height="5" fill="#1b394a" />
  <rect x="1" y="1" width="9" height="5" rx="1" fill="#3c83aa" />
  <circle cx="5.5" cy="-1.5" r="3.5" fill="#6bc5e8" />
  <rect x="4" y="-2.5" width="4" height="1.5" rx="0.5" fill="#ff4b82" />
  <path d="M 2.5 -1.5 Q 0 -1 0 2 Q 1 3 2 1 Z" fill="#e6a15c" />
</g>
"""

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
    {''.join(grid_rects)}
    <g class="slalom-runner">
      {vector_rider_sprite}
    </g>
  </g>
</svg>"""

os.makedirs("dist", exist_ok=True)
with open("dist/github-snowboard-slalom.svg", "w") as f:
    f.write(svg_output)
