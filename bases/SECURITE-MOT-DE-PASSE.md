# Mot de passe des bases documentaires — décision du propriétaire

## Qui définit le mot de passe ?

**Le responsable du dépôt MAJ**, et jamais l'utilisateur qui installe le logiciel.
Le logiciel ne propose pas de créer son propre mot de passe pour débloquer
une base. Il demande le **mot de passe communiqué par l'administrateur**.

Le même secret sert à déchiffrer un pack constructeur autorisé téléchargé
sur GitHub MAJ, ou un pack chiffré importé hors ligne. Une saisie erronée
n'installe rien et laisse la base existante intacte.

## Définition du secret lors de la publication

1. Choisir personnellement un secret fort d'au moins 12 caractères, **hors
   de ChatGPT**, de l'historique Git et des fichiers de documentation.
2. Dans le dépôt GitHub dont tu administres les secrets de construction (par exemple le dépôt du programme), aller dans
   **Settings → Secrets and variables → Actions → New repository secret**.
3. Nommer le secret `MEMS_DOCUMENTARY_PUBLISH_PASSWORD`.
4. L'outil `tools/pack_mems_documentary.py` du dépôt du programme récupère
   ce secret uniquement depuis la variable d'environnement homonyme lors
   du chiffrement du pack. Il n'est pas enregistré dans le pack ni dans
   le manifeste. **Aucun mot de passe fixe n'est livré avec l'application.**
5. Communiquer ce mot de passe, par un canal privé, uniquement aux
   personnes autorisées à installer les bases.

La GitHub Release ne doit recevoir que le **fichier MEMSDOC1 chiffré**
accompagné de son SHA-256 et de ses métadonnées. La vérification AES-256-GCM
fait échouer toute installation avec un secret différent.

## Limites et publication

Le mot de passe administrateur sert à contrôler l'accès au contenu du pack,
pas à protéger une base déjà installée par un mécanisme de droits système.
Une personne autorisée peut toujours consulter les données qu'elle a
légitimement installées. Pour révoquer l'accès à une future version,
il faudra chiffrer le nouveau pack avec un nouveau secret.

**Le chiffrement ne remplace pas l'autorisation de redistribution** des
documents constructeurs Rover. Les bases françaises et anglaises ne doivent
pas être publiées sur une Release publique sans droits confirmés.

Le contenu français RCL0193FRE, le chapitre AKM7169FRE SPi et le corpus
anglais AKM7169ENG ont des statuts différents ; aucune source manquante
ou donnée non relue ne doit être inventée pour afficher une base « complète ».
