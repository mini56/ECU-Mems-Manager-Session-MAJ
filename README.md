# ECU MEMS Manager SESSION — mises à jour

Ce dépôt regroupe **les mises à jour du programme** et, à terme, **une base documentaire complète par langue**.

## Avancement vérifié — 12 novembre 2026

**Mise à jour du 13 novembre 2026 :** [SESSION 140 de test disponible](https://github.com/mini56/ECU-Mems-Manager-Session-MAJ/releases/tag/mems-session-140-admin-encrypted-documentary-TEST). L'importation de bases non chiffrées et la création d'un mot de passe par l'utilisateur ont été supprimées. Windows a validé le chiffrement AES-GCM et l'installation sur données de test. Les packs des manuels constructeurs ne sont pas encore publiés, et le secret `MEMS_DOCUMENTARY_PUBLISH_PASSWORD` doit être accessible comme **Repository secret Actions** du workflow de fabrication.


- **RCL0193FRE français** : base SQLite locale relue disponible au propriétaire, **371 pages, 5 958 entrées, 325 fac-similés**. Détails : [bases/fr/](bases/fr/).
- **AKM7169FRE français** : uniquement les **20 pages originales du chapitre MEMS SPi** ; autres chapitres non retrouvés ; OCR non entièrement relu.
- **AKM7169ENG anglais** : base SQLite source originale reconstruite et testée, **482 pages**. Détails : [bases/en/](bases/en/).
- **MEMS Manager SESSION 139** : **[Setup Windows de test publié](https://github.com/mini56/ECU-Mems-Manager-Session-MAJ/releases/tag/mems-session-139-documentary-offline-TEST)**. Compilation, installation et démarrage Windows réussis. **Attention : ce premier test proposait encore un mot de passe choisi par l'utilisateur et autorisait un ZIP local en clair ; il ne constitue donc PAS la version sécurisée définitive des mises à jour.** Une révision du programme supprime ces deux possibilités et exige les packs chiffrés par l'administrateur ; elle reste en validation Windows. Aucune documentation constructeur n'est embarquée dans ce Setup.
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

**Décision définitive :** le mot de passe est choisi **uniquement par le propriétaire/administrateur du projet** lors de la création des packs chiffrés. L'utilisateur final n'a aucun bouton pour créer son propre mot de passe : il saisit le secret que l'administrateur lui a communiqué. Le logiciel vérifie ce secret par l'authentification AES-GCM du pack ; un ZIP documentaire non chiffré n'est pas installable depuis l'interface. Voir [règles et configuration du secret](bases/SECURITE-MOT-DE-PASSE.md).


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

### Packs FR et EN — préparation du 13 novembre 2026

La base française à deux documents (RCL0193FRE + AKM7169FRE SPi, 391 pages, 6 387 entrées, 345 images) et la base anglaise AKM7169ENG (482 pages) ont été chiffrées au format `MEMSDOC1` avec le **secret administrateur GitHub MAJ**. Les fichiers ont passé les contrôles AES-GCM et SHA-256.

Une **Release brouillon** `mems-documentary-fr-en-20261113` existe ; [création vérifiée sur GitHub Actions](https://github.com/mini56/ECU-Mems-Manager-Session-MAJ/actions/runs/43403631823). Le workflow d'activation est prêt, et son [test FR/EN est vert](https://github.com/mini56/ECU-Mems-Manager-Session-MAJ/actions/runs/43403956332).

**Les fichiers chiffrés ne sont pas encore hébergés sur cette Release ; le manifeste reste donc à `available: false`.** Il faut établir l'autorisation de redistribution des manuels constructeurs avant toute publication publique. Le chiffrement n'est pas une licence.
