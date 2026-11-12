# Inventaire des bases MEMS Manager SESSION

Ce document identifie les données **effectivement présentes dans le code et ses compilations**, avant toute externalisation.

**Règle de sécurité : seules les bases documentaires autonomes peuvent devenir des packs linguistiques.**
Aucune mise à jour de la langue ne doit écraser une base ECU, les historiques, le moteur expert, les fiches techniques ou un index de diagnostic.

## 1 — Base documentaire Rover anglaise : EXISTANTE, RÉCUPÉRABLE

- Source : `mini56/ECU-Mems-Manager-Session`, branche `integration-rover-482-session-20261111`.
- Fragments d'origine : `database/documentary/parts/part-000.gz.part` à `part-028.gz.part`, **29 fragments**.
- Compression reconstituée (SHA-256) : `9e2d30ea5e28461c053a99fdf974e8406cdbb4933f30a3e9b0792f9e65aa7572`.
- SQLite anglaise reconstruite (SHA-256 de la SOURCE avant ajout des métadonnées) :
  `dd37296b5d477c4124133f51e96691858c0ae4746d42c3e4478bf6003a9445bb`.
- Taille SQLite source : **21 508 096 octets**.
- Manuel constructeur anglais de référence : `AKM7169ENG.pdf`, 482 pages.
- Source PDF SHA-256 : `c8bbb30d7d5a52932e7f92723ba5dc70520012ac3ceac21d19ab0a39b4d4c4e0`.
- Comptages vérifiés : 482 pages, 336 procédures, 5 055 étapes, 630 valeurs, 316 illustrations.
- Reconstitution : `tools/build_rover_session_documentary.py` depuis le dépôt du programme et le PDF exact.
- Vérification de la reconstruction et du lecteur : GitHub Actions `43213015415`, succès.
- Fichier de distribution : `database/documentary/rover_482.sqlite` (copie dérivée de la source dont le SHA est différent après ajout des métadonnées).

**État dans le dépôt MAJ : source récupérable et identifiée ; fichier SQLite NON encore publié.**
Le fichier exact de distribution sera publié uniquement après contrôle technique, contrôle des droits de redistribution et test de chargement dans MEMS Manager SESSION.

## 2 — Autres bases et ressources existantes

| Base ou ressources | Emplacement actuel | Usage | À déplacer dans un pack linguistique ? |
| --- | --- | --- | --- |
| `MEMSLibrary_Pack_001/knowledge.sqlite` | Distribution historique | Bibliothèque documentaire RAVE, 47 documents et recherche IA | **Pas encore** : comporte un lecteur distinct et un ancien routage IA ; auditer le schéma et les interactions |
| `database/expert/ia_mems_reference_r20.sqlite` | Distribution du programme | Moteur expert IA MEMS et réponses liées aux ECU | **NON** : maintenir avec le diagnostic |
| `ecu_mems_reference_r5.sqlite` | Cache local `AppLocalDataLocation/reference` | Référence et fiches MEMS 1.2/1.3/1.6/1.9 ; générée des sources `database/reference/` | **NON** : maintenir le fonctionnement existant |
| `mems_global_search_r1.sqlite` | Cache local de recherche | Index dérivé de la référence ECU et des fiches | **NON** : index local dérivé, pas de donnée à télécharger séparément |
| `ecu_mems_manager.sqlite` | `AppLocalDataLocation/database` | Données utilisateur, ECU, sessions, mesures et historiques | **JAMAIS** : base personnelle à préserver |
| Fiches `database/reference/fiches/mems_*.LANG.xml.qz64` | Sources du programme | Fiches ECU disponibles en FR/EN/PT/ES/IT/DE | **NON** : elles sont déjà localisées, séparées des gros manuels RAVE |
| Enrichissements français `RCL0193FRE` | `database/reference/research_enrichment_1790...1860.qz64` | Référence technique issue d'un autre manuel français | **NON**, ce n'est pas le manuel français `AKM7169FRE` attendu |

## 3 — Séparation imposée à MEMS Manager SESSION

La page **Base de données** et l'**IA documentaire** doivent sélectionner une même base documentaire externe par langue. Le diagnostic ECU connecté, les références MEMS, les connaissances expertes et les données utilisateur gardent leurs propres accès et chemins.

Une langue absente ne déclenche jamais le remplacement d'un fichier expert ou d'une base utilisateur. Aucune réponse documentaire ne doit être silencieusement tirée d'une ancienne base différente.

Le choix de la langue doit pointer vers un **pack documentaire complet et vérifié**, installé localement avec sauvegarde et retour arrière. Une nouvelle base anglaise ne doit pas effacer la précédente tant que la validation n'a pas réussi.

## 4 — Distribution et droits

Le dépôt `ECU-Mems-Manager-Session-MAJ` est **public**. Vérifier les droits de redistribution des manuels et de leurs transcriptions avant d'ajouter les SQLite documentaires aux Releases. Les métadonnées et inventaires techniques ne rendent pas la base automatiquement téléchargeable. Les fichiers destinés au diagnostic ne sont pas inclus dans les mises à jour de documentation par langue.

Date de l'inventaire : 12 novembre 2026.
