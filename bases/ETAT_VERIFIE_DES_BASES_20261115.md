# État vérifié des bases documentaires — 15 novembre 2026

> **Document de suivi, pas un pack installable.** Ce document distingue les faits constatés sur GitHub de l'état inconnu des PC utilisateurs. La seule référence pour les téléchargements automatiques SESSION est [`manifest.json`](../manifest.json). Ce compte rendu n'active aucune nouvelle base ni aucune Release.

## 1. Bases **actuellement offertes** par le site MAJ

| Langue | Version publiée selon `manifest.json` | Documents | Pages | Release effectivement publique |
|---|---|---:|---:|---|
| Français | `fr-mems-doc-20261113-139dd8833` | 2 | 391 | [Pack FR](https://github.com/mini56/ECU-Mems-Manager-Session-MAJ/releases/download/mems-doc-20261113-139dd8833/MEMS-DOC-FR-RCL0193FRE-AKM7169FRE-SPI-20261113-MAJ.encrypted) |
| Anglais | `en-mems-rave-en-47-20261114-private` | 48 | 1841 | [Pack EN](https://github.com/mini56/ECU-Mems-Manager-Session-MAJ/releases/download/mems-rave-en-47-20261114-private/MEMS-DOC-EN-RAVE47-AKM7169ENG-PRIVATE.encrypted) |
| PT, ES, IT, DE | Aucune | 0 | 0 | Non disponibles |

L'état **installé sur le PC de l'utilisateur est inconnu**. Un compteur de téléchargements ou une exécution GitHub Actions ne prouve pas qu'un pack ait été installé. Il ne faut ni effacer, ni remplacer, ni inférer l'état des bases locales sans vérification.

### Inventaire exact annoncé pour la base française publiée

| Document | Pages | État |
|---|---:|---|
| `AKM7169FRE` | 20 | Publié FR |
| `RCL0193FRE` | 371 | Publié FR |

SHA-256 du **pack FR publié** : `1686e3f7a8432751695d000897ad6b2412293444444ae983e44d84b083aeda04`.

### Inventaire exact annoncé pour la base anglaise publiée

| Document | Pages |
|---|---:|
| `AKM7169ENG` | 482 |
| `RAVE_CDXN990E` | 41 |
| `RAVE_ELXN970E` | 212 |
| `RAVE_HR01791X` | 90 |
| `RAVE_HR01795E` | 94 |
| `RAVE_IR07102E` | 24 |
| `RAVE_LIBXN` | 1 |
| `RAVE_MCXN960E` | 3 |
| `RAVE_PRXN990E` | 31 |
| `RAVE_R0809BU` | 2 |
| `RAVE_R0962BU` | 1 |
| `RAVE_R2276BU` | 1 |
| `RAVE_R3591BU` | 6 |
| `RAVE_R3814BU` | 1 |
| `RAVE_R4083BU` | 1 |
| `RAVE_R5424BU` | 1 |
| `RAVE_R5898BU` | 1 |
| `RAVE_R6255BU` | 2 |
| `RAVE_R6499BU` | 6 |
| `RAVE_R6529BU` | 1 |
| `RAVE_R6538BU` | 3 |
| `RAVE_R6707BU` | 1 |
| `RAVE_R6957BU` | 2 |
| `RAVE_R7303BU` | 1 |
| `RAVE_R7518BU` | 3 |
| `RAVE_R7532BU` | 2 |
| `RAVE_R7965BU` | 2 |
| `RAVE_R8101BU` | 3 |
| `RAVE_R8381BU` | 1 |
| `RAVE_R8411BU` | 2 |
| `RAVE_R8413BU` | 1 |
| `RAVE_ROXN990E` | 202 |
| `RAVE_RT0003BU` | 2 |
| `RAVE_TB12212E` | 101 |
| `RAVE_TB22382E` | 115 |
| `RAVE_X1885BU` | 1 |
| `RAVE_X6255BU` | 2 |
| `RAVE_X8386BU` | 3 |
| `RAVE_X8408BU` | 5 |
| `RAVE_X8414BU` | 2 |
| `RAVE_X8417BU` | 4 |
| `RAVE_X8419BU` | 1 |
| `RAVE_X8420BU` | 2 |
| `RAVE_X8479BU` | 2 |
| `RAVE_X8499BU` | 3 |
| `RAVE_X8507BU` | 1 |
| `RAVE_XNDB2ENG` | 1 |
| `RCL0193ENG` | 372 |

SHA-256 du **pack EN publié** : `e84f8cf428eb334657edac37761195d5b2a2c9ef4d902231a0578f5501418758`.

Ces inventaires proviennent du manifeste public et des vérifications de publication. Ils n'affirment pas que chaque procédure ou chaque image ait été relue et techniquement validée.

## 2. Documents français reçus, préparés mais **absents du site MAJ**

Les quatre PDF français exportés depuis RAVE ont produit une **base d'ajout distincte**, non une base cumulative officiellement diffusée.

| Fichier RAVE d'origine | Document exporté | Pages du complément | Index et images | Procédures validées ajoutées | État |
|---|---|---:|---|---:|---|
| `ir07301f.pdf` | Équipement audio | 24 | oui | 0 | Complément non publié |
| `elxn010f.pdf` | Bibliothèque électrique | 210 | oui | 0 | Complément non publié |
| `hr01795f.PDF` | Manuel conducteur | 98 | oui | 0 | Complément non publié |
| `cdxn010f.pdf` | Schémas électriques | 74 | oui | 0 | Complément non publié |
| **Total** | | **406** | **406 images** | **0** | **Non disponible via MAJ** |

Vérification directe de `MEMS-RAVE-FR-4-DOCUMENTS-AJOUT.zip` : **4 documents, 406 pages, 406 images, 406 références, zéro procédure et zéro étape**. Taille : 46 940 984 octets ; SHA-256 `7e9cabd6cfe0584eb88dfb786b2441b6f20d706916732caa74c0d7303485b41a`. **NE PAS installer ce ZIP comme remplacement de la base française complète.**

Un essai de fusion ayant donné « six documents, 409 pages » reposait sur une **petite base fictive de trois pages** : ce résultat ne décrit pas la base réelle et **ne valide pas une base de six documents contenant 797 pages**.

## 3. Manuel français de 371 pages : ancien contenu, nouvel OCR non publié

Le manuel `wmxn980f.pdf` (371 pages) correspond au manuel déjà présent sous `RCL0193FRE`. Ne pas le dupliquer.

Un pack **candidat distinct** a été produit avec 371 pages de transcription OCR, dont 325 contenant du texte exploitable ; les transcriptions sont marquées « à vérifier ». Il conserve les deux documents déjà présents. **Ce pack n'est pas la mise à jour officielle du site MAJ.**

- [Release brouillon privée du pack OCR français](https://github.com/mini56/ECU-Mems-Manager-Session-MAJ/releases/tag/untagged-8ee30aaf6e5112990357)
- [Contrôle de création du pack](https://github.com/mini56/ECU-Mems-Manager-Session-MAJ/actions/runs/43702406887)
- [Contrôle d'installation Windows par SESSION](https://github.com/mini56/ECU-Mems-Manager-Session-MAJ/actions/runs/43702732458)

## 4. Autres documents du CD français **pas encore intégrés**

| Document original | Pages | État vérifié |
|---|---:|---|
| `cdxn980f.pdf` | 76 | Absent du pack MAJ FR |
| `ellt990f.pdf` | 214 | Absent du pack MAJ FR |
| `libxn_f.pdf` | 1 | Absent du pack MAJ FR |
| `mcxn980f.pdf` | 2 | Absent du pack MAJ FR |
| `prxn990f.pdf` | 29 | Absent du pack MAJ FR |
| `roxn990f.pdf` | 210 | Absent du pack MAJ FR |
| **Total** | **532** | **Non intégrés** |

Ces fichiers d'origine sont présents dans les archives reçues, mais le contenu de leurs pages protégées n'a pas été transféré dans les bases documentaires publiées.

## 5. Autres versions préparées — ne pas les confondre avec les bases publiques

- [Release brouillon « FR/EN unifiées »](https://github.com/mini56/ECU-Mems-Manager-Session-MAJ/releases/tag/untagged-63a816919739f6c140fd) : **2 documents FR et 48 EN** ; même fonds documentaires que ceux déjà répertoriés, pas les quatre nouveaux documents français.
- [Pack OCR FR en brouillon](https://github.com/mini56/ECU-Mems-Manager-Session-MAJ/releases/tag/untagged-8ee30aaf6e5112990357) : **2 documents FR**, toujours sans les quatre compléments.
- Complément local français de quatre PDF : **4 documents, 406 pages**, non publié, **à ne pas installer seul**.
- Exécutable d'ajout local : ce n'est **pas** un nouveau pack disponible sur MAJ et ce n'est **pas** un contrôle de l'état du PC utilisateur.

## 6. Objectif et conditions de sortie du chantier

**Premier jalon manquant :** construire et valider **un seul pack FR cumulatif**, réunissant les **2 documents et 391 pages existants** + **les 4 documents et 406 pages nouveaux**, soit **6 documents et 797 pages** (sans doublon), avec index, images et procédures antérieures conservés. Ce pack **n'est pas encore disponible dans le manifeste officiel**.

**Collection RAVE FR complète visée :** les 11 documents du CD français (1 309 pages) et le document AKM7169FRE (20 pages), soit **12 documents et 1 329 pages** si les 11 documents sont bien tous distincts. Les six documents absents (532 pages) doivent encore être intégrés : le total de 1 329 pages est **un objectif, pas un résultat existant**.

**Pour publier correctement :** fabriquer un pack FR *complet*, contrôler chaque document, pages, opérations, illustrations, langue, chiffrement et SHA-256 ; tester l'installation avec le lecteur réel de SESSION ; créer une Release appropriée sur MAJ ; **modifier uniquement ensuite** la version, l'URL et l'empreinte dans `manifest.json`. SESSION doit télécharger le pack complet par le mécanisme normal.

**Règle :** ne jamais publier un complément de quatre documents comme s'il s'agissait de la base FR entière, ne pas déclarer « terminé » à partir d'une base synthétique, et ne pas déduire la version installée sur le PC depuis GitHub.
