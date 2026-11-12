# ECU MEMS Manager SESSION — mises à jour

Ce dépôt regroupe **les mises à jour du programme** et, à terme, **une base documentaire complète par langue**.

## Organisation

- `bases/fr/` — Français, priorité n° 1 (édition constructeur française)
- `bases/en/` — Anglais, édition constructeur originale
- `bases/pt/` — Portugais
- `bases/es/` — Espagnol
- `bases/it/` — Italien
- `bases/de/` — Allemand
- `setups/` — publication des installateurs Windows via GitHub Releases
- `manifest.json` — état de disponibilité et contrôle des mises à jour

Chaque dossier linguistique accueillera une **base SQLite indépendante**, accompagnée de son fichier de provenance et de son empreinte SHA-256. Les langues ne seront **jamais mélangées** dans une même base distribuée.

**À ce stade, aucun pack documentaire ni Setup n'est encore publié dans ce dépôt.** Les entrées du manifeste ont `available: false`. Le programme ne doit jamais télécharger un fichier non validé.

### Protection des sources RAVE

La présence d'une édition RAVE ne donne pas automatiquement le droit de redistribuer son PDF ou les données extraites. **Vérifier les droits de redistribution avant tout dépôt public**. Ne pas placer de PDF constructeur ou de base documentaire dans ce dépôt public sans cette vérification.

### Publication d'une base

1. Identifier la langue, l'édition du manuel, sa révision et le SHA-256 du PDF source.
2. Construire et contrôler intégralement la base dans un chantier distinct.
3. Vérifier la conformité technique et la couverture, sans substitution de mots ni mélange de langues.
4. Publier une version du pack sur une GitHub Release autorisée, avec son SHA-256.
5. Renseigner le manifeste uniquement **après** vérification de l'URL, du hash et du pack.

Le programme installé doit aussi proposer une **installation hors ligne** des packs vérifiés.

Le code source du programme reste dans [ECU-Mems-Manager-Session](https://github.com/mini56/ECU-Mems-Manager-Session). Ce dépôt ne contient pas son code source.
