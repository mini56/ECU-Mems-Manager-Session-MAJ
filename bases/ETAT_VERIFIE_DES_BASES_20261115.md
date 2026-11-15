# État vérifié des bases de données — 15 novembre 2026

**La seule source de vérité pour SESSION est [le catalogue MAJ officiel](../manifest.json).**
Ce suivi ne fournit aucun pack intermédiaire et ne remplace pas les versions du manifeste.

## Bases effectivement publiées et proposées par SESSION

| Langue | Version officielle | Documents | Pages | Publication |
|---|---|---:|---:|---|
| Français | `fr-mems-doc-fr-6-20261115` | **6** | **797** | [Release officielle FR](https://github.com/mini56/ECU-Mems-Manager-Session-MAJ/releases/tag/mems-doc-fr-6-20261115) |
| Anglais | `en-mems-rave-en-47-20261114-private` | **48** | **1 841** | [Release officielle EN](https://github.com/mini56/ECU-Mems-Manager-Session-MAJ/releases/tag/mems-rave-en-47-20261114-private) |
| PT, ES, IT, DE | Non disponibles | 0 | 0 | Pas de base publiée |

**Installation sur le PC de l'utilisateur : non vérifiée.** La publication officielle ne signifie pas que SESSION a téléchargé la base sur tous les ordinateurs.

### Documents contenus dans l'unique base française publiée

| Document | Pages | Statut |
|---|---:|---|
| `AKM7169FRE` | 20 | Inclus dans la base FR officielle |
| `DOC_CDXN010F_3BC9A3B46484` | 74 | Inclus dans la base FR officielle |
| `DOC_ELXN010F_91EFD3F4C8DA` | 210 | Inclus dans la base FR officielle |
| `DOC_HR01795F_96EA0F759615` | 98 | Inclus dans la base FR officielle |
| `DOC_IR07301F_EEDC3668AA41` | 24 | Inclus dans la base FR officielle |
| `RCL0193FRE` | 371 | Inclus dans la base FR officielle |
| **Total** | **797** | **6 documents** |

La base complète publiée comprend **751 illustrations**, dont celles des quatre PDF ajoutés, ainsi que **417 opérations et 3 415 étapes** du manuel préexistant préservées. Les textes issus de reconnaissance OCR non relus restent marqués `review_required` et ne sont pas considérés comme des instructions de réparation validées.

Pack chiffré unique : [`MEMS-DOC-FR-RAVE-6-DOCUMENTS-20261115.encrypted`](https://github.com/mini56/ECU-Mems-Manager-Session-MAJ/releases/download/mems-doc-fr-6-20261115/MEMS-DOC-FR-RAVE-6-DOCUMENTS-20261115.encrypted).

SHA-256 du pack officiel : `ab260c28b97bff3f88509fc5a00ed4feed983019c1c3f16a14d33be69118e8c7`.

### Contrôles réellement réussis avant publication

- Restitution exacte du ZIP source utilisateur de **46 940 984 octets**, SHA-256 `7e9cabd6cfe0584eb88dfb786b2441b6f20d706916732caa74c0d7303485b41a`.
- Construction d'**un seul pack complet de 6 documents**, conservation sans modification des deux anciens documents, 797 pages, 751 images, 417 opérations et 3 415 étapes.
- Contrôle des pages et SHA-256 des images, intégrité SQLite, références de provenance, FTS français et chiffrement AES-256-GCM.
- **Installation réelle de la nouvelle base chiffrée dans le lecteur natif SESSION sous Windows**, vérification du mauvais mot de passe et des recherches dans l'ancien manuel RAVE (« joint de culasse ») et dans un nouveau (« autoradio »).
- Publication de la Release et modification du **manifeste MAJ officiel** uniquement après validation Windows.

[Voir la chaîne GitHub complète, réussie](https://github.com/mini56/ECU-Mems-Manager-Session-MAJ/actions/runs/43715508773).

### Documents RAVE français encore absents

Les six documents ci-dessous **ne sont pas inclus dans la base officielle** et restent protégés sous leur forme d'origine. Le nombre de pages du CD n'est pas le nombre de documents publiés.

| Fichier d'origine | Pages | État |
|---|---:|---|
| `cdxn980f.pdf` | 76 | Source reçue, non extraite |
| `ellt990f.pdf` | 214 | Source reçue, non extraite |
| `libxn_f.pdf` | 1 | Source reçue, non extraite |
| `mcxn980f.pdf` | 2 | Source reçue, non extraite |
| `prxn990f.pdf` | 29 | Source reçue, non extraite |
| `roxn990f.pdf` | 210 | Source reçue, non extraite |
| **Total restant** | **532** | **6 documents** |

**Objectif ultérieur pour la collection complète du CD français** : 11 documents RAVE de 1 309 pages, plus `AKM7169FRE` de 20 pages = **12 documents, 1 329 pages**, à condition d'obtenir un contenu lisible, d'éviter les doublons et de valider chaque source. **Ce total est un objectif, pas un résultat livré.**

### Règle de distribution et état local

Le site MAJ propose à SESSION **une seule version cumulative par langue**. Les anciens candidats, brouillons, ZIP de complément et outils locaux **ne sont pas nécessaires à l'installation de la version publiée**, et ne doivent pas être confondus avec la base officielle.

Pour installer normalement : **SESSION → Base de données → Mise à jour → Vérifier les mises à jour → Télécharger la base**, puis saisir le mot de passe administrateur. SESSION doit afficher la version installée à l'issue de la mise à jour et garder une sauvegarde de la précédente base. **L'installation sur un PC utilisateur devra être constatée sur ce PC.**
