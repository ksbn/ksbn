import os
import requests

USERNAME = os.getenv("GITHUB_REPOSITORY_OWNER", "ksbn")
TOKEN = os.getenv("GITHUB_TOKEN")

# Fetch contribution data from GitHub GraphQL API
query = """
query($user: String!) {
  user(login: $user) {
    contributionsCollection {
      contributionCalendar {
        weeks {
          contributionDays {
            color
            contributionCount
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

# Snow palette mapping
def get_snow_color(count):
    if count == 0: return "#ebedf0"  # Snow Base
    if count < 3:  return "#b6e3f4"  # Light Ice
    if count < 6:  return "#6bc5e8"  # Mid Powder
    if count < 9:  return "#2ca0d2"  # Deep Slope
    return "#007bb6"                 # Glacier Blue

# Build SVG grid
svg_cells = ""
for x, week in enumerate(weeks):
    for y, day in enumerate(week["contributionDays"]):
        color = get_snow_color(day["contributionCount"])
        svg_cells += f'<rect x="{x * 13}" y="{y * 13}" width="10" height="10" rx="2" fill="{color}" />\n'

svg_content = f"""<svg width="700" height="110" xmlns="http://www.w3.org/2000/svg">
  <style>
    @keyframes slalom {{
      0%   {{ transform: translate(10px, 0px); }}
      25%  {{ transform: translate(180px, 40px); }}
      50%  {{ transform: translate(350px, 15px); }}
      75%  {{ transform: translate(520px, 60px); }}
      100% {{ transform: translate(670px, 20px); }}
    }}
    .snowboarder {{
      animation: slalom 8s ease-in-out infinite alternate;
      font-size: 16px;
    }}
  </style>
  <g transform="translate(10, 10)">
    {svg_cells}
    <text class="snowboarder" x="0" y="15">🏂‍♀️</text>
  </g>
</svg>"""

os.makedirs("dist", exist_ok=True)
with open("dist/github-snowboard-slalom.svg", "w") as f:
    f.write(svg_content)
