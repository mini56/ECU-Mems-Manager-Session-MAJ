# ECU MEMS Manager SESSION — mises à jour

Ce dépôt regroupe **les mises à jour du programme** et, à terme, **une base documentaire complète par langue**.

## Avancement vérifié — 12 novembre 2026

- **RCL0193FRE français** : base SQLite locale relue disponible au propriétaire, **371 pages, 5 958 entrées, 325 fac-similés**. Détails : [bases/fr/](bases/fr/).
- **AKM7169FRE français** : uniquement les **20 pages originales du chapitre MEMS SPi** ; autres chapitres non retrouvés ; OCR non entièrement relu.
- **AKM7169ENG anglais** : base SQLite source originale reconstruite et testée, **482 pages**. Détails : [bases/en/](bases/en/).
- **MEMS Manager SESSION** : installateur documentaire ZIP local avec mot de passe et sauvegarde testé sur des données synthétiques ; un vrai **Setup Windows 139** est en cours de contrôle sur [GitHub Actions du programme](https://github.com/mini56/ECU-Mems-Manager-Session/actions).
- **Téléchargement automatisé depuis ce site** : **aucun pack activé pour le moment**, aucun fichier constructeur public, le manifeste indique encore `available: false`.

Les sources originales des manuels sont soumises aux droits de diffusion. La préparation d'une SQLite ne prouve pas l'autorisation de la publier sur ce dépôt public. Le site ne présentera aucun fichier absent comme téléchargeable et le bouton du logiciel ne proposera pas d'installation qui ne fonctionne pas.

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

**IMPORTANT — RAVE n'est qu'une source parmi d'autres.** Une base `fr` pourra contenir RAVE et d'autres manuels constructeur, bulletins ou fiches techniques, avec des identifiants de document, révisions, pages et provenances distincts. L'ajout d'un nouveau document ne doit jamais écraser les précédents. Voir [architecture multidocuments](bases/ARCHITECTURE-MULTIDOCUMENTS.md).

**À ce stade, aucun pack documentaire ni Setup n'est encore publié dans ce dépôt.** Les entrées du manifeste ont `available: false`. Le programme ne doit jamais télécharger un fichier non validé.

### Protection par mot de passe — même principe que KALONÉO

**Exigence retenue, à implémenter dans MEMS Manager SESSION :**

- Télécharger le pack de la langue choisie depuis ce dépôt de mises à jour, puis vérifier sa taille et son **SHA-256**.
- Demander **un mot de passe avant toute installation ou mise à jour** d'une base documentaire, y compris lors d'un import hors ligne.
- Refuser un mot de passe absent ou incorrect, sans modifier ni supprimer la base déjà installée ; même règle pour un lancement silencieux.
- Ne jamais enregistrer de mot de passe en clair dans le code, le manifeste, les GitHub Releases ou les journaux. Un secret de publication reste uniquement côté construction.
- Ne jamais remplacer la base en cours avant vérification intégrale de l'intégrité SQLite, de la langue, de la provenance et du SHA-256. Installation atomique avec restauration en cas d'échec.
- **Ne pas demander de mot de passe pour consulter** une base déjà installée : il protège l'installation et les mises à jour, pas la recherche documentaire.
- Pour que le mot de passe protège aussi le contenu téléchargeable d'un dépôt public, publier uniquement des **packs chiffrés et authentifiés** (et non des SQLite ou ZIP lisibles), avec vérification à l'import. Le format cryptographique exact doit être implémenté et testé avant publication.

Ce document définit le comportement **attendu** ; aucun mécanisme d'installation avec mot de passe n'est encore opérationnel dans MEMS Manager SESSION. Les bases sont encore toutes indisponibles dans le manifeste.

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
