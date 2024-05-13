# REVERS(IBL)E ENGINEERING (0/2)

## Meta

* Chall de **misc** / **prog**
* Difficulté : **Difficile**
* Solution : voir `solution.py`
* Déploiement : voir `../Dockerfile_chapter_0`
* Auteur : _hdrien

## Enoncé

"My game is a lot about footwork. If I move well - I play well."- Joueur de tennis peu connu
Au tennis, des déplacements optimaux font gagner des matchs - même chose ici, mais avec des circuits logiques.

Recevez un circuit logique réversible effectuant une opération sur 3 bits. Renvoyez un circuit optimal équivalent. Plusieurs solutions sont possibles.

#### Précisions :

* Les seules portes logiques réversibles utilisées seront :
    * La porte **NOT** 
    * La porte **CNOT** (controlled NOT)
    * La porte **TOFFOLI**
* La convention de notation sera de noter les bits de contrôle en premier.
* Deux circuits seront dit équivalents s'ils effectuent la même opération.
* Un circuit sera dit optimal si il n'existe aucun circuit équivalent comportant un nombre de portes logiques strictement plus petit.