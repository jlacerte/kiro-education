"""
Cours 005: Clean Code - Code Mort
=================================
EXERCICE - Code a analyser

Niveau: Debutant
Duree: 15-20 minutes

INSTRUCTIONS:
-------------
1. Ce fichier simule du code mort dans une page web
2. Lance le script pour voir l'analyse
3. Identifie pourquoi le code est "mort"
4. Corrige en supprimant ou remplacant le code inutile

Pour lancer l'analyse:
    python exercice.py
"""


# ============================================================================
# SIMULATION DE CODE MORT
# ============================================================================

def get_html_with_dead_code() -> str:
    """
    Retourne du HTML avec du code JavaScript mort.

    LE CODE MORT:
    - document.querySelector('.admin-footer script').click()
    - Appeler .click() sur un <script> ne fait RIEN!

    VOTRE MISSION:
    Identifier pourquoi ce code est inutile.
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
        // CODE MORT CI-DESSOUS - A ANALYSER
        // =============================================

        // Initial status check
        setTimeout(() => {
            document.querySelector('.admin-footer script').click();
        }, 1000);

        // =============================================
        // FIN DU CODE MORT
        // =============================================
    </script>
</body>
</html>
'''


def analyze_dead_code():
    """Analyse le code pour detecter le code mort."""

    print("="*60)
    print("COURS 005 - Analyse de Code Mort")
    print("="*60)
    print()

    html_content = get_html_with_dead_code()

    issues = []

    # Detection du pattern problematique
    print("Recherche de patterns de code mort...")
    print("-" * 40)
    print()

    # Pattern 1: .click() sur script
    if "script').click()" in html_content or 'script").click()' in html_content:
        issues.append({
            'type': 'CODE_MORT',
            'severity': 'MEDIUM',
            'description': "Appel de .click() sur un element <script>",
            'reason': "Les elements <script> ne reagissent pas aux clics",
            'line_hint': "setTimeout(() => { document.querySelector('.admin-footer script').click(); ..."
        })

    # Pattern 2: setTimeout avec code inutile
    if "setTimeout" in html_content and "script').click()" in html_content:
        issues.append({
            'type': 'INEFFICACE',
            'severity': 'LOW',
            'description': "setTimeout execute du code sans effet",
            'reason': "Le delai de 1 seconde ne change rien si le code est inutile",
            'line_hint': "setTimeout(() => { ... }, 1000);"
        })

    # Afficher les resultats
    if issues:
        print(f"🔴 CODE MORT DETECTE ({len(issues)} probleme(s)):")
        print()

        for i, issue in enumerate(issues, 1):
            print(f"  Probleme {i}:")
            print(f"  Type: {issue['type']}")
            print(f"  Severite: {issue['severity']}")
            print(f"  Description: {issue['description']}")
            print(f"  Raison: {issue['reason']}")
            print(f"  Code: {issue['line_hint'][:60]}...")
            print()

        print("="*60)
        print("❌ CODE MORT TROUVE - Supprime le code inutile!")
        print("="*60)
        print()
        print("EXPLICATION:")
        print("-" * 40)
        print("""
  document.querySelector('.admin-footer script').click();

  Ce code tente de "cliquer" sur un element <script>.
  Mais les <script> ne reagissent pas aux clics!

  - Un <script> s'execute au chargement de la page
  - Il n'a pas d'evenement onclick
  - .click() ne fait donc RIEN

  C'est du CODE MORT: du code qui s'execute mais n'a aucun effet.
""")
        print("SOLUTION:")
        print("-" * 40)
        print("""
  Option A: SUPPRIMER le code (recommande)
  -----------------------------------------
  // Supprimer ces lignes:
  setTimeout(() => {
      document.querySelector('.admin-footer script').click();
  }, 1000);

  Option B: REMPLACER par un vrai status check
  ---------------------------------------------
  setTimeout(() => {
      fetch('/api/admin/health')
          .then(r => r.json())
          .then(data => updateStatus(data));
  }, 1000);
""")

    else:
        print("✅ Aucun code mort detecte!")
        print()
        print("="*60)
        print("✅ CODE PROPRE - Bien joue!")
        print("="*60)

    return len(issues) == 0


def demonstrate_dead_code():
    """Demontre pourquoi .click() sur script ne fait rien."""

    print()
    print("="*60)
    print("DEMONSTRATION: Pourquoi .click() sur <script> est inutile")
    print("="*60)
    print()

    print("En JavaScript dans le navigateur:")
    print("-" * 40)
    print("""
  // Ceci NE FAIT RIEN:
  document.querySelector('script').click();

  // Pourquoi?
  // 1. Les <script> n'ont pas de handler onclick par defaut
  // 2. Un script s'execute au chargement, pas au clic
  // 3. .click() declenche un evenement que personne n'ecoute

  // Compare avec un bouton (CA MARCHE):
  document.querySelector('button').click();
  // -> Declenche l'action du bouton!

  // Ou un lien (CA MARCHE):
  document.querySelector('a').click();
  // -> Navigue vers le href!
""")

    print("Elements qui reagissent a .click():")
    print("-" * 40)
    print("  ✓ <button>  - Declenche onclick/submit")
    print("  ✓ <a>       - Navigue vers href")
    print("  ✓ <input>   - Focus/check selon le type")
    print("  ✗ <script>  - RIEN!")
    print("  ✗ <style>   - RIEN!")
    print("  ✗ <div>     - Seulement si onclick defini")
    print()


# ============================================================================
# POINT D'ENTREE
# ============================================================================

if __name__ == "__main__":
    analyze_dead_code()
    demonstrate_dead_code()
