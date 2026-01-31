"""
Cours 004: Securite Web - XSS via innerHTML
============================================
CORRIGE - Solution Complete

Ce fichier genere une page HTML SECURISEE.
Compare avec exercice.py pour voir les differences.

La correction utilise escapeHtml() sur toutes les variables.
"""

import os
from pathlib import Path


def get_secure_html() -> str:
    """
    Genere le HTML SECURISE contre le XSS.

    Corrections appliquees:
    1. Fonction escapeHtml() ajoutee
    2. Toutes les variables echappees avec escapeHtml()
    """

    return '''<!DOCTYPE html>
<html>
<head>
    <title>Cours 004 - XSS Demo (SECURISE)</title>
    <style>
        body {
            font-family: 'Courier New', monospace;
            background: #0a0a0f;
            color: #00ff41;
            padding: 20px;
            max-width: 800px;
            margin: 0 auto;
        }
        h1 { color: #00ff41; }
        h2 { color: #ffaa00; }
        .container {
            background: #1a1a2e;
            border: 1px solid #333;
            padding: 20px;
            margin: 20px 0;
            border-radius: 4px;
        }
        .activity-item {
            padding: 10px;
            border-bottom: 1px solid #333;
            display: flex;
            gap: 20px;
        }
        .activity-action { color: #00aaff; }
        .activity-resource { color: #ffaa00; }
        .activity-user { color: #ff4141; }
        .success {
            background: rgba(0, 255, 65, 0.2);
            border: 1px solid #00ff41;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }
        code {
            background: #333;
            padding: 2px 6px;
            border-radius: 3px;
        }
        pre {
            background: #1a1a2e;
            padding: 15px;
            overflow-x: auto;
            border-radius: 4px;
        }
        .escaped {
            color: #888;
            font-style: italic;
        }
    </style>
</head>
<body>
    <h1>Cours 004: XSS SECURISE</h1>

    <div class="success">
        <strong>SECURISE:</strong> Cette page utilise escapeHtml() pour
        empecher l'injection XSS. Aucune alerte ne devrait apparaitre!
    </div>

    <h2>Actions Recentes (Section Securisee)</h2>
    <div class="container" id="recent-actions">
        Chargement...
    </div>

    <h2>Code Securise</h2>
    <div class="container">
        <pre>
// Fonction d'echappement HTML
function escapeHtml(text) {
    if (text === null || text === undefined) return '';
    const div = document.createElement('div');
    div.textContent = String(text);
    return div.innerHTML;
}

// Utilisation securisee
actionsContainer.innerHTML = data.recent_actions.map(action => `
    &lt;div class="activity-item"&gt;
        &lt;span&gt;${escapeHtml(action.action_type)}&lt;/span&gt;
        &lt;span&gt;${escapeHtml(action.resource)}&lt;/span&gt;
        &lt;span&gt;${escapeHtml(action.admin_user)}&lt;/span&gt;
    &lt;/div&gt;
`).join('');
        </pre>
    </div>

    <h2>Donnees Malveillantes (Neutralisees)</h2>
    <div class="container">
        <p>L'attaquant a tente d'injecter:</p>
        <pre id="malicious-data"></pre>
        <p class="escaped">Le code malveillant est affiche comme du texte, pas execute!</p>
    </div>

    <script>
    // ================================================================
    // CODE SECURISE
    // ================================================================

    // CORRECTION: Fonction d'echappement HTML
    function escapeHtml(text) {
        if (text === null || text === undefined) return '';
        const div = document.createElement('div');
        div.textContent = String(text);
        return div.innerHTML;
    }

    // Simulation de donnees avec contenu malveillant
    const serverData = {
        recent_actions: [
            {
                action_type: 'LOGIN',
                resource: '/admin/dashboard',
                admin_user: 'admin@example.com'
            },
            {
                // TENTATIVE D'ATTAQUE - sera neutralisee!
                action_type: '<img src=x onerror="alert(\'XSS Attack!\')">',
                resource: '<script>alert("Malicious")</script>',
                admin_user: '"><script>alert(3)</script><span class="'
            },
            {
                action_type: 'UPDATE',
                resource: '/api/users/123',
                admin_user: 'admin@example.com'
            }
        ]
    };

    document.getElementById('malicious-data').textContent =
        JSON.stringify(serverData.recent_actions[1], null, 2);

    // ================================================================
    // FONCTION SECURISEE
    // ================================================================

    function displayRecentActions(data) {
        const actionsContainer = document.getElementById('recent-actions');

        // SECURISE: escapeHtml() sur chaque variable!
        actionsContainer.innerHTML = data.recent_actions.map(action => `
            <div class="activity-item">
                <span class="activity-action">${escapeHtml(action.action_type)}</span>
                <span class="activity-resource">${escapeHtml(action.resource)}</span>
                <span class="activity-user">${escapeHtml(action.admin_user)}</span>
            </div>
        `).join('');
    }

    // Executer au chargement
    displayRecentActions(serverData);

    </script>

    <h2>Resultat</h2>
    <div class="success">
        <p><strong>Le code malveillant est affiche comme du texte!</strong></p>
        <p>Tu peux voir les balises &lt;script&gt; et &lt;img&gt; dans la liste,
        mais elles ne sont pas executees.</p>
        <p>C'est exactement ce qu'on veut: les donnees sont affichees en securite.</p>
    </div>

</body>
</html>
'''


def run_secure_demo():
    """Genere la page HTML securisee et affiche l'explication."""

    print("="*60)
    print("COURS 004 - CORRIGE - XSS Securise")
    print("="*60)
    print()

    # Generer le fichier HTML
    output_file = Path(__file__).parent / "corrige_xss_demo.html"
    html_content = get_secure_html()

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"Fichier genere: {output_file}")
    print()

    # Verifier que la correction est bien appliquee
    print("Verification de securite:")
    print("-" * 40)

    checks = []

    if 'function escapeHtml' in html_content:
        print("✓ Fonction escapeHtml() presente")
        checks.append(True)
    else:
        print("✗ Fonction escapeHtml() manquante")
        checks.append(False)

    if '${escapeHtml(action.action_type)}' in html_content:
        print("✓ action_type echappe")
        checks.append(True)
    else:
        print("✗ action_type non-echappe")
        checks.append(False)

    if '${escapeHtml(action.resource)}' in html_content:
        print("✓ resource echappe")
        checks.append(True)
    else:
        print("✗ resource non-echappe")
        checks.append(False)

    if '${escapeHtml(action.admin_user)}' in html_content:
        print("✓ admin_user echappe")
        checks.append(True)
    else:
        print("✗ admin_user non-echappe")
        checks.append(False)

    print()
    print("="*60)

    if all(checks):
        print("✅ CODE SECURISE - Toutes les variables sont echappees!")
    else:
        print("❌ Code incomplet - Certaines variables ne sont pas echappees")

    print("="*60)
    print()

    show_explanation()

    print(f"Ouvre dans ton navigateur: {output_file.absolute()}")


def show_explanation():
    """Affiche l'explication de la correction."""
    print("""
============================================================
EXPLICATION DE LA CORRECTION
============================================================

PROBLEME:
---------
innerHTML injecte du HTML brut dans le DOM:

    element.innerHTML = '<script>alert(1)</script>';
    // Le script est EXECUTE!

SOLUTION:
---------
Echapper les caracteres speciaux HTML:

    < devient &lt;
    > devient &gt;
    & devient &amp;
    " devient &quot;

CODE:
-----
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;  // textContent echappe!
    return div.innerHTML;    // Retourne le texte echappe
}

AVANT:
------
    ${action.action_type}
    // '<script>alert(1)</script>' -> EXECUTE!

APRES:
------
    ${escapeHtml(action.action_type)}
    // '&lt;script&gt;alert(1)&lt;/script&gt;' -> AFFICHE!

============================================================
""")


if __name__ == "__main__":
    run_secure_demo()
