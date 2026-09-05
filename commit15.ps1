Set-Location "c:\Users\Lenovo\Downloads\Rise\ai_placement_system"

$commits = @(
    @{ files = @("templates/base.html"); msg = "feat(ui): establish premium dark design system in base.html with animated floating orbs, shimmer logo, glow-active sidebar, dual-color spinner, and CSS variable glow system" },
    @{ files = @("templates/index.html"); msg = "feat(ui): redesign landing page with cinematic hero section, perspective grid overlay, shimmer CTA button, floating stat badges, and insight dot cycling" },
    @{ files = @("templates/dashboard.html"); msg = "feat(ui): overhaul dataset intelligence dashboard with model pill ring, gradient feature importance bars, 3-col graph gallery, and animated progress bars" },
    @{ files = @("templates/analytics.html"); msg = "feat(ui): rebuild analytics page with live Chart.js doughnut and radar charts driven via data-attributes, animated accuracy bars, and graph duo section" },
    @{ files = @("templates/predict.html"); msg = "feat(ui): redesign predictor with glowing amber sliders, real-time fill tracking, shimmer submit button, and dual-color cinematic loading overlay" },
    @{ files = @("templates/result.html"); msg = "feat(ui): rebuild result page with animated SVG probability ring, gradient verdict headline, per-recommendation accent cards, and career score bar" },
    @{ files = @("templates/history.html"); msg = "feat(ui): modernise history page with live client-side search, probability color badges, expandable recommendation rows, and sticky blur header" },
    @{ files = @("templates/improvement.html"); msg = "feat(ui): redesign improvement hub with goal-based predictor slider, gap analysis display, and glassmorphism growth journey cards" },
    @{ files = @("templates/plan.html"); msg = "feat(ui): overhaul growth plan page with vertical evolutionary timeline, per-week priority cards, and skill selector sidebar with category pills" },
    @{ files = @("templates/projects.html"); msg = "feat(ui): rebuild project vault with domain-filtered sidebar, difficulty badges, tech stack chips, and hover lift glow card system" },
    @{ files = @("templates/skills.html"); msg = "feat(ui): redesign skills page with 6-pillar candidacy framework, CSS variable band colors, and band data via tojson for Chart.js rendering" },
    @{ files = @("templates/suggestions.html"); msg = "feat(ui): overhaul suggestions with platform resource card grid, per-platform accent glow, certification path chips grouped by domain" },
    @{ files = @("templates/mentor.html"); msg = "feat(ui): rebuild mentor panel as administrative authority hub with severity-coded risk list, circular probability badges, and linked report tile" },
    @{ files = @("templates/upload.html", "templates/report.html"); msg = "feat(ui): modernise upload ingestion terminal with drag-drop zone and progress steps; rebuild report center with summary metric cards" },
    @{ files = @("templates/base.html"); msg = "feat(nav): complete sidebar navigation with Skills, Projects, System Report links; fix all active-state route detection for 12 routes" }
)

$i = 1
foreach ($c in $commits) {
    foreach ($f in $c.files) {
        git add $f
    }
    git commit -m $c.msg
    Write-Host "[$i/15] Committed: $($c.msg.Substring(0, [Math]::Min(60, $c.msg.Length)))..." -ForegroundColor Green
    $i++
}

Write-Host "`nPushing to origin/main..." -ForegroundColor Cyan
git push origin main
Write-Host "`nAll 15 commits pushed successfully!" -ForegroundColor Green
