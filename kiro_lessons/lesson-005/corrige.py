"""
Cours 005: Clean Code - Code Mort
=================================
CORRIGE - Solution Complete

Ce fichier montre le code APRES suppression du code mort.
Compare avec exercice.py pour voir la difference.
"""


# ============================================================================
# CODE PROPRE - SANS CODE MORT
# ============================================================================

def get_html_clean() -> str:
    """
    Retourne du HTML propre, sans code mort.

    CORRECTION APPLIQUEE:
    - Le code inutile a ete supprime
    - Ou remplace par un vrai status check
    """

    return '''
<!DOCTYPE html>
<html>
<head>
    <title>Admin Dashboard</title>
</head>
<body>
    <div class="admin-container">
        <h1>Dashboard</h1>
        <div id="admin-status">Loading...</div>
    </div>

    <footer class="admin-footer">
        <span id="last-updated">--:--:--</span>

        <script>
            // Script de mise a jour du footer
            document.getElementById('last-updated').textContent =
                new Date().toLocaleTimeString();
        </script>
    </footer>

    <script>
        // =============================================
        // OPTION A: Code mort SUPPRIME (recommande)
        // =============================================
        // Le code suivant a ete supprime car il ne faisait rien:
        //
        // setTimeout(() => {
        //     document.querySelector('.admin-footer script').click();
        // }, 1000);
        //
        // Raison: .click() sur <script> n'a aucun effet


        // =============================================
        // OPTION B: Remplace par un VRAI status check
        // =============================================
        setTimeout(() => {
            // Vrai status check - appel API
            fetch('/api/admin/health')
                .then(response => {
                    if (!response.ok) throw new Error('Health check failed');
                    return response.json();
                })
                .then(data => {
                    const statusEl = document.getElementById('admin-status');
                    if (data.status === 'healthy') {
                        statusEl.textContent = 'System OK';
                        statusEl.style.color = '#00ff41';
                    } else {
                        statusEl.textContent = 'System Warning';
                        statusEl.style.color = '#ffaa00';
                    }
                })
                .catch(error => {
                    const statusEl = document.getElementById('admin-status');
                    statusEl.textContent = 'System Error';
                    statusEl.style.color = '#ff4141';
                    console.error('Health check error:', error);
                });
        }, 1000);
    </script>
</body>
</html>
'''


def analyze_clean_code():
    """Analyse le code propre pour confirmer qu'il n'y a plus de code mort."""

    print("="*60)
    print("COURS 005 - CORRIGE - Analyse de Code")
    print("="*60)
    print()

    html_content = get_html_clean()

    issues = []

    # Verifier que le code mort a ete supprime
    if "script').click()" in html_content or 'script").click()' in html_content:
        # Verifier si c'est dans un commentaire
        lines = html_content.split('\n')
        for line in lines:
            if "script').click()" in line and '//' not in line.split("script')[0]"):
                issues.append("Code mort encore present")

    if issues:
        print("❌ Code mort encore present!")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✅ Aucun code mort detecte!")
        print()
        print("Le code problematique a ete:")
        print("  - Soit SUPPRIME (Option A)")
        print("  - Soit REMPLACE par un vrai status check (Option B)")

    print()
    print("="*60)
    print("✅ CODE PROPRE - Pas de code mort!")
    print("="*60)

    return len(issues) == 0


def show_explanation():
    """Affiche l'explication de la correction."""
    print("""
============================================================
EXPLICATION DE LA CORRECTION
============================================================

PROBLEME:
---------
Le code suivant ne faisait RIEN:

    setTimeout(() => {
        document.querySelector('.admin-footer script').click();
    }, 1000);

Pourquoi?
- .click() sur un <script> n'a aucun effet
- Les scripts s'executent au chargement, pas au clic
- C'etait probablement un reste de debug

SOLUTION A - SUPPRIMER (Recommande):
------------------------------------
Simplement supprimer les 3-4 lignes de code mort.
C'est la solution la plus propre si le code n'est pas necessaire.

SOLUTION B - REMPLACER:
-----------------------
Si l'intention etait de faire un "status check", remplacer par:

    setTimeout(() => {
        fetch('/api/admin/health')
            .then(r => r.json())
            .then(data => updateStatus(data));
    }, 1000);

LECON:
------
- Toujours questionner le code existant
- Si un code ne fait rien, le supprimer
- Les commentaires peuvent mentir - verifier le comportement reel
============================================================
""")


if __name__ == "__main__":
    analyze_clean_code()
    print()
    show_explanation()
